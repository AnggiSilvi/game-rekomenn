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

from .models import Game, Genre, Platform, Publisher, Tag
from .recommendation import HybridRecommendationEngine, get_similar_games
from .utils import get_game_screenshots, get_fallback_screenshots

logger = logging.getLogger(__name__)

@login_required
def home_page(request):
    today = timezone.now().date()
    rec_engine = HybridRecommendationEngine()

    # Popular Games: berdasarkan rating tertinggi
    popular_games = Game.objects.order_by('-rating')[:8]
    
    # Upcoming Games: game yang akan rilis
    upcoming_games = Game.objects.filter(released__gt=today).order_by('released')[:8]
    
    # New Games: game yang baru rilis
    new_games = Game.objects.filter(released__lte=today).order_by('-released')[:8]

    # Recommended Games: untuk user yang login, berikan rekomendasi yang berbeda
    recommended_games = []
    
    if request.user.is_authenticated:
        # Coba ambil game dengan rating menengah tapi dengan variasi genre
        # untuk memberikan rekomendasi yang lebih beragam
        try:
            # Ambil game dengan rating 3.5-4.5 (good but not top-rated)
            # dan urutkan berdasarkan popularitas untuk variasi
            recommended_games = Game.objects.filter(
                rating__gte=3.5, 
                rating__lt=4.5,
                popularity_score__isnull=False
            ).order_by('-popularity_score')[:8]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            # Fallback ke rekomendasi sederhana
            recommended_games = Game.objects.exclude(
                id__in=[g.id for g in popular_games]
            ).order_by('-rating')[:8]

    query = request.GET.get('q')
    search_type = request.GET.get('search_type', 'games')
    search_results = None
    genre_results = None

    if query:
        if search_type == 'games':
            # Pencarian hanya untuk games
            search_results = Game.objects.filter(name__icontains=query).order_by('-rating')
        elif search_type == 'genres':
            # Pencarian hanya untuk genres
            genre_results = Genre.objects.filter(name__icontains=query)

    context = {
        'popular_games': popular_games,
        'upcoming_games': upcoming_games,
        'new_games': new_games,
        'recommended_games': recommended_games,
        'search_results': search_results,
        'genre_results': genre_results,
        'query': query,
        'search_type': search_type,
    }
    return render(request, 'games/home.html', context)

@login_required
def genre_list(request):
    genres = Genre.objects.all()
    genre_data = []
    for genre in genres:
        example_games = genre.game_set.all()[:3]
        genre_data.append({'genre': genre, 'example_games': example_games})
    return render(request, 'games/genre_list.html', {'genre_data': genre_data})

@login_required
def publisher_list(request):
    publishers = Publisher.objects.all()
    publisher_data = []
    for publisher in publishers:
        example_games = publisher.game_set.all()[:3]
        publisher_data.append({'publisher': publisher, 'example_games': example_games})
    return render(request, 'games/publisher_list.html', {'publisher_data': publisher_data})

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
    games = Game.objects.filter(genres=genre).order_by('-rating')
    return render(request, 'games/games_by_category.html', {
        'category_type': 'Genre',
        'category_name': genre.name,
        'games': games
    })

@login_required
def games_by_publisher(request, publisher_name):
    publisher = get_object_or_404(Publisher, name=publisher_name)
    games = Game.objects.filter(publishers=publisher).order_by('-rating')
    return render(request, 'games/games_by_category.html', {
        'category_type': 'Publisher',
        'category_name': publisher.name,
        'games': games
    })

