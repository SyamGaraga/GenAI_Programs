import requests
import datetime
import chromadb
import json

# ------------------------------------------
# 1️⃣ CONFIG
# ------------------------------------------
STATES = {
    "Tamil Nadu": (13.0827, 80.2707),
    "Kerala": (10.8505, 76.2711),
    "Karnataka": (12.9716, 77.5946),
    "Maharashtra": (19.8762, 75.3433),
    "Gujarat": (22.2587, 71.1924),
    "Delhi": (28.7041, 77.1025)
}

API_URL = "https://api.open-meteo.com/v1/forecast"
TODAY = str(datetime.date.today())

# Initialize ChromaDB
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="temperature_data")


# ------------------------------------------
# 2️⃣ FETCH TEMPERATURE FUNCTION
# ------------------------------------------
def get_temperature(lat, lon, state):
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        }
        response = requests.get(API_URL, params=params, timeout=10)
        data = response.json()

        temp = data["current_weather"]["temperature"]
        print(f"{state}: {temp}°C")
        return temp

    except Exception as e:
        print(f"❌ Error fetching temperature for {state}: {e}")
        return None


# ------------------------------------------
# 3️⃣ CREATE METADATA FUNCTION
# ------------------------------------------
def generate_metadata(state, temp):
    """Simple local metadata (NO API USED)."""
    if temp >= 35:
        condition = "Hot"
    elif temp >= 20:
        condition = "Normal"
    else:
        condition = "Cold"

    return {
        "state": state,
        "temperature": temp,
        "condition": condition,
        "date": TODAY
    }


# ------------------------------------------
# 4️⃣ FETCH DATA & SAVE TO TXT
# ------------------------------------------
file_data = {}

for state, (lat, lon) in STATES.items():
    temp = get_temperature(lat, lon, state)

    if temp is None:
        continue

    file_data[state] = temp

# Save temperatures into a text file
with open("temperature.txt", "w") as f:
    for state, temp in file_data.items():
        f.write(f"{state}: {temp}°C\n")

print("\n📄 Saved data to temperature.txt")


# ------------------------------------------
# 5️⃣ STORE IN CHROMADB
# ------------------------------------------
documents, metadatas, ids = [], [], []

for state, temp in file_data.items():
    desc = f"Today's temperature in {state} is {temp}°C."
    meta = generate_metadata(state, temp)

    documents.append(desc)
    metadatas.append(meta)
    ids.append(f"{state}-{TODAY}")

collection.add(documents=documents, metadatas=metadatas, ids=ids)

print("\n✅ Temperature data stored successfully!\n")


# ------------------------------------------
# 6️⃣ DAILY REPORT
# ------------------------------------------
def generate_report():
    print(f"\n📊 Daily Temperature Report — {TODAY}\n")
    
    all_data = collection.get(include=["metadatas"])

    today_data = [m for m in all_data["metadatas"] if m["date"] == TODAY]

    if not today_data:
        print("No data found for today.")
        return

    # sort by temp
    today_data_sorted = sorted(today_data, key=lambda x: x["temperature"], reverse=True)

    highest = today_data_sorted[0]
    lowest = today_data_sorted[-1]
    mid = today_data_sorted[len(today_data_sorted)//2]

    print(f"🔥 Highest: {highest['state']} ({highest['temperature']}°C — {highest['condition']})")
    print(f"🌤️ Medium: {mid['state']} ({mid['temperature']}°C — {mid['condition']})")
    print(f"❄️ Lowest: {lowest['state']} ({lowest['temperature']}°C — {lowest['condition']})")

    print("\n----------------------------------------")


# Run Report
generate_report()
