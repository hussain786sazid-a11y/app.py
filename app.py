from flask import Flask, render_template, request, session, redirect, url_for
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super-secret-key-weather-app-2025'  # Strong secret key
app.config['SESSION_TYPE'] = 'filesystem'
import os
API_KEY =os.environ.get("b4f909954fe4af4facd8a868017f0db7")

@app.route('/')
def home():
    # Debug: Print session contents
    print("Session data:", dict(session))
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    city = request.form.get('city')
    
    if not city:
        return render_template('error.html', message="Please enter a city name!")
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            weather_info = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temp': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            }
            
            # Search History - Initialize if needed
            if 'search_history' not in session:
                session['search_history'] = []
            
            # Add to history (avoid duplicates)
            history = session['search_history']
            if data['name'] in history:
                history.remove(data['name'])
            history.insert(0, data['name'])
            session['search_history'] = history[:5]  # Keep only last 5
            
            # Mark session as modified
            session.modified = True
            
            print("Updated history:", session['search_history'])  # Debug
            
            return render_template('weather.html', weather=weather_info)
        else:
            return render_template('error.html', message="City not found!")
    except Exception as e:
        print("Error:", e)  # Debug
        return render_template('error.html', message="Network error!")

@app.route('/forecast', methods=['POST'])
def forecast():
    city = request.form.get('city')
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            forecast_list = []
            for i in range(0, 40, 8):
                if i < len(data['list']):
                    item = data['list'][i]
                    forecast_list.append({
                        'date': item['dt_txt'].split(' ')[0],
                        'temp': item['main']['temp'],
                        'description': item['weather'][0]['description'],
                        'humidity': item['main']['humidity'],
                        'wind_speed': item['wind']['speed']
                    })
            
            return render_template('forecast.html', city=city, forecasts=forecast_list)
        else:
            return render_template('error.html', message="City not found!")
    except:
        return render_template('error.html', message="Network error!")

@app.route('/add_favorite', methods=['GET', 'POST'])
def add_favorite():
    if request.method == 'POST':
        city = request.form.get('city')
    else:
        city = request.args.get('city')
    
    if not city:
        return redirect(url_for('home'))
    
    # Initialize favorites if not exists
    if 'favorites' not in session:
        session['favorites'] = []
    
    favorites = session['favorites']
    
    # Add city if not already in favorites
    if city not in favorites and len(favorites) < 5:
        favorites.append(city)
        session['favorites'] = favorites
        session.modified = True
        print("Added to favorites:", city)  # Debug
        print("Current favorites:", session['favorites'])  # Debug
    
    return redirect(url_for('home'))

@app.route('/remove_favorite/<city>')
def remove_favorite(city):
    if 'favorites' in session:
        favorites = session['favorites']
        if city in favorites:
            favorites.remove(city)
            session['favorites'] = favorites
            session.modified = True
            print("Removed from favorites:", city)  # Debug
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()