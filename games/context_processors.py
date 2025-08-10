from .models import Platform, Genre

def all_platforms(request):
    """
    Makes a list of all Platform objects available to all templates.
    """
    return {
        'all_platforms': Platform.objects.all().order_by('name'),
        'all_genres': Genre.objects.all().order_by('name')
    }
