from flask import Flask, render_template, redirect, request, session, url_for
from urllib.parse import urlencode
import joblib
from dotenv import load_dotenv
import os
# from utils import *

import requests

def get_featured_game_images():
    url = 'https://store.steampowered.com/api/featured/'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        games = data.get('large_capsules', []) + data.get('featured_win', [])
        game_images = [game['header_image'] for game in games[:10]]
        return game_images
    
    else:
        print("Failed to fetch featured games", flush=True)
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

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'my_super_secret_key')

STEAM_API_KEY = os.getenv('STEAM_API_KEY')
STEAM_OPENID_URL = 'https://steamcommunity.com/openid/login'

model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'svd_model.pkl')
model = joblib.load(model_path)


@app.route('/')
def home():
    top_games = [{'appid': 570, 'name': 'Dota 2', 'image': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/570/header.jpg?t=1724428927', 'tags': [{'id': '1', 'description': 'Action'}, {'id': '2', 'description': 'Strategy'}, {'id': '37', 'description': 'Free To Play'}]}, {'appid': 730, 'name': 'Counter-Strike 2', 'image': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/730/header.jpg?t=1719426374', 'tags': [{'id': '1', 'description': 'Action'}, {'id': '37', 'description': 'Free To Play'}]}, {'appid': 440, 'name': 'Team Fortress 2', 'image': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/440/header.jpg?t=1721932689', 'tags': [{'id': '1', 'description': 'Action'}, {'id': '37', 'description': 'Free To Play'}]}, {'appid': 271590, 'name': 'Grand Theft Auto V', 'image': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/271590/header.jpg?t=1720472998', 'tags': [{'id': '1', 'description': 'Action'}, {'id': '25', 'description': 'Adventure'}]}, {'appid': 578080, 'name': 'PUBG: BATTLEGROUNDS', 'image': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/578080/header.jpg?t=1720671886', 'tags': [{'id': '1', 'description': 'Action'}, {'id': '25', 'description': 'Adventure'}, {'id': '29', 'description': 'Massively Multiplayer'}, {'id': '37', 'description': 'Free To Play'}]}, {'appid': 1172470, 'name': 'Apex Legends™', 'image': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1172470/header.jpg?t=1723202302', 'tags': [{'id': '1', 'description': 'Action'}, {'id': '25', 'description': 'Adventure'}, {'id': '37', 'description': 'Free To Play'}]}, {'appid': 945360, 'name': 'Among Us', 'image': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/945360/header.jpg?t=1718741655', 'tags': [{'id': '4', 'description': 'Casual'}]}, {'appid': 252950, 'name': 'Rocket League®', 'image': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/252950/header.jpg?t=1717714777', 'tags': [{'id': '1', 'description': 'Action'}, {'id': '23', 'description': 'Indie'}, {'id': '9', 'description': 'Racing'}, {'id': '18', 'description': 'Sports'}]}, {'appid': 1085660, 'name': 'Destiny 2', 'image': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1085660/header.jpg?t=1720218333', 'tags': [{'id': '1', 'description': 'Action'}, {'id': '25', 'description': 'Adventure'}, {'id': '37', 'description': 'Free To Play'}]}, {'appid': 236850, 'name': 'Europa Universalis IV', 'image': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/236850/header.jpg?t=1720717509', 'tags': [{'id': '28', 'description': 'Simulation'}, {'id': '2', 'description': 'Strategy'}]}]
    featured_games = get_featured_game_images()
    return render_template('main.html', featured=featured_games, games=top_games)


@app.route('/analysis')
def analysis():
    return render_template('analysis.html')


@app.route('/login')
def login():
    return render_template('login.html')


# Valve Steam OpenID login (required by Steam API)
@app.route('/initiate_steam_login')
def initiate_steam_login():
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': url_for('after_login', _external=True),
        'openid.realm': request.host_url,
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }
    query_string = urlencode(params)
    login_url = f"{STEAM_OPENID_URL}?{query_string}"
    return redirect(login_url)


@app.route('/after_login')
def after_login():
    # Extract Steam ID from the OpenID response
    steam_id = request.args.get('openid.claimed_id').split('/')[-1]
    session['steam_id'] = steam_id
    
    # Fetch the user's Steam profile information, including their username
    user_info = get_user_info(steam_id, STEAM_API_KEY)
    if user_info:
        session['username'] = user_info.get('personaname') 
        session['avatar'] = user_info.get('avatarfull')

    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    if 'steam_id' not in session:
        return redirect(url_for('login'))

    steam_id = session['steam_id']
    games = get_owned_games(steam_id, STEAM_API_KEY)

    if not games:
        return render_template('profile.html', message="No games found for this user.")

    return render_template('profile.html', games=games)

@app.route('/recommendations')
def recommendations():
    if 'steam_id' not in session:
        return redirect(url_for('login'))

    steam_id = session['steam_id']
    owned_games = get_owned_games(steam_id, STEAM_API_KEY)

    if not owned_games:
        return render_template('recommendations.html', message="No games found for this user.")

    all_games = fetch_all_games()

    owned_game_ids = {game['appid'] for game in owned_games}
    predicted_ratings = []
 
    for game in all_games:
        appid = game['appid']
        if appid in owned_game_ids:
            continue
        
        prediction = model.predict(uid=steam_id, iid=appid)
        predicted_ratings.append((appid, prediction.est))

    top_20_games = sorted(predicted_ratings, key=lambda x: x[1], reverse=True)[:20]
    top_20_game_ids = [game[0] for game in top_20_games]

    recommended_games = fetch_game_details(top_20_game_ids)
    recommended_games_with_ratings = [
        {'game': game, 'rating': next(rating for id, rating in top_20_games if id == game['appid'])}
        for game in recommended_games
    ]

    return render_template('recommendations.html', recommended_games=recommended_games_with_ratings)


@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
