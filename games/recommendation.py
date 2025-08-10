import numpy as np
import pandas as pd
import joblib
import os
import logging
import warnings

from django.db.models import Count
from .models import Game
from .clustering import GameClusteringEngine
from .cosine_similarity import CosineSimilarityEngine

logger = logging.getLogger(__name__)

class HybridRecommendationEngine:
    """
    Hybrid Recommendation Engine yang menggunakan HANYA K-Means + Cosine Similarity
    dengan 4 atribut: genre, rating, esrb, platform
    TANPA popularity-based fallback
    """
    def __init__(self):
        self.clustering_engine = GameClusteringEngine()
        self.similarity_engine = CosineSimilarityEngine()
        self._load_models()

    def _load_models(self):
        """
        Memuat semua model yang diperlukan.
        """
        # Suppress sklearn version warnings
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
            warnings.filterwarnings("ignore", message=".*numpy._core.*")
            warnings.filterwarnings("ignore", category=FutureWarning)
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            
            # Muat model K-Means dengan prioritas loading
            try:
                # Coba muat model K3 terlebih dahulu, kemudian fallback ke model lama
                success = self.clustering_engine.load_model()  # Akan otomatis coba K3 dulu
                if success:
                    logger.info("Model K-Means berhasil dimuat.")
                else:
                    logger.warning("Gagal memuat model K-Means, akan menggunakan fallback.")
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Gagal memuat model K-Means: {error_msg}")
                
                # Berikan informasi debugging yang lebih baik
                if "239" in error_msg:
                    logger.error("Error 239: Masalah kompatibilitas sklearn - model perlu diregenerasi")
                elif "pickle" in error_msg.lower():
                    logger.error("Error pickle: File model corrupt - perlu regenerasi")

            # Muat model Cosine Similarity
            try:
                success = self.similarity_engine.load_model('cosine_similarity_model.pkl')
                if success:
                    logger.info("Model Cosine Similarity berhasil dimuat.")
                else:
                    logger.warning("Gagal memuat model Cosine Similarity, akan menggunakan fallback.")
            except Exception as e:
                logger.warning(f"Gagal memuat model Cosine Similarity: {str(e)}")

    def get_recommendations(self, game_id=None, num_recommendations=10, recommendation_type='similar'):
        """
        Mengembalikan daftar rekomendasi game berdasarkan tipe yang diminta.
        HANYA mendukung: 'similar', 'clustering', 'hybrid'
        """
        # Validasi game_id diperlukan untuk semua tipe rekomendasi
        if game_id is None:
            logger.error("game_id diperlukan untuk tipe rekomendasi ini.")
            return []
            
        try:
            anchor_game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            logger.error(f"Game dengan ID {game_id} tidak ditemukan.")
            return []

        if recommendation_type == 'clustering':
            return self._clustering_based_recommendations(anchor_game, num_recommendations)
        elif recommendation_type == 'similar':
            return self._similarity_based_recommendations(anchor_game, num_recommendations)
        elif recommendation_type == 'hybrid':
            return self._hybrid_recommendations(anchor_game, num_recommendations)
        else:
            logger.warning(f"Tipe rekomendasi '{recommendation_type}' tidak dikenali. Gunakan: 'similar', 'clustering', atau 'hybrid'")
            return []

    def _hybrid_recommendations(self, anchor_game, num_recommendations):
        """
        Rekomendasi hybrid yang menggabungkan HANYA clustering dan similarity.
        DENGAN elemen randomness untuk variasi hasil.
        TANPA popularity-based fallback.
        """
        try:
            import random
            
            # Hitung pembagian rekomendasi dengan sedikit variasi random
            base_split = num_recommendations // 2
            # Tambahkan variasi random ±2 untuk pembagian
            cluster_count = max(1, base_split + random.randint(-2, 2))
            similarity_count = max(1, num_recommendations - cluster_count)
            
            # Ambil lebih banyak rekomendasi untuk memberikan ruang randomness
            cluster_pool_size = min(cluster_count * 3, 20)  # Ambil 3x lebih banyak atau max 20
            similarity_pool_size = min(similarity_count * 3, 20)  # Ambil 3x lebih banyak atau max 20
            
            # Ambil rekomendasi dari clustering (pool lebih besar)
            cluster_pool = self._clustering_based_recommendations(anchor_game, cluster_pool_size)
            logger.info(f"Clustering pool menghasilkan {len(cluster_pool)} rekomendasi")
            
            # Ambil rekomendasi dari similarity (pool lebih besar)
            similar_pool = self._similarity_based_recommendations(anchor_game, similarity_pool_size)
            logger.info(f"Similarity pool menghasilkan {len(similar_pool)} rekomendasi")
            
            # Randomize selection dari pool
            cluster_recs = []
            if cluster_pool:
                # Shuffle dan ambil sejumlah yang dibutuhkan
                shuffled_cluster = list(cluster_pool)
                random.shuffle(shuffled_cluster)
                cluster_recs = shuffled_cluster[:cluster_count]
            
            similar_recs = []
            if similar_pool:
                # Shuffle dan ambil sejumlah yang dibutuhkan
                shuffled_similar = list(similar_pool)
                random.shuffle(shuffled_similar)
                similar_recs = shuffled_similar[:similarity_count]
            
            # Gabungkan dan hilangkan duplikat
            all_recs = []
            seen_ids = set()
            
            # Randomize urutan penambahan (kadang clustering dulu, kadang similarity dulu)
            methods = [
                ('clustering', cluster_recs),
                ('similarity', similar_recs)
            ]
            random.shuffle(methods)  # Random urutan metode
            
            for method_name, recs in methods:
                for game in recs:
                    if game.id not in seen_ids:
                        all_recs.append(game)
                        seen_ids.add(game.id)
            
            # Jika masih kurang dari target, ambil dari sisa pool
            if len(all_recs) < num_recommendations:
                remaining_needed = num_recommendations - len(all_recs)
                logger.info(f"Masih butuh {remaining_needed} rekomendasi tambahan")
                
                # Gabungkan sisa pool yang belum digunakan
                remaining_pool = []
                
                # Tambahkan sisa dari cluster pool
                for game in cluster_pool:
                    if game.id not in seen_ids:
                        remaining_pool.append(game)
                
                # Tambahkan sisa dari similar pool
                for game in similar_pool:
                    if game.id not in seen_ids:
                        remaining_pool.append(game)
                
                # Shuffle remaining pool dan ambil yang dibutuhkan
                if remaining_pool:
                    random.shuffle(remaining_pool)
                    for game in remaining_pool:
                        if len(all_recs) >= num_recommendations:
                            break
                        if game.id not in seen_ids:
                            all_recs.append(game)
                            seen_ids.add(game.id)
            
            # Final shuffle untuk variasi urutan hasil
            if len(all_recs) > 1:
                random.shuffle(all_recs)
            
            final_count = len(all_recs)
            logger.info(f"Hybrid recommendation menghasilkan {final_count} dari {num_recommendations} yang diminta")
            
            return all_recs[:num_recommendations]
            
        except Exception as e:
            logger.error(f"Error saat membuat rekomendasi hybrid: {e}")
            return []

    def _similarity_based_recommendations(self, anchor_game, num_recommendations):
        """Rekomendasi berdasarkan cosine similarity dengan 4 atribut."""
        try:
            # Gunakan cosine similarity engine
            recommended_games = self.similarity_engine.get_similar_games(
                anchor_game.id, 
                num_recommendations
            )
            
            if recommended_games:
                return recommended_games
            else:
                logger.warning("Cosine similarity tidak menghasilkan rekomendasi.")
                return []
                
        except Exception as e:
            logger.error(f"Error saat membuat rekomendasi similarity: {e}.")
            return []

    def _clustering_based_recommendations(self, anchor_game, num_recommendations):
        """Rekomendasi berdasarkan K-Means clustering dengan 4 atribut."""
        try:
            # Gunakan clustering engine
            recommended_games = self.clustering_engine.get_cluster_recommendations(
                anchor_game, 
                num_recommendations
            )
            
            if recommended_games:
                return recommended_games
            else:
                logger.warning("K-Means clustering tidak menghasilkan rekomendasi.")
                return []
                
        except Exception as e:
            logger.error(f"Error saat membuat rekomendasi clustering: {e}.")
            return []

# Fungsi lama dipertahankan untuk kompatibilitas jika masih ada yang memanggilnya
def get_similar_games(game, num_similar=10):
    """
    Fungsi kompatibilitas lama - menggunakan genre similarity sederhana
    """
    genres = game.genres.all()
    if not genres.exists():
        return Game.objects.exclude(id=game.id).order_by('-rating')[:num_similar]
    
    return Game.objects.filter(genres__in=genres) \
        .exclude(id=game.id) \
        .distinct().order_by('-rating')[:num_similar]
