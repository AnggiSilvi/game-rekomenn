"""
Management command untuk melatih model K-Means clustering
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
import logging

from games.models import Game
from games.clustering import GameClusteringEngine

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Melatih model K-Means untuk clustering game'

    def add_arguments(self, parser):
        parser.add_argument(
            '--n-clusters',
            type=int,
            default=5,
            help='Jumlah cluster yang diinginkan (default: 5)',
        )
        parser.add_argument(
            '--min-games',
            type=int,
            default=10,
            help='Jumlah minimum game yang diperlukan untuk clustering (default: 10)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Tampilkan informasi detail',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Memulai pelatihan model K-Means...'))
        
        # Setup logging
        if options['verbose']:
            logging.basicConfig(level=logging.INFO)
        
        # Cek jumlah game yang tersedia
        total_games = Game.objects.count()
        if total_games < options['min_games']:
            self.stdout.write(
                self.style.ERROR(
                    f'Jumlah game tidak mencukupi untuk clustering. '
                    f'Ditemukan: {total_games}, minimal: {options["min_games"]}'
                )
            )
            return
        
        self.stdout.write(f'Ditemukan {total_games} game untuk clustering')
        
        # Inisialisasi clustering engine
        n_clusters = min(options['n_clusters'], total_games // 2)  # Pastikan tidak terlalu banyak cluster
        clustering_engine = GameClusteringEngine(n_clusters=n_clusters)
        
        try:
            # Latih model
            self.stdout.write('Menyiapkan fitur dan melatih model...')
            cluster_labels = clustering_engine.fit()
            
            if len(cluster_labels) == 0:
                self.stdout.write(self.style.ERROR('Gagal melatih model: tidak ada data'))
                return
            
            # Tampilkan hasil
            unique_clusters = len(set(cluster_labels))
            self.stdout.write(
                self.style.SUCCESS(
                    f'Model berhasil dilatih dengan {unique_clusters} cluster'
                )
            )
            
            if clustering_engine.silhouette_avg:
                self.stdout.write(
                    f'Silhouette Score: {clustering_engine.silhouette_avg:.3f}'
                )
            
            # Tampilkan informasi cluster jika verbose
            if options['verbose']:
                self.show_cluster_info(clustering_engine)
            
            # Test model loading
            self.stdout.write('Menguji pemuatan model...')
            test_engine = GameClusteringEngine()
            if test_engine.load_model():
                self.stdout.write(self.style.SUCCESS('Model berhasil dimuat dan diuji'))
            else:
                self.stdout.write(self.style.WARNING('Model tersimpan tapi ada masalah saat pemuatan'))
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Pelatihan model K-Means selesai!\n'
                    'File yang dihasilkan:\n'
                    '- model_kmeans.pkl (model K-Means)\n'
                    '- df_clustering.csv (data hasil clustering)'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Gagal melatih model: {str(e)}')
            )
            logger.error(f'Error dalam pelatihan model: {str(e)}', exc_info=True)
    
    def show_cluster_info(self, clustering_engine):
        """Menampilkan informasi detail tentang cluster"""
        self.stdout.write('\n=== INFORMASI CLUSTER ===')
        
        cluster_info = clustering_engine.get_cluster_info()
        
        for cluster_id, info in cluster_info.items():
            self.stdout.write(f'\nCluster {cluster_id}:')
            self.stdout.write(f'  - Jumlah game: {info["jumlah_game"]}')
            self.stdout.write(f'  - Rata-rata rating: {info["rata_rata_rating"]:.2f}')
            self.stdout.write(f'  - Rata-rata popularity: {info["rata_rata_popularity"]:.2f}')
            self.stdout.write(f'  - Contoh game: {", ".join(info["game_sample"])}')
        
        self.stdout.write('\n' + '='*30)
