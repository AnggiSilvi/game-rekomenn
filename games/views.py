from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.db.models import Q
from django.utils.text import slugify
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
import os
import joblib
import logging

from .models import Game, Genre, Platform
from .recommendation import HybridRecommendationEngine, get_similar_games
from .utils import get_game_screenshots, get_fallback_screenshots
import logging

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

@login_required
def home_page(request):
    today = timezone.now().date()
    rec_engine = HybridRecommendationEngine()

    # Popular Games: berdasarkan rating tertinggi dengan deduplication
    popular_games_query = Game.objects.order_by('-rating')[:12]  # Ambil lebih banyak untuk antisipasi duplikat
    popular_games = []
    popular_seen_ids = set()
    
    for game in popular_games_query:
        if game.id not in popular_seen_ids and len(popular_games) < 8:
            popular_games.append(game)
            popular_seen_ids.add(game.id)

    # Recommended Games: menggunakan HYBRID recommendation system dengan deduplication ketat
    recommended_games = []
    
    if request.user.is_authenticated:
        try:
            # Ambil sample game untuk dijadikan anchor (game dengan rating tinggi)
            sample_games = Game.objects.filter(rating__gte=4.0).order_by('?')[:3]
            
            hybrid_recommendations = []
            seen_ids = set()
            # Tambahkan popular games ke seen_ids untuk menghindari duplikasi dengan rekomendasi
            seen_ids.update(popular_seen_ids)
            
            for sample_game in sample_games:
                # Gunakan metode hybrid langsung untuk mendapatkan 8 rekomendasi
                hybrid_games = rec_engine.get_recommendations(
                    game_id=sample_game.id, 
                    num_recommendations=8, 
                    recommendation_type='hybrid'
                )
                
                # Tambahkan hasil hybrid dengan deduplication ketat
                for game in hybrid_games:
                    if (game.id not in seen_ids and 
                        len(hybrid_recommendations) < 8 and
                        game.id not in popular_seen_ids):  # Pastikan tidak duplikat dengan popular games
                        hybrid_recommendations.append(game)
                        seen_ids.add(game.id)
                
                # Jika sudah dapat 8 game, break
                if len(hybrid_recommendations) >= 8:
                    break
            
            # Jika masih kurang dari 8, coba ambil lebih banyak dari sample game pertama
            if len(hybrid_recommendations) < 8 and sample_games:
                additional_hybrid = rec_engine.get_recommendations(
                    game_id=sample_games[0].id, 
                    num_recommendations=16,  # Ambil lebih banyak untuk antisipasi duplikat
                    recommendation_type='hybrid'
                )
                
                for game in additional_hybrid:
                    if (game.id not in seen_ids and 
                        len(hybrid_recommendations) < 8 and
                        game.id not in popular_seen_ids):
                        hybrid_recommendations.append(game)
                        seen_ids.add(game.id)
            
            # Pastikan tepat 8 game
            recommended_games = hybrid_recommendations[:8]
            
        except Exception as e:
            logger.error(f"Error generating hybrid recommendations: {e}")
            # Jika error, tidak ada fallback - biarkan kosong
            recommended_games = []

    # Universal search functionality - mencari di semua kategori sekaligus
    query = request.GET.get('q')
    search_results = None
    genre_results = None
    platform_results = None
    esrb_results = None
    rating_results = None
    is_rating_search = False
    rating_search_info = None

    if query:
        query_lower = query.lower()
        
        # Cek apakah ini pencarian rating terlebih dahulu
        if 'rating' in query_lower:
            import re
            rating_match = re.search(r'rating\s*([1-5])', query_lower)
            if rating_match:
                is_rating_search = True
                rating_num = int(rating_match.group(1))
                
                # Tentukan range rating dan ambil games
                if rating_num == 5:
                    rating_games = Game.objects.filter(rating__gte=4.5).exclude(rating__isnull=True).order_by('-rating')
                    range_name = 'Rating 5 (4.5-5.0)'
                elif rating_num == 4:
                    rating_games = Game.objects.filter(rating__gte=3.5, rating__lt=4.5).exclude(rating__isnull=True).order_by('-rating')
                    range_name = 'Rating 4 (3.5-4.4)'
                elif rating_num == 3:
                    rating_games = Game.objects.filter(rating__gte=2.5, rating__lt=3.5).exclude(rating__isnull=True).order_by('-rating')
                    range_name = 'Rating 3 (2.5-3.4)'
                elif rating_num == 2:
                    rating_games = Game.objects.filter(rating__gte=1.5, rating__lt=2.5).exclude(rating__isnull=True).order_by('-rating')
                    range_name = 'Rating 2 (1.5-2.4)'
                elif rating_num == 1:
                    rating_games = Game.objects.filter(rating__lt=1.5).exclude(rating__isnull=True).order_by('-rating')
                    range_name = 'Rating 1 (0-1.4)'
                
                if rating_games.exists():
                    # Untuk pencarian rating, gunakan hasil rating sebagai search_results utama
                    search_results = rating_games
                    rating_search_info = {
                        'range_name': range_name,
                        'rating_num': rating_num,
                        'count': rating_games.count()
                    }
                    
                    # Tetap buat rating_results untuk kompatibilitas template
                    rating_results = [{
                        'range_name': range_name,
                        'games': rating_games,
                        'count': rating_games.count()
                    }]
        
        # Jika bukan pencarian rating, lakukan pencarian universal biasa
        if not is_rating_search:
            search_results = Game.objects.filter(
                Q(name__icontains=query) |
                Q(genres__name__icontains=query) |
                Q(platforms__name__icontains=query) |
                Q(esrb__icontains=query)
            ).distinct().order_by('-rating')
        
        # Ambil hasil kategori untuk ditampilkan terpisah (kecuali untuk pencarian rating)
        if not is_rating_search:
            genre_results = Genre.objects.filter(name__icontains=query)
            platform_results = Platform.objects.filter(name__icontains=query)
            
            # ESRB results - filter yang valid saja
            esrb_matches = Game.objects.exclude(
                esrb__isnull=True
            ).exclude(
                esrb=''
            ).exclude(
                esrb='N/A'
            ).exclude(
                esrb='Rating Pending'
            ).filter(
                esrb__icontains=query
            ).values_list('esrb', flat=True).distinct()
            
            esrb_results = list(esrb_matches)

    context = {
        'popular_games': popular_games,
        'recommended_games': recommended_games,
        'search_results': search_results,
        'genre_results': genre_results,
        'platform_results': platform_results,
        'esrb_results': esrb_results,
        'rating_results': rating_results,
        'query': query,
        'is_rating_search': is_rating_search,
        'rating_search_info': rating_search_info,
    }
    return render(request, 'games/home.html', context)

