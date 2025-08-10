import requests
import logging

logger = logging.getLogger(__name__)

def get_game_screenshots(game_name, api_key="ead7e838d51f4f5987a7427e8883e185"):
    """
    Mendapatkan screenshot gameplay dari RAWG API
    Returns: list of screenshot URLs (maksimal 4)
    """
    try:
        # Search game first
        search_response = requests.get(
            "https://api.rawg.io/api/games",
            params={
                'key': api_key,
                'search': game_name,
                'page_size': 1
            },
            timeout=10
        )
        
        if search_response.status_code != 200:
            logger.warning(f"Failed to search game {game_name}: {search_response.status_code}")
            return []
            
        search_data = search_response.json()
        
        if not search_data.get('results'):
            logger.warning(f"No results found for game: {game_name}")
            return []
            
        game_id = search_data['results'][0]['id']
        
        # Get screenshots for the game
        screenshots_response = requests.get(
            f"https://api.rawg.io/api/games/{game_id}/screenshots",
            params={'key': api_key},
            timeout=10
        )
        
        if screenshots_response.status_code != 200:
            logger.warning(f"Failed to get screenshots for {game_name}: {screenshots_response.status_code}")
            return []
            
        screenshots_data = screenshots_response.json()
        
        # Extract screenshot URLs (maksimal 4)
        screenshots = []
        for screenshot in screenshots_data.get('results', [])[:4]:
            if screenshot.get('image'):
                screenshots.append(screenshot['image'])
                
        return screenshots
        
    except Exception as e:
        logger.error(f"Error getting screenshots for {game_name}: {str(e)}")
        return []

def get_fallback_screenshots(game_name):
    """
    Fallback screenshots dengan placeholder yang lebih menarik
    """
    colors = ['4a90e2', '7b68ee', '32cd32', 'ff6347']
    screenshots = []
    
    for i, color in enumerate(colors, 1):
        url = f"https://via.placeholder.com/600x400/{color}/ffffff?text={game_name[:10]}+Gameplay+{i}"
        screenshots.append(url)
    
    return screenshots
