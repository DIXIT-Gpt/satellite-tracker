from skyfield.api import load, wgs84

print("🛰️ ISS LIVE POSITION")
print("====================")

# Approximate Delhi location
latitude = 28.61
longitude = 77.23

ts = load.timescale()

satellites = load.tle_file(
    "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"
)

iss = next(s for s in satellites if "ISS" in s.name.upper())

observer = wgs84.latlon(latitude, longitude)

t = ts.now()

difference = iss - observer
alt, az, distance = difference.at(t).altaz()

print(f"\n🛰️ Satellite: {iss.name}")
print(f"📐 Altitude: {alt.degrees:.1f}°")
print(f"🧭 Direction: {az.degrees:.1f}°")
print(f"📏 Distance: {distance.km:.1f} km")

if alt.degrees > 0:
    print("\n👀 ISS IS ABOVE YOUR HORIZON!")
else:
    print("\n🌍 ISS is currently below your horizon.")
