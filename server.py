from http.server import SimpleHTTPRequestHandler, HTTPServer
from skyfield.api import load, wgs84
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
import tempfile
import os
import json


print("🛰️ SATELLITE TRACKER")
print("====================")
print("Downloading satellite data...")

ts = load.timescale()


# --------------------------------------------------
# Download a TLE group without leaving gp.php files
# --------------------------------------------------

def download_group(url):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.close()

    try:
        with urlopen(url, timeout=30) as response:
            data = response.read()

        with open(temp.name, "wb") as file:
            file.write(data)

        satellites = load.tle_file(temp.name, reload=True)

        return satellites

    finally:
        try:
            os.remove(temp.name)
        except:
            pass


# --------------------------------------------------
# Load satellite groups
# --------------------------------------------------

groups = [
    (
        "stations",
        "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"
    ),
    (
        "weather",
        "https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle"
    ),
    (
        "gps-ops",
        "https://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle"
    ),
]


all_satellites = []

for group_name, url in groups:

    try:
        satellites = download_group(url)

        print(f"✅ {group_name}: {len(satellites)} satellites")

        all_satellites.extend(satellites)

    except Exception as error:
        print(f"⚠️ Could not load {group_name}: {error}")


# --------------------------------------------------
# Remove duplicate satellite names
# --------------------------------------------------

satellite_map = {}

for satellite in all_satellites:
    satellite_map[satellite.name] = satellite


# --------------------------------------------------
# Pick useful satellites
# --------------------------------------------------

wanted_keywords = [
    "ISS",
    "ZARYA",
    "TIANHE",
    "TIANGONG",
    "CSS",
    "HST",
    "HUBBLE",
    "NOAA",
    "METEOR",
    "GOES",
    "GPS",
]


selected = []

for name, satellite in satellite_map.items():

    upper_name = name.upper()

    if any(keyword in upper_name for keyword in wanted_keywords):

        if satellite not in selected:
            selected.append(satellite)


# Add a few GPS satellites if available
gps_count = 0

for name, satellite in satellite_map.items():

    if "GPS" in name.upper():

        if satellite not in selected:
            selected.append(satellite)
            gps_count += 1

        if gps_count >= 8:
            break


# Keep the app fast
selected = selected[:30]


print(f"\n🛰️ Tracking {len(selected)} satellites:")

for satellite in selected:
    print("   •", satellite.name)


# --------------------------------------------------
# Find ISS
# --------------------------------------------------

iss = None

for satellite in selected:

    if "ISS" in satellite.name.upper():
        iss = satellite
        break


class Handler(SimpleHTTPRequestHandler):

    def do_GET(self):

        parsed = urlparse(self.path)

        # --------------------------------------------------
        # Satellite API
        # --------------------------------------------------

        if parsed.path == "/api/satellites":

            try:

                params = parse_qs(parsed.query)

                latitude = float(
                    params.get("lat", ["28.61"])[0]
                )

                longitude = float(
                    params.get("lon", ["77.23"])[0]
                )

                observer = wgs84.latlon(
                    latitude,
                    longitude
                )

                t = ts.now()

                results = []

                for satellite in selected:

                    try:

                        difference = satellite - observer

                        alt, az, distance = difference.at(t).altaz()

                        altitude = float(alt.degrees)
                        direction = float(az.degrees)
                        distance_km = float(distance.km)

                        visible = altitude > 0

                        results.append({
                            "name": satellite.name,
                            "altitude": round(altitude, 1),
                            "direction": round(direction, 1),
                            "distance": round(distance_km, 1),
                            "visible": visible
                        })

                    except Exception as error:

                        print(
                            f"Satellite error {satellite.name}:",
                            error
                        )


                data = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "satellites": results
                }

                response = json.dumps(data).encode()

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    "application/json"
                )

                self.send_header(
                    "Access-Control-Allow-Origin",
                    "*"
                )

                self.send_header(
                    "Cache-Control",
                    "no-store"
                )

                self.send_header(
                    "Content-Length",
                    str(len(response))
                )

                self.end_headers()

                self.wfile.write(response)

                return


            except Exception as error:

                response = json.dumps({
                    "error": str(error)
                }).encode()

                self.send_response(500)

                self.send_header(
                    "Content-Type",
                    "application/json"
                )

                self.send_header(
                    "Content-Length",
                    str(len(response))
                )

                self.end_headers()

                self.wfile.write(response)

                return


        # --------------------------------------------------
        # Normal website files
        # --------------------------------------------------

        super().do_GET()


# --------------------------------------------------
# Start server
# --------------------------------------------------

server = HTTPServer(
    ("0.0.0.0", 8080),
    Handler
)

print("\n============================")
print("✅ SERVER READY")
print("============================")
print()
print("Open this in your browser:")
print()
print("http://127.0.0.1:8080/web/")
print()
print("Auto-updating every 1 second.")
print("============================")


server.serve_forever()
