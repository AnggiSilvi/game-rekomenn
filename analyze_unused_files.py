#!/usr/bin/env python3
"""
Script untuk menganalisis file yang tidak digunakan dalam proyek game recommender system
"""

import os
import re
from pathlib import Path

def analyze_unused_files():
    """Analisis file yang tidak digunakan dalam proyek"""
    
    # File yang digunakan berdasarkan analisis kode
    used_files = {
        # Python files yang digunakan
        'games/models.py': 'Digunakan di views.py, recommendation.py, clustering.py',
        'games/views.py': 'Digunakan di urls.py',
        'games/urls.py': 'Digunakan di config/urls.py',
        'games/recommendation.py': 'Digunakan di views.py',
        'games/clustering.py': 'Digunakan di recommendation.py',
        'games/cosine_similarity.py': 'Digunakan di recommendation.py',
        'games/utils.py': 'Digunakan di views.py',
        'games/context_processors.py': 'Kemungkinan digunakan di settings.py',
        'config/settings.py': 'File konfigurasi Django utama',
        'config/urls.py': 'URL routing utama',
        'config/wsgi.py': 'WSGI configuration untuk deployment',
        'manage.py': 'Django management script',
        
        # Template files yang digunakan
        'games/templates/games/base.html': 'Extended oleh semua template lain',
        'games/templates/games/home.html': 'Digunakan di views.home_page',
        'games/templates/games/login.html': 'Digunakan di views.login_view',
        'games/templates/games/register.html': 'Digunakan di views.register_view',
        'games/templates/games/dashboard.html': 'Digunakan di views.dashboard_view',
        'games/templates/games/game_detail.html': 'Digunakan di views.game_detail',
        'games/templates/games/genre_list.html': 'Digunakan di views.genre_list',
        'games/templates/games/platform_list.html': 'Digunakan di views.platform_list',
        'games/templates/games/esrb_list.html': 'Digunakan di views.esrb_list',
        'games/templates/games/rating_list.html': 'Digunakan di views.rating_list',
        'games/templates/games/games_by_category.html': 'Digunakan di multiple views',
        'games/templates/games/advanced_search.html': 'Kemungkinan digunakan (ada di template)',
        
        # Static files yang digunakan
        'games/static/games/css/style.css': 'Digunakan di base.html',
        
        # Management commands
        'games/management/commands/import_csv.py': 'Django management command',
        'games/management/commands/train_kmeans.py': 'Django management command',
        'games/management/commands/train_recommendations.py': 'Django management command',
        
        # Migration files
        'games/migrations/0001_initial.py': 'Database migration',
        'games/migrations/0002_platform_icon_class.py': 'Database migration',
        'games/migrations/0003_game_content_vector_game_popularity_score_and_more.py': 'Database migration',
        'games/migrations/0004_game_esrb.py': 'Database migration',
        'games/migrations/0005_game_store_url.py': 'Database migration',
        'games/migrations/0006_remove_usergameinteraction_game_and_more.py': 'Database migration',
        'games/migrations/0007_userbookmark_usergamerating.py': 'Database migration',
        'games/migrations/0008_alter_usergamerating_unique_together_and_more.py': 'Database migration',
        
        # Test files
        'games/tests/test_clustering.py': 'Unit test untuk clustering',
        'games/tests/test_recommendations.py': 'Unit test untuk recommendations',
        
        # Data files yang digunakan
        'games_clustered_k3_with_ids.csv': 'Digunakan di clustering.py',
        'cosine_similarity_matrix.npy': 'Digunakan di cosine_similarity.py',
        'cosine_similarity_model.pkl': 'Digunakan di recommendation.py',
        'kmeans_model_k3.pkl': 'Digunakan di clustering.py',
        'df_cb_content_ready_with_ids.csv': 'Digunakan di cosine_similarity.py',
        'games_with_images.csv': 'Data file untuk import',
        
        # Configuration files
        'requirements.txt': 'Dependencies list',
        'app.yaml': 'Google App Engine configuration',
        '.gitignore': 'Git ignore rules',
        'README.md': 'Project documentation',
        'LICENSE': 'License file',
    }
    
    # File yang kemungkinan tidak digunakan
    potentially_unused_files = {
        'clustering_analysis.ipynb': 'Jupyter notebook - kemungkinan hanya untuk analisis/development',
        'test_original_files_usage.py': 'Script test - kemungkinan temporary',
    }
    
    # Scan semua file dalam proyek
    all_files = []
    project_root = Path('.')
    
    for root, dirs, files in os.walk(project_root):
        # Skip virtual environment dan cache directories
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
        
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file))
            all_files.append(file_path)
    
    print("=== ANALISIS FILE YANG TIDAK DIGUNAKAN ===\n")
    
    print("1. FILE YANG DIGUNAKAN:")
    print("-" * 50)
    for file_path, usage in used_files.items():
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            print(f"   └─ {usage}")
        else:
            print(f"❌ {file_path} (file tidak ditemukan)")
        print()
    
    print("\n2. FILE YANG KEMUNGKINAN TIDAK DIGUNAKAN:")
    print("-" * 50)
    for file_path, note in potentially_unused_files.items():
        if os.path.exists(file_path):
            print(f"⚠️  {file_path}")
            print(f"   └─ {note}")
        print()
    
    print("\n3. FILE LAIN YANG DITEMUKAN:")
    print("-" * 50)
    other_files = []
    for file_path in all_files:
        if (file_path not in used_files and 
            file_path not in potentially_unused_files and
            not file_path.startswith('venv/') and
            not file_path.startswith('.git/') and
            not '__pycache__' in file_path and
            not file_path.endswith('.pyc')):
            other_files.append(file_path)
    
    if other_files:
        for file_path in sorted(other_files):
            print(f"📄 {file_path}")
    else:
        print("Tidak ada file lain yang ditemukan.")
    
    print("\n=== KESIMPULAN ===")
    print("-" * 50)
    print(f"Total file yang dianalisis: {len(all_files)}")
    print(f"File yang digunakan: {len(used_files)}")
    print(f"File yang kemungkinan tidak digunakan: {len(potentially_unused_files)}")
    print(f"File lain: {len(other_files)}")
    
    print("\n=== REKOMENDASI ===")
    print("-" * 50)
    print("File yang bisa dihapus jika tidak diperlukan:")
    for file_path, note in potentially_unused_files.items():
        if os.path.exists(file_path):
            print(f"• {file_path} - {note}")
    
    print("\nCatatan:")
    print("- Semua file migration sebaiknya TIDAK dihapus")
    print("- File test sebaiknya dipertahankan untuk quality assurance")
    print("- File konfigurasi (.gitignore, requirements.txt, dll) diperlukan")
    print("- Data files (.csv, .pkl, .npy) diperlukan untuk model ML")

if __name__ == "__main__":
    analyze_unused_files()