@login_required
def genre_list(request):
    genres = Genre.objects.all()
    genre_data = []
    used_images = set()  # Track gambar yang sudah digunakan
    
    for genre in genres:
        # Ambil game dengan gambar cover yang bagus dan rating tinggi
        games_with_images = genre.game_set.exclude(
            cover_image_url__isnull=True
        ).exclude(
            cover_image_url=''
        ).exclude(
            cover_image_url='https://via.placeholder.com/250x350.png?text=No+Image'
        ).exclude(
            cover_image_url__icontains='placeholder'
        ).filter(
            rating__isnull=False
        ).order_by('-rating', '-popularity_score')
        
        representative_game = None
        
        # Cari game dengan gambar yang belum digunakan
        for game in games_with_images:
            # Normalize URL untuk perbandingan yang lebih akurat
            clean_url = game.cover_image_url.split('?')[0] if game.cover_image_url else ''
            if clean_url and clean_url not in used_images:
                representative_game = game
                used_images.add(clean_url)
                break
        
        # Jika tidak ada game dengan gambar unik, buat placeholder unik untuk genre ini
        if not representative_game:
            # Buat warna unik berdasarkan nama genre
            colors = [
                ('4a90e2', 'ffffff'),  # Blue
                ('7b68ee', 'ffffff'),  # Purple  
                ('32cd32', 'ffffff'),  # Green
                ('ff6347', 'ffffff'),  # Red
                ('ffa500', 'ffffff'),  # Orange
                ('20b2aa', 'ffffff'),  # Teal
                ('dc143c', 'ffffff'),  # Crimson
                ('9370db', 'ffffff'),  # Medium Purple
                ('3cb371', 'ffffff'),  # Sea Green
                ('cd853f', 'ffffff'),  # Peru
                ('ff69b4', 'ffffff'),  # Hot Pink
                ('00ced1', 'ffffff'),  # Dark Turquoise
                ('ffd700', '000000'),  # Gold
                ('8a2be2', 'ffffff'),  # Blue Violet
                ('ff1493', 'ffffff'),  # Deep Pink
            ]
            
            # Pilih warna berdasarkan hash nama genre untuk konsistensi
            color_index = hash(genre.name) % len(colors)
            color_bg, color_text = colors[color_index]
            
            # Buat game dummy dengan placeholder unik
            class DummyGame:
                def __init__(self, genre_name, color_bg, color_text):
                    self.name = genre_name
                    self.cover_image_url = f'https://via.placeholder.com/300x200/{color_bg}/{color_text}?text={genre_name.replace(" ", "+")}'
                    self.rating = 0
            
            representative_game = DummyGame(genre.name, color_bg, color_text)
            used_images.add(representative_game.cover_image_url.split('?')[0])
        
        # Ambil contoh games untuk display
        example_games = games_with_images[:3] if games_with_images else []
        
        genre_data.append({
            'genre': genre, 
            'example_games': example_games,
            'representative_game': representative_game
        })
    
    return render(request, 'games/genre_list.html', {'genre_data': genre_data})

