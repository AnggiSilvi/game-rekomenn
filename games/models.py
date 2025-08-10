from django.db import models

# Model-model kecil untuk relasi data
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Platform(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(max_length=50, blank=True)
    def __str__(self): return self.name

class Publisher(models.Model):
    name = models.CharField(max_length=150, unique=True)
    def __str__(self): return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

# Model Utama untuk Game
class Game(models.Model):
    name = models.CharField(max_length=255)
    released = models.DateField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    metacritic = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cover_image_url = models.URLField(max_length=500, null=True, blank=True, default='https://via.placeholder.com/250x350.png?text=No+Image')
    esrb = models.CharField(max_length=10, null=True, blank=True)
    store_url = models.JSONField(null=True, blank=True, default=dict)

    genres = models.ManyToManyField(Genre, blank=True)
    platforms = models.ManyToManyField(Platform, blank=True)
    publishers = models.ManyToManyField(Publisher, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    popularity_score = models.FloatField(default=0.0)
    content_vector = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_content_features(self):
        """Return content features untuk content-based filtering"""
        features = {
            'genres': list(self.genres.values_list('name', flat=True)),
            'platforms': list(self.platforms.values_list('name', flat=True)),
            'publishers': list(self.publishers.values_list('name', flat=True)),
            'tags': list(self.tags.values_list('name', flat=True)),
            'rating': self.rating or 0,
            'metacritic': self.metacritic or 0,
        }
        return features

# Model untuk Similarity antar Game
class GameSimilarity(models.Model):
    game1 = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='similarity_from')
    game2 = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='similarity_to')
    content_similarity = models.FloatField(default=0.0)
    collaborative_similarity = models.FloatField(default=0.0)
    hybrid_similarity = models.FloatField(default=0.0)
    last_calculated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('game1', 'game2')

    def __str__(self):
        return f"Similarity: {self.game1.name} - {self.game2.name}"
