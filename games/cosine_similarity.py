"""
Cosine Similarity Engine untuk Game Recommendation
Modul ini menyediakan fungsionalitas untuk rekomendasi game berdasarkan cosine similarity.
Menggunakan 4 atribut: genre, rating, esrb, platform
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
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Count

from .models import Game, Genre, Platform

logger = logging.getLogger(__name__)

class CosineSimilarityEngine:
    """
    Engine untuk rekomendasi game menggunakan Cosine Similarity.
    Menggunakan 4 atribut: genre, rating, esrb, platform
    """
    
    def __init__(self):
        """
        Inisialisasi cosine similarity engine.
        """
        self.similarity_matrix = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.games_df = None
        self.game_index_map = {}
        
    def prepare_features(self, games_queryset=None):
        """
        Menyiapkan fitur-fitur untuk cosine similarity dari data game.
        Prioritas: df_cb_content_ready_with_ids.csv -> df_cb_content_ready.csv -> fallback
        
        Args:
            games_queryset: QuerySet dari model Game (opsional, akan menggunakan CSV jika tersedia)
            
        Returns:
            pandas.DataFrame: DataFrame dengan fitur-fitur yang sudah diproses
        """
        # Coba baca dari file CSV dengan database IDs terlebih dahulu
        csv_with_ids_path = 'df_cb_content_ready_with_ids.csv'
        csv_path = 'df_cb_content_ready.csv'
        
        # Prioritas 1: File dengan database IDs
        if os.path.exists(csv_with_ids_path):
            try:
                logger.info("Menggunakan dataset dengan DB IDs dari df_cb_content_ready_with_ids.csv")
                df_ready = pd.read_csv(csv_with_ids_path)
                
                # Gunakan database ID langsung jika tersedia
                if 'db_id' in df_ready.columns:
                    df_ready = df_ready.dropna(subset=['db_id'])
                    df_ready['id'] = df_ready['db_id'].astype(int)
                else:
                    # Fallback ke mapping nama jika tidak ada db_id
                    if games_queryset is None:
                        games_queryset = Game.objects.all()
                    
                    name_to_id = {game.name: game.id for game in games_queryset}
                    df_ready['id'] = df_ready['Name'].map(name_to_id)
                    df_ready = df_ready.dropna(subset=['id'])
                    df_ready['id'] = df_ready['id'].astype(int)
                
                # Rename kolom untuk konsistensi
                df_ready = df_ready.rename(columns={
                    'Name': 'name',
                    'Rating': 'rating',
                    'Genres': 'genres',
                    'Platforms': 'platforms',
                    'ESRB': 'esrb'
                })
                
                # Gunakan fitur yang sudah di-encode
                self.feature_columns = [
                    'Rating_scaled',    # Rating yang sudah dinormalisasi
                    'ESRB_cat'         # ESRB yang sudah di-encode
                ]
                
                # Tambahkan encoding untuk genres dan platforms jika diperlukan
                if 'Genres_list' in df_ready.columns:
                    df_ready['genres_encoded'] = df_ready['Genres_list'].apply(
                        lambda x: hash(str(x)) % 1000 if pd.notna(x) else 0
                    )
                    self.feature_columns.append('genres_encoded')
                
                if 'Platforms_list' in df_ready.columns:
                    df_ready['platforms_encoded'] = df_ready['Platforms_list'].apply(
                        lambda x: hash(str(x)) % 1000 if pd.notna(x) else 0
                    )
                    self.feature_columns.append('platforms_encoded')
                
                # Ambil kolom yang diperlukan
                required_cols = ['id', 'name', 'genres', 'platforms', 'esrb'] + self.feature_columns
                available_cols = [col for col in required_cols if col in df_ready.columns]
                features_df = df_ready[available_cols].copy()
                
                logger.info(f"Dataset berhasil dimuat dari CSV dengan DB IDs: {len(features_df)} game")
                logger.info(f"Fitur yang digunakan: {self.feature_columns}")
                
                return features_df
                
            except Exception as e:
                logger.warning(f"Gagal membaca CSV dengan IDs: {str(e)}, mencoba file tanpa IDs")
        
        # Prioritas 2: File tanpa database IDs
        if os.path.exists(csv_path):
            try:
                logger.info("Menggunakan dataset yang sudah diproses dari df_cb_content_ready.csv")
                df_ready = pd.read_csv(csv_path)
                
                # Buat mapping ID berdasarkan nama game dari database
                if games_queryset is None:
                    games_queryset = Game.objects.all()
                
                name_to_id = {game.name: game.id for game in games_queryset}
                
                # Tambahkan kolom ID berdasarkan nama
                df_ready['id'] = df_ready['Name'].map(name_to_id)
                
                # Filter hanya game yang ada di database
                df_ready = df_ready.dropna(subset=['id'])
                df_ready['id'] = df_ready['id'].astype(int)
                
                # Rename kolom untuk konsistensi
                df_ready = df_ready.rename(columns={
                    'Name': 'name',
                    'Rating': 'rating',
                    'Genres': 'genres',
                    'Platforms': 'platforms',
                    'ESRB': 'esrb'
                })
                
                # Gunakan fitur yang sudah di-encode
                self.feature_columns = [
                    'Rating_scaled',    # Rating yang sudah dinormalisasi
                    'ESRB_cat'         # ESRB yang sudah di-encode
                ]
                
                # Tambahkan encoding untuk genres dan platforms jika diperlukan
                if 'Genres_list' in df_ready.columns:
                    df_ready['genres_encoded'] = df_ready['Genres_list'].apply(
                        lambda x: hash(str(x)) % 1000 if pd.notna(x) else 0
                    )
                    self.feature_columns.append('genres_encoded')
                
                if 'Platforms_list' in df_ready.columns:
                    df_ready['platforms_encoded'] = df_ready['Platforms_list'].apply(
                        lambda x: hash(str(x)) % 1000 if pd.notna(x) else 0
                    )
                    self.feature_columns.append('platforms_encoded')
                
                # Ambil kolom yang diperlukan
                required_cols = ['id', 'name', 'genres', 'platforms', 'esrb'] + self.feature_columns
                available_cols = [col for col in required_cols if col in df_ready.columns]
                features_df = df_ready[available_cols].copy()
                
                logger.info(f"Dataset berhasil dimuat dari CSV dengan {len(features_df)} game")
                logger.info(f"Fitur yang digunakan: {self.feature_columns}")
                
                return features_df
                
            except Exception as e:
                logger.warning(f"Gagal membaca CSV, menggunakan fallback: {str(e)}")
        
        # Fallback ke metode lama jika CSV tidak tersedia
        logger.info("Menggunakan metode fallback untuk menyiapkan fitur")
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
                'genres': genre_name,
                'platforms': platform_name,
                'esrb': game.esrb or 'Unknown',
            }
            games_data.append(game_data)
        
        # Buat DataFrame
        df = pd.DataFrame(games_data)
        
        if df.empty:
            logger.warning("Tidak ada data game untuk cosine similarity")
            return pd.DataFrame()
        
        # Encode categorical features - hanya 3 atribut kategorikal
        categorical_features = ['genres', 'platforms', 'esrb']
        
        for feature in categorical_features:
            if feature not in self.label_encoders:
                self.label_encoders[feature] = LabelEncoder()
            
            # Fit dan transform
            df[f'{feature}_encoded'] = self.label_encoders[feature].fit_transform(df[feature])
        
        # Pilih hanya 4 fitur untuk similarity
        self.feature_columns = [
            'rating',           # Numerik
            'genres_encoded',    # Kategorikal → Numerik
            'platforms_encoded', # Kategorikal → Numerik
            'esrb_encoded'      # Kategorikal → Numerik
        ]
        
        # Ambil fitur untuk similarity
        features_df = df[['id', 'name', 'genres', 'platforms', 'esrb'] + self.feature_columns].copy()
        
        logger.info(f"Fitur yang disiapkan untuk cosine similarity (4 atribut): {self.feature_columns}")
        logger.info(f"Jumlah game: {len(features_df)}")
        
        return features_df
    
    def fit(self, games_queryset=None):
        """
        Melatih model Cosine Similarity dengan data game.
        
        Args:
            games_queryset: QuerySet dari model Game
            
        Returns:
            numpy.array: Similarity matrix
        """
        # Siapkan fitur
        self.games_df = self.prepare_features(games_queryset)
        
        if self.games_df.empty:
            logger.error("Tidak dapat menghitung cosine similarity: tidak ada data")
            return np.array([])
        
        # Buat mapping index untuk game
        self.game_index_map = {game_id: idx for idx, game_id in enumerate(self.games_df['id'])}
        
        # Ambil fitur numerik saja
        X = self.games_df[self.feature_columns].values
        
        # Normalisasi fitur
        X_scaled = self.scaler.fit_transform(X)
        
        # Hitung cosine similarity matrix
        self.similarity_matrix = cosine_similarity(X_scaled)
        
        logger.info(f"Cosine similarity matrix berhasil dihitung dengan shape: {self.similarity_matrix.shape}")
        
        # Simpan model
        self.save_model()
        
        return self.similarity_matrix
    
    def get_similar_games(self, game_id, num_recommendations=10):
        """
        Mendapatkan rekomendasi game berdasarkan cosine similarity.
        
        Args:
            game_id (int): ID game yang dijadikan acuan
            num_recommendations (int): Jumlah rekomendasi yang diinginkan
            
        Returns:
            list: List dari instance Game yang direkomendasikan
        """
        if self.similarity_matrix is None or self.games_df is None:
            logger.warning("Cosine similarity tidak menghasilkan rekomendasi.")
            return []
        
        # Cari index game dalam matrix
        if game_id not in self.game_index_map:
            logger.warning(f"Game dengan ID {game_id} tidak ditemukan dalam data")
            logger.warning("Cosine similarity tidak menghasilkan rekomendasi.")
            return []
        
        try:
            game_idx = self.game_index_map[game_id]
            
            # Validasi index
            if game_idx >= len(self.similarity_matrix):
                logger.warning(f"Index game {game_idx} melebihi ukuran matrix {len(self.similarity_matrix)}")
                logger.warning("Cosine similarity tidak menghasilkan rekomendasi.")
                return []
            
            # Ambil similarity scores untuk game ini
            similarity_scores = self.similarity_matrix[game_idx]
            
            # Buat list (index, score) dan urutkan berdasarkan score
            game_scores = [(idx, score) for idx, score in enumerate(similarity_scores)]
            game_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Ambil top recommendations (skip index 0 karena itu game itu sendiri)
            recommended_indices = [idx for idx, score in game_scores[1:num_recommendations+1] if idx < len(self.games_df)]
            
            if not recommended_indices:
                logger.warning("Cosine similarity tidak menghasilkan rekomendasi.")
                return []
            
            # Ambil game IDs dari indices dengan error handling
            recommended_game_ids = []
            for idx in recommended_indices:
                try:
                    if idx < len(self.games_df):
                        game_id_val = self.games_df.iloc[idx]['id']
                        recommended_game_ids.append(int(game_id_val))
                except (IndexError, KeyError, ValueError) as e:
                    logger.warning(f"Error mengambil game ID dari index {idx}: {str(e)}")
                    continue
            
            if not recommended_game_ids:
                logger.warning("Cosine similarity tidak menghasilkan rekomendasi.")
                return []
            
            # Query ke database untuk mendapatkan objek Game
            recommended_games = Game.objects.filter(id__in=recommended_game_ids)
            
            # Pertahankan urutan sesuai dengan similarity score
            recommended_games_sorted = []
            for rec_game_id in recommended_game_ids:
                try:
                    game = recommended_games.get(id=rec_game_id)
                    recommended_games_sorted.append(game)
                except Game.DoesNotExist:
                    continue
            
            if recommended_games_sorted:
                logger.info(f"Ditemukan {len(recommended_games_sorted)} rekomendasi berdasarkan cosine similarity")
            else:
                logger.warning("Cosine similarity tidak menghasilkan rekomendasi.")
            
            return recommended_games_sorted
            
        except Exception as e:
            logger.error(f"Error saat membuat rekomendasi similarity: {str(e)}")
            logger.warning("Cosine similarity tidak menghasilkan rekomendasi.")
            return []
    
    def get_similarity_score(self, game_id1, game_id2):
        """
        Mendapatkan similarity score antara dua game.
        
        Args:
            game_id1 (int): ID game pertama
            game_id2 (int): ID game kedua
            
        Returns:
            float: Similarity score (0-1)
        """
        if self.similarity_matrix is None:
            logger.warning("Model belum dilatih")
            return 0.0
        
        if game_id1 not in self.game_index_map or game_id2 not in self.game_index_map:
            logger.warning("Salah satu atau kedua game tidak ditemukan dalam data")
            return 0.0
        
        idx1 = self.game_index_map[game_id1]
        idx2 = self.game_index_map[game_id2]
        
        return float(self.similarity_matrix[idx1][idx2])
    
    def save_model(self, model_path='cosine_similarity_model.pkl'):
        """
        Menyimpan model yang sudah dilatih.
        
        Args:
            model_path (str): Path untuk menyimpan model
        """
        if self.similarity_matrix is None:
            logger.error("Model belum dilatih")
            return False
        
        try:
            # Simpan model dan data pendukung
            model_data = {
                'similarity_matrix': self.similarity_matrix,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_columns': self.feature_columns,
                'games_df': self.games_df,
                'game_index_map': self.game_index_map
            }
            
            joblib.dump(model_data, model_path)
            logger.info(f"Model cosine similarity berhasil disimpan ke {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Gagal menyimpan model: {str(e)}")
            return False
    
    def load_model(self, model_path='cosine_similarity_model.pkl'):
        """
        Memuat model yang sudah disimpan.
        Prioritas: cosine_similarity_matrix.npy -> cosine_similarity_model.pkl
        
        Args:
            model_path (str): Path model yang akan dimuat
        """
        # Coba muat dari file .npy terbaru terlebih dahulu
        npy_matrix_path = 'cosine_similarity_matrix.npy'
        csv_data_path = 'df_cb_content_ready.csv'
        
        if os.path.exists(npy_matrix_path) and os.path.exists(csv_data_path):
            try:
                logger.info("Menggunakan similarity matrix terbaru dari cosine_similarity_matrix.npy")
                
                # Muat similarity matrix
                self.similarity_matrix = np.load(npy_matrix_path)
                
                # Muat data game dari CSV
                self.games_df = self.prepare_features()
                
                if not self.games_df.empty:
                    # Buat mapping index untuk game
                    self.game_index_map = {game_id: idx for idx, game_id in enumerate(self.games_df['id'])}
                    
                    # Set feature columns sesuai dengan yang digunakan
                    self.feature_columns = [col for col in ['Rating_scaled', 'ESRB_cat', 'genres_encoded', 'platforms_encoded'] 
                                          if col in self.games_df.columns]
                    
                    # Inisialisasi scaler dan encoders (tidak diperlukan karena data sudah diproses)
                    self.scaler = StandardScaler()
                    self.label_encoders = {}
                    
                    logger.info(f"Model berhasil dimuat dari file .npy dengan {len(self.games_df)} game")
                    logger.info(f"Similarity matrix shape: {self.similarity_matrix.shape}")
                    return True
                else:
                    logger.warning("Data game kosong dari CSV")
                    
            except Exception as e:
                logger.warning(f"Gagal memuat dari file .npy: {str(e)}, mencoba file .pkl")
        
        # Fallback ke file .pkl lama
        if not os.path.exists(model_path):
            logger.error(f"File model {model_path} tidak ditemukan")
            return False
        
        try:
            # Suppress sklearn version warnings
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
                model_data = joblib.load(model_path)
            
            # Cek apakah model data dalam format yang benar
            if isinstance(model_data, dict):
                required_keys = ['similarity_matrix', 'scaler', 'label_encoders', 'feature_columns', 'games_df', 'game_index_map']
                if all(key in model_data for key in required_keys):
                    self.similarity_matrix = model_data['similarity_matrix']
                    self.scaler = model_data['scaler']
                    self.label_encoders = model_data['label_encoders']
                    self.feature_columns = model_data['feature_columns']
                    self.games_df = model_data['games_df']
                    self.game_index_map = model_data['game_index_map']
                else:
                    logger.warning("Model format tidak lengkap, mencoba menggunakan data yang tersedia")
                    # Coba ambil data yang tersedia
                    self.similarity_matrix = model_data.get('similarity_matrix', None)
                    self.scaler = model_data.get('scaler', StandardScaler())
                    self.label_encoders = model_data.get('label_encoders', {})
                    self.feature_columns = model_data.get('feature_columns', [])
                    self.games_df = model_data.get('games_df', None)
                    self.game_index_map = model_data.get('game_index_map', {})
                    
                    if self.similarity_matrix is None:
                        logger.error("Similarity matrix tidak ditemukan dalam model data")
                        return False
            else:
                logger.error("Format model tidak dikenali")
                return False
            
            logger.info(f"Model cosine similarity berhasil dimuat dari {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Gagal memuat model: {str(e)}")
            # Jika gagal memuat model, inisialisasi dengan nilai default
            logger.info("Mencoba inisialisasi model baru...")
            try:
                self.similarity_matrix = None
                self.scaler = StandardScaler()
                self.label_encoders = {}
                self.feature_columns = []
                self.games_df = None
                self.game_index_map = {}
                logger.warning("Model tidak dapat dimuat, menggunakan konfigurasi default. Perlu training ulang.")
                return False
            except Exception as init_error:
                logger.error(f"Gagal inisialisasi model default: {str(init_error)}")
                return False
    
    def get_model_info(self):
        """
        Mendapatkan informasi tentang model yang sudah dilatih.
        
        Returns:
            dict: Informasi model
        """
        if self.similarity_matrix is None:
            return {'status': 'Model belum dilatih'}
        
        return {
            'status': 'Model sudah dilatih',
            'matrix_shape': self.similarity_matrix.shape,
            'num_games': len(self.games_df) if self.games_df is not None else 0,
            'features_used': self.feature_columns,
            'avg_similarity': float(np.mean(self.similarity_matrix)),
            'max_similarity': float(np.max(self.similarity_matrix)),
            'min_similarity': float(np.min(self.similarity_matrix))
        }