@login_required
def publisher_list(request):
    # Publisher functionality not available in current model
    return render(request, 'games/publisher_list.html', {'publisher_data': []})

@login_required
def esrb_list(request):
    esrb_ratings = Game.objects.exclude(esrb__isnull=True).exclude(esrb='').exclude(esrb='N/A').exclude(esrb='Rating Pending').values_list('esrb', flat=True).distinct()
    esrb_data = []
    for esrb_rating in esrb_ratings:
        example_games = Game.objects.filter(esrb=esrb_rating)[:3]
        if example_games.exists():
            esrb_data.append({'esrb_rating': esrb_rating, 'example_games': example_games})
    return render(request, 'games/esrb_list.html', {'esrb_data': esrb_data})

@login_required
def platform_list(request):
    platforms = Platform.objects.all()
    platform_data = []
    for platform in platforms:
        example_games = platform.game_set.all()[:3]
        platform_data.append({'platform': platform, 'example_games': example_games})
    return render(request, 'games/platform_list.html', {'platform_data': platform_data})

@login_required
def rating_list(request):
    rating_groups = {
        '5-stars': {'name': '5 Stars', 'games': Game.objects.filter(rating__gte=4.5)},
        '4-stars': {'name': '4 Stars', 'games': Game.objects.filter(rating__gte=3.5, rating__lt=4.5)},
        '3-stars': {'name': '3 Stars', 'games': Game.objects.filter(rating__gte=2.5, rating__lt=3.5)},
        '2-stars': {'name': '2 Stars', 'games': Game.objects.filter(rating__gte=1.5, rating__lt=2.5)},
        '1-star': {'name': '1 Star', 'games': Game.objects.filter(rating__lt=1.5)},
    }
    rating_data = {}
    for slug, data in rating_groups.items():
        rating_data[slug] = {
            'name': data['name'],
            'games': data['games'][:3],
            'total': data['games'].count()
        }
    return render(request, 'games/rating_list.html', {'rating_data': rating_data})

@login_required
def games_by_genre(request, genre_name):
    genre = get_object_or_404(Genre, name=genre_name)
    
    # Tambahkan distinct() dan manual deduplication untuk genre
    games_query = Game.objects.filter(genres=genre).distinct().order_by('-rating', 'id')
    
    # Manual deduplication berdasarkan ID
    seen_ids = set()
    unique_games = []
    
    for game in games_query:
        if game.id not in seen_ids:
            unique_games.append(game)
            seen_ids.add(game.id)
    
    return render(request, 'games/games_by_category.html', {
        'category_type': 'Genre',
        'category_name': genre.name,
        'games': unique_games
    })

