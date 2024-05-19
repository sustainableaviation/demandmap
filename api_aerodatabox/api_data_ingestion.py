import os
import requests
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import toml

# Define paths
current_directory = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(current_directory, "API_Key/config.toml")
airport_path = os.path.join(current_directory, "airport_data/available_airports")
connection_data_directory = os.path.join(current_directory, "connection_data")


# Function to get the API key from the config file
def get_api_key():
    try:
        with open(file_path, "r") as config_file:
            config = toml.load(config_file)
            return config["api"]["key"]
    except FileNotFoundError:
        print("Config file not found!")
        return None
    except KeyError:
        print("API key not found in config file!")
        return None


api_key = get_api_key()


def get_api_key():
    try:
        with open(config_path, "r") as config_file:
            config = toml.load(config_file)
            return config["api"]["key"]
    except FileNotFoundError:
        print("Config file not found!")
        return None
    except KeyError:
        print("API key not found in config file!")
        return None


api_key = get_api_key()

if api_key is None:
    print("Exiting program due to missing API key.")
    exit()

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}

# Define the airports_info directory
airports_info_directory = current_directory / "airport_data/airports_detail_data"

# Check if the airports_info directory already exists
if airports_info_directory.exists():
    print(f"The directory 'airports_detail_data' already exists at {airports_info_directory}. Exiting program.")
    exit()

# Create the airports_info directory since it does not exist
airports_info_directory.mkdir(parents=True)

# Read the JSON file containing ICAO codes
json_file_path = current_directory / "airport_data/available_airports.json"
with open(json_file_path, 'r') as f:
    airports_icao = json.load(f)

# Fetch data from the API and write to JSON files
for icao in airports_icao['items']:
    url = f"https://aerodatabox.p.rapidapi.com/airports/icao/{icao}"
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        file_path = airports_info_directory / f"{icao}.json"

        # Write the JSON response to a file
        with open(file_path, "w") as file:
            file.write(response.text)
        print("JSON data saved to:", file_path)
    else:
        print("Failed to retrieve data from the API:", response.status_code)

    # Delay for 0.6 seconds to avoid hitting the rate limit
    time.sleep(0.6)



# Function to get airport routes for a specific ICAO code and date
def get_airport_routes(icao_code, date):
    url = f"https://aerodatabox.p.rapidapi.com/airports/icao/{icao_code}/stats/routes/daily/{date}"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None


# Function to create a folder for each month within the Connection_Data directory
def create_month_folder(base_directory, month):
    folder_name = month.strftime("%m-%B")
    month_folder_path = os.path.join(base_directory, folder_name)
    if not os.path.exists(month_folder_path):
        os.makedirs(month_folder_path)
    return month_folder_path


# Ensure the 'Connection_Data' directory exists
if not os.path.exists(connection_data_directory):
    os.makedirs(connection_data_directory)

""" Read the airport ICAO codes from the "Airports.json" file
This function requires a file called Airports.json from the Healthcheck.py
"""
with open(airport_path, "r") as airports_file:
    airports_dataset = json.load(airports_file)

# Define date range
start_date = datetime(year=2023, month=5, day=7)
end_date = datetime(year=2024, month=5, day=7)

# Retrieve and save data
while start_date <= end_date:
    month_folder = create_month_folder(connection_data_directory, start_date)
    date_str = start_date.strftime("%Y-%m-%d")
    print(f"Retrieving data for {date_str}...")
    for airport_icao in airports_dataset["items"]:
        airport_routes = get_airport_routes(airport_icao, date_str)
        if airport_routes:
            file_path = os.path.join(month_folder, f"{airport_icao}.json")
            with open(file_path, "w") as json_file:
                json.dump(airport_routes, json_file)
            print(f"Data for airport {airport_icao} saved successfully.")
        else:
            print(f"Failed to retrieve data for airport {airport_icao}.")
    start_date += relativedelta(months=1)
    start_date = start_date.replace(day=7)