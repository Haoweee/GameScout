import requests

def get_featured_game_images():
    url = 'https://store.steampowered.com/api/featured/'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        game_images = [game['header_image'] for game in data['featured_win']]
        return game_images
    else:
        print("Failed to fetch featured games")
        return None


def fetch_top_games():
    SPECIFIC_GAME_IDS = [
        570,        # Dota 2
        730,        # Counter-Strike: Global Offensive
        440,        # Team Fortress 2
        271590,     # Grand Theft Auto V
        578080,     # PUBG: BATTLEGROUNDS
        1172470,    # Apex Legends
        945360,     # Among Us
        252950,     # Rocket League
        1085660,    # Destiny 2
        236850,     # Europa Universalis IV
    ]

    top_games = fetch_game_details(SPECIFIC_GAME_IDS)
    
    return top_games[:10]


def get_owned_games(steamid, api_key):
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steamid}&format=json&include_appinfo=1&include_played_free_games=1'
    response = requests.get(url)

    if response.status_code == 200:
        games = response.json().get('response', {}).get('games', [])
        for game in games:
            game['playtime_forever'] = round(game['playtime_forever'] / 60, 2)
        
        games.sort(key=lambda x: x['name'].lower())        
        return games
    return []


def get_user_info(steamid, api_key):
    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steamid}'
    response = requests.get(url)
    if response.status_code == 200:
        player_info = response.json().get('response', {}).get('players', [])
        if player_info:
            return player_info[0]
    return None


def fetch_game_details(game_ids):
    game_details = []
    
    for appid in game_ids:
        url = f'https://store.steampowered.com/api/appdetails?appids={appid}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if str(appid) in data and data[str(appid)]['success']:
                game_info = data[str(appid)]['data']
                game_details.append({
                    'appid': appid,
                    'name': game_info.get('name', 'N/A'),
                    'image': game_info.get('header_image', 'N/A'),
                    'tags': game_info.get('genres', [])  # Assuming tags are in 'genres'
                })
        else:
            print(f"Failed to fetch details for game {appid}")
    print(game_details)
    return game_details


def fetch_all_games():
    url = 'http://api.steampowered.com/ISteamApps/GetAppList/v2/'
    response = requests.get(url)

    if response.status_code != 200:
        print("Error fetching game list from Steam API")
        return []

    data = response.json()
    apps = data.get('applist', {}).get('apps', [])
    games = [{'appid': app['appid'], 'name': app['name']} for app in apps]

    return games