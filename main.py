import create_html
import parsing

import os
import json
import csv

print("=== debrief ===")

# Check if required libraries are installed
required_libraries = [
    "csv", "json", "requests", "bs4", "urllib", "feedparser", "ast", "re", "time", "google"
]

missing_libraries = []
for lib in required_libraries:
    try:
        __import__(lib)
    except ImportError:
        missing_libraries.append(lib)

if missing_libraries:
    print(f"Missing required libraries: {', '.join(missing_libraries)}")
    print("Please install them using pip:")
    for lib in missing_libraries:
        print(f"pip install {lib}")
    exit(1)

# Default settings
DEFAULT_SETTINGS = {
    "model": "gemini-2.0-flash-lite",
    "batch_size": 20,
    "input_file": "rss_sources.txt",
    "output_file": "results.csv",
    "google_api_key": "",
    "interests": "",
    "preview_sites": "yes",
    "theme": "aero.css"
}

# Check if settings.json exists, create it if not
if not os.path.exists("settings.json"):
    print("settings.json not found. Creating it with default values...")
    with open("settings.json", "w") as f:
        json.dump(DEFAULT_SETTINGS, f, indent=4)
else:
    print("settings.json already exists.")

# Load settings
with open("settings.json", "r") as f:
    settings = json.load(f)

# Check if Google API key is blank
if not settings["google_api_key"]:
    print("Google API key is missing.")
    print("Please get an API key from https://aistudio.google.com/apikey")
    api_key = input("Enter your Google API key: ").strip()
    if api_key:
        settings["google_api_key"] = api_key
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        print("Google API key saved.")
    else:
        print("No API key provided. Exiting.")
        exit(1)

# Present settings to the user
print("\nCurrent Settings:")
for key, value in settings.items():
    if key == "google_api_key":
        print(f"{key}: {'*' * 12} (WARNING: Never share your API key)")
    else:
        print(f"{key}: {value}")

# Ask if the user wants to change settings
change_settings = input("\nDo you want to change any settings? (yes/no): ").strip().lower()
if change_settings == "yes":
    for key in settings:
        new_value = input(f"Enter new value for {key} (leave blank to keep current): ").strip()
        if new_value:
            settings[key] = new_value
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)
    print("Settings updated.")

# Check if results.csv exists
output_file = settings["output_file"]
if os.path.exists(output_file):
    fetch_new = input(f"{output_file} already exists. Do you want to fetch and rate new stories? (yes/no): ").strip().lower()
    if fetch_new != "yes":
        print("Exiting.")
        exit(0)
else:
    print(f"{output_file} not found. Fetching will begin.")

# Placeholder functions for parsing and HTML creation
def parse_and_rate():
    print("Running parse_and_rate()...")
    # Implement your parsing and rating logic here
    pass

def build_html():
    print("Running build_html()...")
    # Implement your HTML creation logic here
    pass

# Run the functions
parsing.parse_and_rate()
create_html.build_html()
