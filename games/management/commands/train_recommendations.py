# games/management/commands/train_recommendations.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from datetime import timedelta
import random

from games.models import Game
from games.recommendation import HybridRecommendationEngine
from games.clustering import GameClusteringEngine

class Command(BaseCommand):
    help = 'Train recommendation system and create sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample-data',
            action='store_true',
            help='Create sample users and ratings for testing',
        )
        parser.add_argument(
            '--num-users',
            type=int,
            default=20,
            help='Number of sample users to create',
        )
        parser.add_argument(
            '--train-kmeans',
            action='store_true',
            help='Train K-Means clustering model',
        )
        parser.add_argument(
            '--n-clusters',
            type=int,
            default=5,
            help='Number of clusters for K-Means (default: 5)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting recommendation system training...'))
        
        if options['create_sample_data']:
            self.create_sample_data(options['num_users'])
        
        if options['train_kmeans']:
            self.train_kmeans_model(options['n_clusters'])
        
        self.train_recommendation_system()
        
        self.stdout.write(self.style.SUCCESS('Recommendation system training completed!'))

    def create_sample_data(self, num_users):
        """Create sample users for testing (simplified version)"""
        self.stdout.write('Creating sample data...')
        
        # Get all games
        games = list(Game.objects.all())
        if not games:
            self.stdout.write(self.style.ERROR('No games found. Please import games first.'))
            return
        
        # Create sample users
        for i in range(num_users):
            username = f'user_{i+1}'
            email = f'user{i+1}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'User',
                    'last_name': f'{i+1}',
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {username}')
        
        self.stdout.write(self.style.SUCCESS(f'Created {num_users} sample users'))

    def train_recommendation_system(self):
        """Train the recommendation system"""
        self.stdout.write('Training recommendation system...')
        
        # Calculate game popularity scores based on rating only
        self.calculate_popularity_scores()
        
        # Train cosine similarity model
        self.train_cosine_similarity()
        
        self.stdout.write(self.style.SUCCESS('Recommendation system training completed'))

    def calculate_popularity_scores(self):
        """Calculate popularity scores for games based on rating"""
        self.stdout.write('Calculating game popularity scores...')
        
        games = Game.objects.all()
        
        for game in games:
            # Simple popularity formula based on rating only
            popularity_score = game.rating or 0
            
            game.popularity_score = popularity_score
            game.save(update_fields=['popularity_score'])
        
        self.stdout.write(f'Updated popularity scores for {games.count()} games')

    def train_cosine_similarity(self):
        """Train cosine similarity model"""
        self.stdout.write('Training cosine similarity model...')
        
        try:
            from games.cosine_similarity import CosineSimilarityEngine
            
            similarity_engine = CosineSimilarityEngine()
            similarity_matrix = similarity_engine.fit()
            
            if similarity_matrix is not None and similarity_matrix.size > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Cosine similarity model trained successfully with matrix shape: {similarity_matrix.shape}'
                    )
                )
            else:
                self.stdout.write(self.style.ERROR('Failed to train cosine similarity model'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error training cosine similarity model: {str(e)}')
            )

    def train_kmeans_model(self, n_clusters=5):
        """Train K-Means clustering model"""
        self.stdout.write('Training K-Means clustering model...')
        
        # Check if we have enough games
        total_games = Game.objects.count()
        if total_games < 10:
            self.stdout.write(
                self.style.WARNING(
                    f'Not enough games for clustering. Found: {total_games}, minimum: 10'
                )
            )
            return
        
        try:
            # Initialize clustering engine
            n_clusters = min(n_clusters, total_games // 2)  # Don't create too many clusters
            clustering_engine = GameClusteringEngine(n_clusters=n_clusters)
            
            # Train the model
            cluster_labels = clustering_engine.fit()
            
            if len(cluster_labels) > 0:
                unique_clusters = len(set(cluster_labels))
                self.stdout.write(
                    self.style.SUCCESS(
                        f'K-Means model trained successfully with {unique_clusters} clusters'
                    )
                )
                
                if clustering_engine.silhouette_avg:
                    self.stdout.write(f'Silhouette Score: {clustering_engine.silhouette_avg:.3f}')
            else:
                self.stdout.write(self.style.ERROR('Failed to train K-Means model'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error training K-Means model: {str(e)}')
            )

    def create_demo_user(self):
        """Create a demo user for testing"""
        demo_user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User',
            }
        )
        
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS('Created demo user'))
        
        return demo_user
