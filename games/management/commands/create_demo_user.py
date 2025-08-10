from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a demo user for testing'

    def handle(self, *args, **options):
        username = 'demo'
        password = 'demo123'
        email = 'demo@example.com'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists')
            )
        else:
            User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            self.stdout.write(
                self.style.SUCCESS(f'Demo user created successfully!')
            )
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Password: {password}')
