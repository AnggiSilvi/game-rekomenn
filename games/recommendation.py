import numpy as np
import pandas as pd
import joblib
import os
import logging
import warnings

from django.db.models import Count
from .models import Game

logger = logging.getLogger(__name__)

class HybridRecommendationEngine:
    """
    Hybrid Recommendation Engine yang mendukung rekomendasi berbasis kemiripan (similarity),
    clustering, dan popularitas.
    """
    def __init__(self):
        self.similarity_model = None
        self.kmeans_model = None
        self.games_df = None
        self.game_objects = None
        self._load_models()

    def _load_models(self):
        """
        Memuat semua model dan data yang diperlukan dari file.
        """
        # Muat data game dan cluster
        cluster_data_path = 'df_clustering.csv'
        if os.path.exists(cluster_data_path):
            try:
                self.games_df = pd.read_csv(cluster_data_path)
                logger.info("File df_clustering.csv berhasil dimuat.")
            except Exception as e:
                logger.error(f"Gagal memuat df_clustering.csv: {str(e)}")
                self.games_df = None
        else:
            logger.warning("File df_clustering.csv tidak ditemukan.")
            self.games_df = None

        # Muat model K-Means
        kmeans_path = 'model_kmeans.pkl'
        if os.path.exists(kmeans_path):
            try:
                # Suppress sklearn version warnings for model loading
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
                    self.kmeans_model = joblib.load(kmeans_path)
                logger.info("Model model_kmeans.pkl berhasil dimuat.")
            except Exception as e:
                logger.error(f"Gagal memuat model_kmeans.pkl: {str(e)}")
                self.kmeans_model = None
        else:
            logger.warning("File model_kmeans.pkl tidak ditemukan.")
            self.kmeans_model = None

        # Muat model similarity
        similarity_path = 'rekomendasi_sistem.pkl'
        if os.path.exists(similarity_path):
            try:
                # Suppress sklearn version warnings for model loading
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
                    self.similarity_model = joblib.load(similarity_path)
                # Asumsikan urutan dalam model similarity sama dengan di database
                self.game_objects = list(Game.objects.all().order_by('id'))
                logger.info("Model rekomendasi_sistem.pkl berhasil dimuat.")
            except Exception as e:
                logger.error(f"Gagal memuat rekomendasi_sistem.pkl: {str(e)}")
                self.similarity_model = None
        else:
            logger.warning("File rekomendasi_sistem.pkl tidak ditemukan.")
            self.similarity_model = None

    def get_recommendations(self, game_id, num_recommendations=10, recommendation_type='similar'):
        """
        Mengembalikan daftar rekomendasi game berdasarkan tipe yang diminta.
        """
        try:
            anchor_game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            logger.error(f"Game dengan ID {game_id} tidak ditemukan.")
            return self._popularity_based_recommendations(num_recommendations)

        if recommendation_type == 'clustering':
            return self._clustering_based_recommendations(anchor_game, num_recommendations)
        elif recommendation_type == 'similar':
            return self._similarity_based_recommendations(anchor_game, num_recommendations)
        else: # Fallback ke popularitas jika tipe tidak dikenali
            return self._popularity_based_recommendations(num_recommendations)

    def _similarity_based_recommendations(self, anchor_game, num_recommendations):
        """Rekomendasi berdasarkan kemiripan konten (content-based)."""
        if self.similarity_model is None or self.game_objects is None:
            logger.warning("Similarity model tidak tersedia, fallback ke popularitas.")
            return self._popularity_based_recommendations(num_recommendations)

        try:
            # Model kemiripan diindeks oleh ID game secara langsung.
            # Dapatkan skor untuk game jangkar.
            similarity_scores = self.similarity_model[anchor_game.id]

            # Urutkan game berdasarkan skor kemiripan
            # Asumsikan similarity_scores adalah dict atau Series: {game_id: score}
            sorted_similar_games = sorted(similarity_scores.items(), key=lambda item: item[1], reverse=True)

            # Ambil ID game yang direkomendasikan, kecuali game itu sendiri
            recommended_ids = [
                game_id for game_id, score in sorted_similar_games
                if game_id != anchor_game.id
            ][:num_recommendations]

            # Ambil objek Game dari database
            recommended_games = Game.objects.filter(id__in=recommended_ids)
            
            # Pertahankan urutan dari model
            recommended_games_sorted = sorted(recommended_games, key=lambda game: recommended_ids.index(game.id))
            
            return recommended_games_sorted
        except (KeyError, AttributeError) as e:
            logger.error(f"Error saat mencari game di similarity model: {e}. Fallback ke popularitas.")
            return self._popularity_based_recommendations(num_recommendations)

    def _clustering_based_recommendations(self, anchor_game, num_recommendations):
        """Rekomendasi berdasarkan cluster yang sama."""
        if self.games_df is None:
            logger.warning("Dataframe clustering tidak tersedia, fallback ke popularitas.")
            return self._popularity_based_recommendations(num_recommendations)

        try:
            # Menggunakan 'name' (huruf kecil) sesuai kemungkinan nama kolom di CSV
            game_row = self.games_df[self.games_df['name'] == anchor_game.name]
            if game_row.empty:
                logger.warning(f"Game '{anchor_game.name}' tidak ditemukan di df_clustering. Fallback ke popularitas.")
                return self._popularity_based_recommendations(num_recommendations)

            cluster_id = game_row['Cluster'].values[0]
            
            # Ambil semua game di cluster yang sama, kecuali game itu sendiri
            same_cluster_df = self.games_df[
                (self.games_df['Cluster'] == cluster_id) &
                (self.games_df['name'] != anchor_game.name)
            ]
            
            # Ambil nama-nama game dan query ke database
            recommended_game_names = same_cluster_df['name'].head(num_recommendations).tolist()
            recommended_games = Game.objects.filter(name__in=recommended_game_names)
            
            return list(recommended_games)
        except Exception as e:
            logger.error(f"Error saat membuat rekomendasi cluster: {e}. Fallback ke popularitas.")
            return self._popularity_based_recommendations(num_recommendations)

    def _popularity_based_recommendations(self, num_recommendations=10):
        """Fallback rekomendasi berdasarkan skor popularitas yang sudah dihitung."""
        return list(Game.objects.filter(
            popularity_score__isnull=False
        ).order_by('-popularity_score', '-rating')[:num_recommendations])

# Fungsi lama dipertahankan untuk kompatibilitas jika masih ada yang memanggilnya
def get_similar_games(game, num_similar=10):
    genres = game.genres.all()
    if not genres.exists():
        return Game.objects.exclude(id=game.id).order_by('-rating')[:num_similar]
    
    return Game.objects.filter(genres__in=genres) \
        .exclude(id=game.id) \
        .distinct().order_by('-rating')[:num_similar]