@login_required
def games_by_esrb(request, esrb_slug):
    esrb_map = {
        'everyone': 'Everyone',
        'everyone-10-plus': 'Everyone 10+',
        'teen': 'Teen',
        'mature': 'Mature',
        'adults-only': 'Adults Only'
    }
    esrb_rating = esrb_map.get(esrb_slug)
    if not esrb_rating:
        raise Http404("ESRB rating not found")

    games = Game.objects.filter(esrb=esrb_rating).order_by('-rating')
    return render(request, 'games/games_by_category.html', {
        'category_type': 'ESRB',
        'category_name': esrb_rating,
        'games': games
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
    
    # Inisialisasi engine dan dapatkan rekomendasi hybrid
    rec_engine = HybridRecommendationEngine()
    
    # Dapatkan rekomendasi dari kedua metode
    similar_games = rec_engine.get_recommendations(game_id=game.id, num_recommendations=10, recommendation_type='similar')
    cluster_games = rec_engine.get_recommendations(game_id=game.id, num_recommendations=10, recommendation_type='clustering')
    
    # Gabungkan dan deduplikasi rekomendasi
    hybrid_games = []
    seen_ids = set()
    
    # Tambahkan dari similarity-based (prioritas pertama)
    for game_obj in similar_games:
        if game_obj.id not in seen_ids and game_obj.id != game.id:
            hybrid_games.append(game_obj)
            seen_ids.add(game_obj.id)
    
    # Tambahkan dari clustering-based (prioritas kedua)
    for game_obj in cluster_games:
        if game_obj.id not in seen_ids and game_obj.id != game.id:
            hybrid_games.append(game_obj)
            seen_ids.add(game_obj.id)
            if len(hybrid_games) >= 10:
                break
    
    # Jika masih kurang dari 10, tambahkan dari popularity-based dengan variasi
    if len(hybrid_games) < 10:
        # Coba ambil game dari genre yang sama terlebih dahulu
        if game.genres.exists():
            genre_games = Game.objects.filter(
                genres__in=game.genres.all()
            ).exclude(id=game.id).exclude(id__in=seen_ids).order_by('-rating')[:15]
            
            for game_obj in genre_games:
                if game_obj.id not in seen_ids:
                    hybrid_games.append(game_obj)
                    seen_ids.add(game_obj.id)
                    if len(hybrid_games) >= 10:
                        break
        
        # Jika masih kurang, tambahkan dari popularity-based
        if len(hybrid_games) < 10:
            popular_games = rec_engine.get_recommendations(game_id=game.id, num_recommendations=20, recommendation_type='popularity')
            for game_obj in popular_games:
                if game_obj.id not in seen_ids and game_obj.id != game.id:
                    hybrid_games.append(game_obj)
                    seen_ids.add(game_obj.id)
                    if len(hybrid_games) >= 10:
                        break

    # Dapatkan screenshot gameplay dari API
    gameplay_screenshots = get_game_screenshots(game.name)
    
    # Jika tidak ada screenshot dari API, gunakan fallback
    if not gameplay_screenshots:
        gameplay_screenshots = get_fallback_screenshots(game.name)

    context = {
        'game': game,
        'hybrid_games': hybrid_games,
        'gameplay_screenshots': gameplay_screenshots,
    }
    return render(request, 'games/game_detail.html', context)

def get_recommendations_api(request):
    try:
        rec_type = request.GET.get('type', 'hybrid')
        num_recs = int(request.GET.get('num', 10))
        game_id = request.GET.get('game_id', 1) # Default ke 1 jika tidak ada, popularitas tidak butuh id

        rec_engine = HybridRecommendationEngine()
        recommendations = rec_engine.get_recommendations(game_id=game_id, num_recommendations=num_recs, recommendation_type=rec_type)

        recs_data = [{
            'id': game.id,
            'name': game.name,
            'rating': game.rating,
            'cover_image_url': game.cover_image_url,
            'released': game.released.isoformat() if game.released else None,
        } for game in recommendations]

        return JsonResponse({'recommendations': recs_data, 'type': rec_type, 'count': len(recs_data)})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def search_suggestions(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('search_type', 'games')
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    suggestions = {'games': [], 'genres': []}

    if search_type == 'games':
        # Only return game suggestions
        games = Game.objects.filter(name__icontains=query).values('id', 'name', 'cover_image_url')[:10]
        suggestions['games'] = list(games)
    elif search_type == 'genres':
        # Only return genre suggestions
        genres = Genre.objects.filter(name__icontains=query).values('name')[:10]
        suggestions['genres'] = [g['name'] for g in genres]

    return JsonResponse({
        'suggestions': suggestions,
        'search_type': search_type
    })

def similarity_matrix_info(request):
    model_path = 'rekomendasi_sistem.pkl'
    if os.path.exists(model_path):
        try:
            similarity_matrix = joblib.load(model_path)
            return JsonResponse({
                'status': 'success',
                'shape': similarity_matrix.shape,
                'message': 'Recommendation model (rekomendasi_sistem.pkl) loaded successfully'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error loading recommendation model: {str(e)}'})
    else:
        return JsonResponse({'status': 'error', 'message': 'rekomendasi_sistem.pkl not found'})

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
    recent_recommendations = rec_engine.get_recommendations(
        game_id=1, 
        num_recommendations=12, 
        recommendation_type='popularity'
    )
    
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
