from flask import Flask, render_template, request, redirect, url_for
import requests
from geopy.geocoders import Nominatim
from plotly.offline import plot
import plotly.graph_objs as go

app = Flask(__name__)

# OpenWeatherMap API key
API_KEY = "735d8eef6142ce3d8528dea2ed98f789"

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/features')
def news():
    return render_template('features.html')
@app.route('/download')
def indx():
    return render_template('download.html')

@app.route('/fetch_coordinates', methods=['POST'])
def fetch_coordinates():
    if request.method == 'POST':
        location = request.form['location']
        geolocator = Nominatim(user_agent="GetLoc")
        location_data = geolocator.geocode(location)
        if location_data:
            latitude = location_data.latitude
            longitude = location_data.longitude
            return redirect(url_for('get_weather', lat=latitude, lon=longitude))
        else:
            return "Location not found."

@app.route('/review')
def get_weather():
    # Coordinates of the location
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    # Fetch weather data from OpenWeatherMap API
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()

    # Fetch air pollution data from OpenWeatherMap API
    pollution_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    pollution_response = requests.get(pollution_url)
    pollution_data = pollution_response.json()

    # Create weather plot
    weather_plot = create_plot(weather_data, 'Weather Data')

    # Create pollution plot
    pollution_plot = create_plot(pollution_data, 'Air Pollution Data')
    

    return render_template('weather.html', weather_plot=weather_plot, pollution_plot=pollution_plot)

# 


def create_plot(data, title):
    if 'main' in data:  # Weather data
        # Extract weather parameters
        temp_kelvin = data['main']['temp']
        temp_celsius = temp_kelvin - 273.15
        temp_fahrenheit = (temp_celsius * 9/5) + 32
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        cloud_coverage = data['clouds']['all']
        
        # Define keys and values for plotting
        keys = ['Temperature (Celsius)', 'Temperature (Fahrenheit)', 'Humidity', 'Wind Speed', 'Cloud Coverage']
        values = [temp_celsius, temp_fahrenheit, humidity, wind_speed, cloud_coverage]
        
        pollution_status = "No Pollution"  # Assume no pollution for weather data
    elif 'list' in data and 'main' in data['list'][0]:  # Air quality data
        # Extract air quality parameters
        keys = ['AQI', 'CO', 'NO', 'NO2', 'O3', 'SO2', 'PM2.5', 'PM10', 'NH3']
        values = [data['list'][0]['main']['aqi'], data['list'][0]['components']['co'], 
                  data['list'][0]['components']['no'], data['list'][0]['components']['no2'],
                  data['list'][0]['components']['o3'], data['list'][0]['components']['so2'],
                  data['list'][0]['components']['pm2_5'], data['list'][0]['components']['pm10'],
                  data['list'][0]['components']['nh3']]
        components = [
    data['list'][0]['components']['co'],
    data['list'][0]['components']['no'],
    data['list'][0]['components']['no2'],
    data['list'][0]['components']['o3'],
    data['list'][0]['components']['so2'],
    data['list'][0]['components']['pm2_5'],
    data['list'][0]['components']['pm10'],
    data['list'][0]['components']['nh3']
]

                # Calculate the average of the component values
        average_value = sum(components) / len(components)

                # Define a threshold for the average value
        threshold = 50  # Adjust the threshold as needed

                # Check if the average value exceeds the threshold
        pollution_present = average_value > threshold
        pollution_status = "Polluted" if pollution_present else "Negligible Pollution"
        print("Pollution Status:", pollution_status)  # Print whether pollution is present or not

        # Set thresholds for each parameter
     
    else:
        raise ValueError("Invalid data format")

    # Create plotly bar chart
    plot_data = [go.Bar(x=keys, y=values, marker_color='skyblue')]
    layout = go.Layout(title=title, xaxis_title='Parameters', yaxis_title='Values')
    fig = go.Figure(data=plot_data, layout=layout)

    # Convert plot to HTML
    plot_html = plot(fig, include_plotlyjs=False, output_type='div')

    return plot_html, pollution_status

if __name__ == '__main__':
    app.run(debug=True)
