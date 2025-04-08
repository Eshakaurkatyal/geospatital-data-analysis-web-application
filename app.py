from flask import Flask, render_template, request
from database_config import get_db_connection
import math

app = Flask(__name__)

# Function to calculate distance using Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c  # Distance in km

# Function to calculate distance from equator
def distance_from_equator(latitude):
    return abs(latitude) * 111  # 1° latitude ≈ 111 km

# Function for stereographic projection calculations
def stereographic_projection(lat, lon):
    R = 6371  # Earth's radius in km
    x = R * math.cos(math.radians(lat)) * math.sin(math.radians(lon))
    y = R * math.sin(math.radians(lat))
    return round(x, 2), round(y, 2)

# Function to calculate solar angle based on latitude
def solar_angle(latitude):
    declination = 23.44  # Earth's axial tilt
    return round(90 - abs(latitude - declination), 2)

# Route 1: Homepage - User enters coordinates
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        lat = float(request.form["latitude"])
        lon = float(request.form["longitude"])
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch the continent from `locations`
        cursor.execute("SELECT name FROM locations WHERE latitude=%s AND longitude=%s", (lat, lon))
        continent = cursor.fetchone()
        conn.close()

        if continent:
            continent_name = continent["name"].lower().replace(" ", "_")
            return render_template("country.html", continent=continent_name)
        else:
            return "Continent not found."

    return render_template("index.html")

# Route 2: Select a Country from the Continent
@app.route("/countries/<continent>", methods=["GET", "POST"])
def countries(continent):
    valid_continents = ["asia", "europe", "africa", "north_america", "south_america"]

    if continent not in valid_continents:
        return render_template("calculations.html", country=None)

    table_name = f"{continent}_countries"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch country list
    cursor.execute(f"SELECT id, country_name FROM {table_name}")
    countries = cursor.fetchall()
    conn.close()

    country_details = None  # Initialize the country details variable to None

    if request.method == "POST":
        country_id = request.form["country"]
        
        # Reconnect to the database to fetch the country details
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch details of the selected country by its ID
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", (country_id,))
        country_details = cursor.fetchone()
        conn.close()

        # Handle the case where latitude/longitude is missing and display an error message if so
        if country_details and (country_details['latitude'] is None or country_details['longitude'] is None):
            return render_template("error.html", message="Latitude or Longitude is missing for the selected country.")

        return render_template("calculations.html", country=country_details)

    return render_template("details.html", continent=continent, countries=countries)

# Route 3: Perform Calculations
@app.route("/calculate", methods=["POST"])
def calculate():
    country_name = request.form["country_name"]
    latitude = float(request.form["latitude"])
    longitude = float(request.form["longitude"])
    calculation_type = request.form["calculation"]

    result = None

    if calculation_type == "distance_equator":
        result = f"Distance from the Equator: {distance_from_equator(latitude)} km"
    elif calculation_type == "stereographic_projection":
        x, y = stereographic_projection(latitude, longitude)
        result = f"Stereographic Projection: (X: {x}, Y: {y})"
    elif calculation_type == "solar_angle":
        result = f"Solar Angle: {solar_angle(latitude)}°"
    elif calculation_type == "quit":
        return "Thank you for using the system!"

    return render_template("result.html", country=country_name, result=result)
@app.route("/quit", methods=["GET"])
def quit():
    return "Thank you for using the system!"


if __name__ == "__main__":
    app.run(debug=True)
