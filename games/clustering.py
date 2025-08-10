"""
Game Clustering Engine menggunakan K-Means
Modul ini menyediakan fungsionalitas untuk mengelompokkan game berdasarkan fitur-fitur tertentu.
"""

import os
import logging
import warnings

# Handle numpy._core import issue
try:
    import numpy as np
    # Test numpy._core availability
    try:
        from numpy import _core
    except ImportError:
        # If numpy._core is not available, try to import numpy differently
        import numpy as np
        # Suppress warnings about numpy._core
        warnings.filterwarnings('ignore', message='.*numpy._core.*')
except ImportError as e:
    logging.error(f"Failed to import numpy: {e}")
    raise ImportError("NumPy is required but not properly installed. Please run: pip install numpy==1.26.4")

import pandas as pd
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score
from django.db.models import Count

from .models import Game, Genre, Platform

logger = logging.getLogger(__name__)

class GameClusteringEngine:
    """
    Engine untuk clustering game menggunakan algoritma K-Means.
    """
    
    def __init__(self, n_clusters=5, random_state=42):
        """
        Inisialisasi clustering engine.
        
        Args:
            n_clusters (int): Jumlah cluster yang diinginkan
            random_state (int): Seed untuk reproducibility
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.silhouette_avg = None
        
    def prepare_features(self, games_queryset=None):
        """
        Menyiapkan fitur-fitur untuk clustering dari data game.
        Menggunakan hanya 4 atribut: genre, rating, esrb, platform
        
        Args:
            games_queryset: QuerySet dari model Game
            
        Returns:
            pandas.DataFrame: DataFrame dengan fitur-fitur yang sudah diproses
        """
        if games_queryset is None:
            games_queryset = Game.objects.all()
            
        # Konversi ke list untuk memudahkan pemrosesan
        games_data = []
        
        for game in games_queryset:
            # Ambil genre utama (yang pertama jika ada multiple)
            primary_genre = game.genres.first()
            genre_name = primary_genre.name if primary_genre else 'Unknown'
            
            # Ambil platform utama
            primary_platform = game.platforms.first()
            platform_name = primary_platform.name if primary_platform else 'Unknown'
            
            game_data = {
                'id': game.id,
                'name': game.name,
                'rating': game.rating or 0.0,
                'genre': genre_name,
                'platform': platform_name,
                'esrb': game.esrb or 'Unknown',
            }
            games_data.append(game_data)
        
        # Buat DataFrame
        df = pd.DataFrame(games_data)
        
        if df.empty:
            logger.warning("Tidak ada data game untuk clustering")
            return pd.DataFrame()
        
        # Encode categorical features - hanya 3 atribut kategorikal
        categorical_features = ['genre', 'platform', 'esrb']
        
        for feature in categorical_features:
            if feature not in self.label_encoders:
                self.label_encoders[feature] = LabelEncoder()
            
            # Fit dan transform
            df[f'{feature}_encoded'] = self.label_encoders[feature].fit_transform(df[feature])
        
        # Pilih hanya 4 fitur untuk clustering
        self.feature_columns = [
            'rating',           # Numerik
            'genre_encoded',    # Kategorikal → Numerik
            'platform_encoded', # Kategorikal → Numerik
            'esrb_encoded'      # Kategorikal → Numerik
        ]
        
        # Ambil fitur untuk clustering
        features_df = df[['id', 'name', 'genre', 'platform', 'esrb'] + self.feature_columns].copy()
        
        logger.info(f"Fitur yang disiapkan untuk clustering (4 atribut): {self.feature_columns}")
        logger.info(f"Jumlah game: {len(features_df)}")
        
        return features_df
    
    def fit(self, games_queryset=None):
        """
        Melatih model K-Means dengan data game.
        
        Args:
            games_queryset: QuerySet dari model Game
            
        Returns:
            numpy.array: Label cluster untuk setiap game
        """
        # Siapkan fitur
        features_df = self.prepare_features(games_queryset)
        
        if features_df.empty:
            logger.error("Tidak dapat melakukan clustering: tidak ada data")
            return np.array([])
        
        # Ambil fitur numerik saja
        X = features_df[self.feature_columns].values
        
        # Normalisasi fitur
        X_scaled = self.scaler.fit_transform(X)
        
        # Inisialisasi dan latih K-Means
        self.kmeans_model = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10,
            max_iter=300
        )
        
        # Fit model
        cluster_labels = self.kmeans_model.fit_predict(X_scaled)
        
        # Hitung silhouette score
        if len(set(cluster_labels)) > 1:  # Minimal 2 cluster untuk silhouette score
            self.silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            logger.info(f"Silhouette Score: {self.silhouette_avg:.3f}")
        else:
            self.silhouette_avg = 0.0
            logger.warning("Hanya 1 cluster ditemukan, silhouette score = 0")
        
        # Simpan hasil clustering ke DataFrame
        features_df['Cluster'] = cluster_labels
        
        # Simpan ke file CSV
        output_path = 'df_clustering.csv'
        features_df.to_csv(output_path, index=False)
        logger.info(f"Data clustering disimpan ke {output_path}")
        
        # Simpan model
        model_path = 'model_kmeans.pkl'
        joblib.dump(self.kmeans_model, model_path)
        logger.info(f"Model K-Means disimpan ke {model_path}")
        
        return cluster_labels
    
    def predict(self, games_queryset):
        """
        Prediksi cluster untuk game baru.
        
        Args:
            games_queryset: QuerySet dari model Game
            
        Returns:
            numpy.array: Label cluster untuk setiap game
        """
        if self.kmeans_model is None:
            logger.error("Model belum dilatih. Jalankan fit() terlebih dahulu.")
            return np.array([])
        
        # Siapkan fitur
        features_df = self.prepare_features(games_queryset)
        
        if features_df.empty:
            return np.array([])
        
        # Ambil fitur numerik
        X = features_df[self.feature_columns].values
        
        # Normalisasi dengan scaler yang sudah dilatih
        X_scaled = self.scaler.transform(X)
        
        # Prediksi cluster
        cluster_labels = self.kmeans_model.predict(X_scaled)
        
        return cluster_labels
    
    def get_cluster_recommendations(self, anchor_game, num_recommendations=10):
        """
        Mendapatkan rekomendasi game dari cluster yang sama.
        Prioritas: games_clustered_k3_with_ids.csv -> games_clustered_k3.csv -> df_clustering.csv
        
        Args:
            anchor_game: Instance dari model Game
            num_recommendations (int): Jumlah rekomendasi yang diinginkan
            
        Returns:
            list: List dari instance Game yang direkomendasikan
        """
        # Coba baca dari file clustering terbaru dengan ID database
        k3_with_ids_path = 'games_clustered_k3_with_ids.csv'
        k3_cluster_path = 'games_clustered_k3.csv'
        cluster_data_path = 'df_clustering.csv'
        
        df_clustering = None
        use_db_ids = False
        
        # Prioritas 1: File K3 dengan database IDs
        if os.path.exists(k3_with_ids_path):
            try:
                logger.info("Menggunakan data clustering terbaru dengan DB IDs dari games_clustered_k3_with_ids.csv")
                df_clustering = pd.read_csv(k3_with_ids_path)
                use_db_ids = True
            except Exception as e:
                logger.warning(f"Gagal membaca games_clustered_k3_with_ids.csv: {str(e)}, mencoba file lama")
        
        # Prioritas 2: File K3 tanpa IDs
        if df_clustering is None and os.path.exists(k3_cluster_path):
            try:
                logger.info("Menggunakan data clustering terbaru dari games_clustered_k3.csv")
                df_clustering = pd.read_csv(k3_cluster_path)
                use_db_ids = False
            except Exception as e:
                logger.warning(f"Gagal membaca games_clustered_k3.csv: {str(e)}, mencoba file lama")
        
        # Fallback: File lama
        if df_clustering is None and os.path.exists(cluster_data_path):
            try:
                logger.info("Menggunakan data clustering dari df_clustering.csv")
                df_clustering = pd.read_csv(cluster_data_path)
                use_db_ids = False
            except Exception as e:
                logger.error(f"Gagal membaca df_clustering.csv: {str(e)}")
                return []
        
        if df_clustering is None:
            logger.warning("Tidak ada file clustering yang tersedia")
            return []
        
        # Cari cluster dari anchor game
        if use_db_ids and 'db_id' in df_clustering.columns:
            # Gunakan database ID untuk pencarian yang lebih akurat
            game_row = df_clustering[df_clustering['db_id'] == anchor_game.id]
            if game_row.empty:
                logger.warning(f"Game dengan ID {anchor_game.id} tidak ditemukan di data clustering")
                return []
        else:
            # Fallback ke pencarian berdasarkan nama
            name_column = 'name' if 'name' in df_clustering.columns else 'Name'
            game_row = df_clustering[df_clustering[name_column] == anchor_game.name]
            if game_row.empty:
                logger.warning(f"Game '{anchor_game.name}' tidak ditemukan di data clustering")
                return []
        
        cluster_column = 'Cluster' if 'Cluster' in df_clustering.columns else 'cluster'
        cluster_id = game_row[cluster_column].values[0]
        
        # Ambil game lain dari cluster yang sama
        if use_db_ids and 'db_id' in df_clustering.columns:
            same_cluster_df = df_clustering[
                (df_clustering[cluster_column] == cluster_id) &
                (df_clustering['db_id'] != anchor_game.id)
            ]
        else:
            name_column = 'name' if 'name' in df_clustering.columns else 'Name'
            same_cluster_df = df_clustering[
                (df_clustering[cluster_column] == cluster_id) &
                (df_clustering[name_column] != anchor_game.name)
            ]
        
        # Urutkan berdasarkan rating
        rating_column = 'rating' if 'rating' in same_cluster_df.columns else 'Rating'
        if rating_column in same_cluster_df.columns:
            same_cluster_df = same_cluster_df.sort_values(
                rating_column, 
                ascending=False
            )
        
        # Ambil rekomendasi berdasarkan metode yang tersedia
        recommended_games = []
        
        if use_db_ids and 'db_id' in same_cluster_df.columns:
            # Gunakan database ID langsung
            recommended_ids = same_cluster_df['db_id'].head(num_recommendations).tolist()
            recommended_ids = [int(id_val) for id_val in recommended_ids if pd.notna(id_val)]
            
            if recommended_ids:
                recommended_games = list(Game.objects.filter(id__in=recommended_ids))
                # Pertahankan urutan sesuai dengan sorting
                id_to_game = {game.id: game for game in recommended_games}
                recommended_games = [id_to_game[game_id] for game_id in recommended_ids if game_id in id_to_game]
        else:
            # Fallback ke pencarian berdasarkan nama
            name_column = 'name' if 'name' in same_cluster_df.columns else 'Name'
            recommended_game_names = same_cluster_df[name_column].head(num_recommendations).tolist()
            
            # Query ke database untuk mendapatkan objek Game
            for name in recommended_game_names:
                try:
                    game = Game.objects.filter(name__iexact=name).first()
                    if game:
                        recommended_games.append(game)
                except Exception as e:
                    logger.warning(f"Error mencari game '{name}': {str(e)}")
                    continue
        
        if recommended_games:
            logger.info(f"Ditemukan {len(recommended_games)} rekomendasi dari cluster {cluster_id}")
        else:
            logger.warning("K-Means clustering tidak menghasilkan rekomendasi.")
        
        return recommended_games
    
    def get_cluster_info(self):
        """
        Mendapatkan informasi tentang cluster yang terbentuk.
        
        Returns:
            dict: Informasi cluster
        """
        cluster_data_path = 'df_clustering.csv'
        if not os.path.exists(cluster_data_path):
            return {}
        
        try:
            df_clustering = pd.read_csv(cluster_data_path)
            
            cluster_info = {}
            for cluster_id in df_clustering['Cluster'].unique():
                cluster_games = df_clustering[df_clustering['Cluster'] == cluster_id]
                
                cluster_info[cluster_id] = {
                    'jumlah_game': len(cluster_games),
                    'rata_rata_rating': cluster_games['rating'].mean(),
                    'game_sample': cluster_games['name'].head(5).tolist()
                }
            
            return cluster_info
            
        except Exception as e:
            logger.error(f"Gagal mendapatkan info cluster: {str(e)}")
            return {}
    
    def save_model(self, model_path='model_kmeans.pkl'):
        """
        Menyimpan model yang sudah dilatih.
        
        Args:
            model_path (str): Path untuk menyimpan model
        """
        if self.kmeans_model is None:
            logger.error("Model belum dilatih")
            return False
        
        try:
            # Simpan model dan scaler
            model_data = {
                'kmeans_model': self.kmeans_model,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_columns': self.feature_columns,
                'n_clusters': self.n_clusters,
                'silhouette_score': self.silhouette_avg
            }
            
            joblib.dump(model_data, model_path)
            logger.info(f"Model berhasil disimpan ke {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Gagal menyimpan model: {str(e)}")
            return False
    
    def load_model(self, model_path='model_kmeans.pkl'):
        """
        Memuat model yang sudah disimpan.
        Prioritas: kmeans_model_k3.pkl -> model_kmeans.pkl
        
        Args:
            model_path (str): Path model yang akan dimuat
        """
        # Coba muat dari file K-Means terbaru dengan 3 cluster terlebih dahulu
        k3_model_path = 'kmeans_model_k3.pkl'
        
        if os.path.exists(k3_model_path):
            try:
                logger.info("Menggunakan model K-Means terbaru dengan 3 cluster dari kmeans_model_k3.pkl")
                
                # Suppress sklearn version warnings dan numpy._core warnings
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
                    warnings.filterwarnings("ignore", message=".*numpy._core.*")
                    warnings.filterwarnings("ignore", category=FutureWarning)
                    warnings.filterwarnings("ignore", category=DeprecationWarning)
                    
                    model_data = joblib.load(k3_model_path)
                
                # Set n_clusters ke 3 untuk model terbaru
                self.n_clusters = 3
                
                # Cek apakah ini format baru (dict) atau format lama (langsung KMeans object)
                if isinstance(model_data, dict):
                    # Cek apakah semua key yang diperlukan ada
                    if 'kmeans_model' in model_data:
                        self.kmeans_model = model_data['kmeans_model']
                        self.scaler = model_data.get('scaler', StandardScaler())
                        self.label_encoders = model_data.get('label_encoders', {})
                        self.feature_columns = model_data.get('feature_columns', ['rating', 'genre_encoded', 'platform_encoded', 'esrb_encoded'])
                        self.n_clusters = model_data.get('n_clusters', 3)
                        self.silhouette_avg = model_data.get('silhouette_score', 0.0)
                        logger.info("Model K3 format dict berhasil dimuat")
                    else:
                        logger.error("Model K3 format dict tidak valid - missing 'kmeans_model' key")
                        logger.error(f"Available keys: {list(model_data.keys())}")
                        return False
                else:
                    # Format lama - langsung KMeans object
                    if hasattr(model_data, 'predict'):  # Validasi bahwa ini adalah KMeans object
                        self.kmeans_model = model_data
                        self.n_clusters = getattr(model_data, 'n_clusters', 3)
                        # Set default values
                        self.scaler = StandardScaler()
                        self.label_encoders = {}
                        self.feature_columns = ['rating', 'genre_encoded', 'platform_encoded', 'esrb_encoded']
                        logger.info("Model K3 format lama berhasil dimuat dengan default values")
                    else:
                        logger.error(f"Model K3 bukan KMeans object yang valid: {type(model_data)}")
                        return False
                
                logger.info(f"Model K-Means berhasil dimuat dari {k3_model_path} dengan {self.n_clusters} clusters")
                return True
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Gagal memuat model K3: {error_msg}")
                
                # Berikan informasi lebih detail untuk debugging
                if "239" in error_msg:
                    logger.error("Error 239: Kemungkinan masalah kompatibilitas sklearn version")
                elif "pickle" in error_msg.lower():
                    logger.error("Error pickle: File model mungkin corrupt atau tidak kompatibel")
                elif "numpy" in error_msg.lower():
                    logger.error("Error numpy: Masalah dengan numpy version atau array format")
                
                logger.info("Mencoba model fallback...")
        
        # Fallback ke model lama
        if not os.path.exists(model_path):
            logger.error(f"File model {model_path} tidak ditemukan")
            logger.warning("Gagal memuat model K-Means, akan menggunakan fallback.")
            return False
        
        try:
            logger.info(f"Mencoba memuat model fallback dari {model_path}")
            
            # Suppress sklearn version warnings dan numpy._core warnings
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
                warnings.filterwarnings("ignore", message=".*numpy._core.*")
                warnings.filterwarnings("ignore", category=FutureWarning)
                warnings.filterwarnings("ignore", category=DeprecationWarning)
                
                model_data = joblib.load(model_path)
            
            # Cek apakah ini format baru (dict) atau format lama (langsung KMeans object)
            if isinstance(model_data, dict):
                if 'kmeans_model' in model_data:
                    self.kmeans_model = model_data['kmeans_model']
                    self.scaler = model_data.get('scaler', StandardScaler())
                    self.label_encoders = model_data.get('label_encoders', {})
                    self.feature_columns = model_data.get('feature_columns', ['rating', 'genre_encoded', 'platform_encoded', 'esrb_encoded'])
                    self.n_clusters = model_data.get('n_clusters', 5)
                    self.silhouette_avg = model_data.get('silhouette_score', 0.0)
                    logger.info("Model fallback format dict berhasil dimuat")
                else:
                    logger.error("Model fallback format dict tidak valid - missing 'kmeans_model' key")
                    logger.error(f"Available keys: {list(model_data.keys())}")
                    return False
            else:
                # Format lama - langsung KMeans object
                if hasattr(model_data, 'predict'):  # Validasi bahwa ini adalah KMeans object
                    self.kmeans_model = model_data
                    self.n_clusters = getattr(model_data, 'n_clusters', 5)
                    # Set default values
                    self.scaler = StandardScaler()
                    self.label_encoders = {}
                    self.feature_columns = ['rating', 'genre_encoded', 'platform_encoded', 'esrb_encoded']
                    logger.info("Model fallback format lama berhasil dimuat dengan default values")
                else:
                    logger.error(f"Model fallback bukan KMeans object yang valid: {type(model_data)}")
                    return False
            
            logger.info(f"Model berhasil dimuat dari {model_path} dengan {self.n_clusters} clusters")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gagal memuat model fallback: {error_msg}")
            
            # Berikan informasi lebih detail untuk debugging
            if "239" in error_msg:
                logger.error("Error 239: Kemungkinan masalah kompatibilitas sklearn version")
                logger.error("Solusi: Regenerasi model dengan versi sklearn yang sesuai")
            elif "pickle" in error_msg.lower():
                logger.error("Error pickle: File model mungkin corrupt atau tidak kompatibel")
                logger.error("Solusi: Hapus file model dan regenerasi ulang")
            elif "numpy" in error_msg.lower():
                logger.error("Error numpy: Masalah dengan numpy version atau array format")
                logger.error("Solusi: Update numpy atau regenerasi model")
            
            logger.warning("Model tidak dapat dimuat, akan menggunakan fallback.")
            return False