@login_required
def games_by_publisher(request, publisher_name):
    # Publisher functionality not available in current model
    raise Http404("Publisher functionality not available")

@login_required
def games_by_esrb(request, esrb_slug):
    esrb_map = {
        'everyone': 'Everyone',
        'everyone-10': 'Everyone 10+',  # Fixed: slugify converts "Everyone 10+" to "everyone-10"
        'everyone-10-plus': 'Everyone 10+',  # Keep this for backward compatibility
        'teen': 'Teen',
        'mature': 'Mature',
        'adults-only': 'Adults Only'
    }
    esrb_rating = esrb_map.get(esrb_slug)
    if not esrb_rating:
        raise Http404("ESRB rating not found")

    # Enhanced deduplication: by ID, name, and normalized name
    games_query = Game.objects.filter(esrb=esrb_rating).distinct().order_by('-rating', 'id')
    
    # Triple-layer deduplication to prevent any duplicates
    seen_ids = set()
    seen_names = set()
    seen_normalized_names = set()
    unique_games = []
    
    def normalize_name_for_dedup(name):
        """Normalize name for deduplication"""
        if not name:
            return ""
        import re
        import unicodedata
        
        # Apply same normalization as our fix command
        normalized = name
        normalized = normalized.replace('\u2019', "'")  # Right single quotation mark
        normalized = re.sub(r'[''`´'']', "'", normalized)  # Various apostrophes
        normalized = normalized.replace('\u2013', '-')  # En dash
        normalized = normalized.replace('\u2014', '-')  # Em dash  
        normalized = normalized.replace('\u2212', '-')  # Minus sign
        normalized = re.sub(r'[–—−‒]', '-', normalized)  # Various dashes
        normalized = unicodedata.normalize('NFKD', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized.lower()
    
    for game in games_query:
        normalized_name = normalize_name_for_dedup(game.name)
        
        # Check for duplicates by ID, exact name, or normalized name
        if (game.id not in seen_ids and 
            game.name not in seen_names and 
            normalized_name not in seen_normalized_names):
            
            unique_games.append(game)
            seen_ids.add(game.id)
            seen_names.add(game.name)
            seen_normalized_names.add(normalized_name)
    
    return render(request, 'games/games_by_category.html', {
        'category_type': 'ESRB',
        'category_name': esrb_rating,
        'games': unique_games
    })

@login_required
def games_by_rating(request, rating_range):
    rating_ranges = {
        '5-stars': {'name': '5 Stars', 'min': 4.5, 'max': 5.0},
        '4-stars': {'name': '4 Stars', 'min': 3.5, 'max': 4.5},
        '3-stars': {'name': '3 Stars', 'min': 2.5, 'max': 3.5},
        '2-stars': {'name': '2 Stars', 'min': 1.5, 'max': 2.5},
        '1-star': {'name': '1 Star', 'min': 0, 'max': 1.5},
    }
    range_info = rating_ranges.get(rating_range)
    if not range_info:
        raise Http404("Rating range not found")

    games = Game.objects.filter(rating__gte=range_info['min'], rating__lt=range_info['max']).order_by('-rating')
    return render(request, 'games/games_by_category.html', {
        'category_type': 'Rating',
        'category_name': range_info['name'],
        'games': games
    })

@login_required
def games_by_platform(request, platform_slug):
    platforms = Platform.objects.all()
    platform = None
    for p in platforms:
        if slugify(p.name) == platform_slug:
            platform = p
            break
    if not platform:
        raise Http404("Platform not found")
    games = Game.objects.filter(platforms=platform).order_by('-rating')
    return render(request, 'games/games_by_category.html', {
        'category_type': 'Platform',
        'category_name': platform.name,
        'games': games
    })

@login_required
def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # Inisialisasi engine dan dapatkan rekomendasi hybrid langsung
    rec_engine = HybridRecommendationEngine()
    
    # Gunakan metode hybrid langsung untuk mendapatkan 10 rekomendasi
    hybrid_games = rec_engine.get_recommendations(
        game_id=game.id, 
        num_recommendations=15,  # Ambil lebih banyak untuk antisipasi duplikat
        recommendation_type='hybrid'
    )
    
    # Filter untuk memastikan tidak ada game yang sama dengan game saat ini
    filtered_hybrid_games = []
    for game_obj in hybrid_games:
        if game_obj.id != game.id:
            filtered_hybrid_games.append(game_obj)
    
    # Jika masih kurang dari 10 setelah filtering, ambil lebih banyak
    if len(filtered_hybrid_games) < 10:
        additional_hybrid = rec_engine.get_recommendations(
            game_id=game.id, 
            num_recommendations=20,  # Ambil lebih banyak untuk antisipasi duplikat
            recommendation_type='hybrid'
        )
        
        seen_ids = {g.id for g in filtered_hybrid_games}
        seen_ids.add(game.id)  # Tambahkan game saat ini ke seen_ids
        
        for game_obj in additional_hybrid:
            if len(filtered_hybrid_games) >= 10:
                break
            if game_obj.id not in seen_ids:
                filtered_hybrid_games.append(game_obj)
                seen_ids.add(game_obj.id)
    
    # Pastikan maksimal 10 game
    final_hybrid_games = filtered_hybrid_games[:10]

    # Dapatkan screenshot gameplay dari API
    gameplay_screenshots = get_game_screenshots(game.name)
    
    # Jika tidak ada screenshot dari API, gunakan fallback
    if not gameplay_screenshots:
        gameplay_screenshots = get_fallback_screenshots(game.name)

    context = {
        'game': game,
        'hybrid_games': final_hybrid_games,
        'gameplay_screenshots': gameplay_screenshots,
    }
    return render(request, 'games/game_detail.html', context)

def get_recommendations_api(request):
    try:
        rec_type = request.GET.get('type', 'hybrid')
        num_recs = int(request.GET.get('num', 10))
        game_id = request.GET.get('game_id')
        input_game_name = request.GET.get('input_game_name')

        rec_engine = HybridRecommendationEngine()

        if rec_type == 'csv':
            if not input_game_name:
                logger.error("input_game_name parameter is required for CSV recommendations")
                return JsonResponse({'recommendations': [], 'type': rec_type, 'count': 0})

            recommended_names = rec_engine.get_recommendations(
                recommendation_type='csv',
                input_game_name=input_game_name,
                num_recommendations=num_recs
            )
            # Query Game objects by name
            recommended_games = list(Game.objects.filter(name__in=recommended_names))
            # Sort recommended_games to match order in recommended_names
            recommended_games_sorted = []
            for name in recommended_names:
                for game in recommended_games:
                    if game.name == name:
                        recommended_games_sorted.append(game)
                        break
            recs_data = [{
                'id': game.id,
                'name': game.name,
                'rating': game.rating,
                'cover_image_url': game.cover_image_url,
                'genres': [genre.name for genre in game.genres.all()],
                'platforms': game.platforms,
                'esrb': game.esrb,
            } for game in recommended_games_sorted]

            return JsonResponse({'recommendations': recs_data, 'type': rec_type, 'count': len(recs_data)})

        if game_id is not None:
            game_id = int(game_id)
        else:
            game_id = None

        recommendations = rec_engine.get_recommendations(game_id=game_id, num_recommendations=num_recs, recommendation_type=rec_type)

        recs_data = [{
            'id': game.id,
            'name': game.name,
            'rating': game.rating,
            'cover_image_url': game.cover_image_url,
            'genres': [genre.name for genre in game.genres.all()],
            'platforms': game.platforms,
            'esrb': game.esrb,
        } for game in recommendations]

        return JsonResponse({'recommendations': recs_data, 'type': rec_type, 'count': len(recs_data)})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def search_suggestions(request):
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    # Universal search suggestions - cari di semua kategori
    suggestions = {
        'games': [],
        'genres': [],
        'platforms': [],
        'esrb': [],
        'ratings': []
    }

    # Game suggestions
    games = Game.objects.filter(name__icontains=query).values('id', 'name', 'cover_image_url')[:5]
    suggestions['games'] = list(games)
    
    # Genre suggestions
    genres = Genre.objects.filter(name__icontains=query).values('name')[:3]
    suggestions['genres'] = [g['name'] for g in genres]
    
    # Platform suggestions
    platforms = Platform.objects.filter(name__icontains=query).values('name')[:3]
    suggestions['platforms'] = [p['name'] for p in platforms]
    
    # ESRB suggestions
    esrb_matches = Game.objects.exclude(
        esrb__isnull=True
    ).exclude(
        esrb=''
    ).exclude(
        esrb='N/A'
    ).exclude(
        esrb='Rating Pending'
    ).filter(
        esrb__icontains=query
    ).values_list('esrb', flat=True).distinct()[:3]
    
    suggestions['esrb'] = list(esrb_matches)
    
    # Rating suggestions - keyword 'rating 1' sampai 'rating 5'
    rating_suggestions = []
    query_lower = query.lower()
    
    # Cek apakah query mengandung 'rating' diikuti angka 1-5
    if 'rating' in query_lower:
        import re
        rating_match = re.search(r'rating\s*([1-5])', query_lower)
        if rating_match:
            rating_num = int(rating_match.group(1))
            rating_suggestions.append(f'Rating {rating_num}')
    elif query.replace('.', '').isdigit():
        # Jika hanya angka, suggest format 'rating X'
        try:
            rating_num = float(query)
            if 1 <= rating_num <= 5:
                rating_suggestions.append(f'Rating {int(rating_num)}')
        except ValueError:
            pass
        
    suggestions['ratings'] = rating_suggestions[:2]

    return JsonResponse({
        'suggestions': suggestions
    })

def similarity_matrix_info(request):
    model_path = 'cosine_similarity_model.pkl'
    if os.path.exists(model_path):
        try:
            model_data = joblib.load(model_path)
            if isinstance(model_data, dict) and 'similarity_matrix' in model_data:
                similarity_matrix = model_data['similarity_matrix']
                return JsonResponse({
                    'status': 'success',
                    'shape': similarity_matrix.shape,
                    'message': 'Cosine similarity model loaded successfully (new format)'
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid model format'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error loading similarity model: {str(e)}'})
    else:
        return JsonResponse({'status': 'error', 'message': 'cosine_similarity_model.pkl not found'})

# Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('games:home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'games:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Username atau password salah.')
    
    return render(request, 'games/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('games:home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Akun berhasil dibuat untuk {username}!')
            return redirect('games:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'games/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Anda telah berhasil logout.')
    return redirect('games:login')

@login_required
def dashboard_view(request):
    from django.db.models import Count, Avg
    
    # Get basic statistics
    total_games = Game.objects.count()
    total_genres = Genre.objects.count()
    total_platforms = Platform.objects.count()
    avg_rating = Game.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # User-specific statistics (placeholder for now)
    user_stats = {
        'total_ratings': 0,
        'avg_rating': 0,
        'total_interactions': 0,
        'favorite_genres': []
    }
    
    # Get recent recommendations using the recommendation engine
    rec_engine = HybridRecommendationEngine()
    
    # Ambil sample game untuk dijadikan anchor untuk dashboard
    try:
        sample_game = Game.objects.filter(rating__gte=4.0).first()
        if sample_game:
            recent_recommendations = rec_engine.get_recommendations(
                game_id=sample_game.id, 
                num_recommendations=12, 
                recommendation_type='hybrid'
            )
        else:
            # Fallback jika tidak ada game dengan rating tinggi
            recent_recommendations = list(Game.objects.order_by('-rating')[:12])
    except Exception as e:
        logger.error(f"Error getting dashboard recommendations: {e}")
        recent_recommendations = list(Game.objects.order_by('-rating')[:12])
    
    context = {
        'total_games': total_games,
        'total_genres': total_genres,
        'total_platforms': total_platforms,
        'avg_rating': avg_rating,
        'stats': user_stats,
        'recent_recommendations': recent_recommendations,
        'recent_ratings': [],  # Placeholder for user ratings
        'favorite_platforms': [],  # Placeholder for user platforms
    }
    
    return render(request, 'games/dashboard.html', context)
