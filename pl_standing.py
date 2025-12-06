import requests
import pandas as pd
import logging
import os
from sqlalchemy import create_engine, inspect, text
import urllib.parse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------------------------------------------------------------
# CONFIGURE LOGGING
# -------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# -------------------------------------------------------------
# 1. EXTRACT JSON FROM FOOTBALL API
# -------------------------------------------------------------
def extract_json(response):
    if response.status_code != 200:
        logging.error(f"API request failed with status code: {response.status_code}")
        logging.debug(f"Response: {response.text}")
        return None
        
    try:
        data = response.json()
        if 'standings' not in data or not data['standings']:
            logging.error("'standings' key missing in data.")
            return None
        team_table = data['standings'][0]['table']
        logging.info(f"Extracted {len(team_table)} teams.")
        return team_table
    except Exception as e:
        logging.error(f"JSON parsing error: {e}", exc_info=True)
        return None

# -------------------------------------------------------------
# 2. TRANSFORM JSON → DATAFRAME
# -------------------------------------------------------------
def transform_standings(team_table):
    flat_data = []
    for team in team_table:
        team_row = {
            'position': team['position'],
            'team_name': team['team']['name'],
            'points': team['points'],
            'playedGames': team['playedGames'],
            'won': team['won'],
            'draw': team['draw'],
            'lost': team['lost'],
            'goals_for': team['goalsFor'],
            'goals_against': team['goalsAgainst'],
            'goal_difference': team['goalDifference']
        }
        flat_data.append(team_row)
    df_standings = pd.DataFrame(flat_data)
    logging.info("Transformed JSON to DataFrame.")
    return df_standings

# -------------------------------------------------------------
# 3. SAVE DATAFRAME TO CSV
# -------------------------------------------------------------
def save_to_csv(df, filename="pl_standings.csv"):
    try:
        df.to_csv(filename, index=False)
        logging.info(f"Successfully saved DataFrame to '{filename}'")
        return filename
    except Exception as e:
        logging.error(f"Failed to save CSV: {e}", exc_info=True)
        return None

# -------------------------------------------------------------
# 4. LOAD CSV TO MYSQL (WITH DUPLICATE PREVENTION)
# -------------------------------------------------------------
def csv_to_mysql(csv_file):
    # Get credentials from environment variables
    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DATABASE", "mydatabase")
    table_name = os.getenv("MYSQL_TABLE", "pl_standings")

    # Validate required environment variables
    if not password:
        logging.error("MYSQL_PASSWORD not found in environment variables!")
        return

    encoded_password = urllib.parse.quote_plus(password)
    database_url = f"mysql+mysqlconnector://{user}:{encoded_password}@{host}/{database}"

    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        logging.info(f"Read {len(df)} rows from '{csv_file}'")
        
        # Create engine
        engine = create_engine(database_url)
        inspector = inspect(engine)

        # If table does not exist, create it with proper schema
        if not inspector.has_table(table_name):
            # Create table with primary key to prevent duplicates
            with engine.begin() as conn:
                create_table_sql = text(f"""
                    CREATE TABLE `{table_name}` (
                        position INT,
                        team_name VARCHAR(255) PRIMARY KEY,
                        points INT,
                        playedGames INT,
                        won INT,
                        draw INT,
                        lost INT,
                        goals_for INT,
                        goals_against INT,
                        goal_difference INT
                    )
                """)
                conn.execute(create_table_sql)
            logging.info(f"Table '{table_name}' created with primary key on team_name.")
        
        # Clear existing data before inserting new data
        with engine.begin() as conn:
            delete_sql = text(f"DELETE FROM `{table_name}`")
            conn.execute(delete_sql)
            logging.info(f"Cleared existing data from '{table_name}'.")
        
        # Load new data
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        logging.info(f"Successfully loaded {len(df)} rows to MySQL table '{table_name}'.")

    except FileNotFoundError:
        logging.error(f"CSV file '{csv_file}' not found.")
    except ImportError as ie:
        logging.error(f"Missing required library: {ie}")
    except Exception as e:
        logging.error(f"Database operation error: {e}", exc_info=True)

# -------------------------------------------------------------
# 5. MAIN PROGRAM
# -------------------------------------------------------------
def main():
    # Get API credentials from environment variables
    api_token = os.getenv("FOOTBALL_API_TOKEN")
    
    # Validate API token
    if not api_token:
        logging.error("FOOTBALL_API_TOKEN not found in environment variables!")
        logging.error("Please create a .env file with your API token.")
        return

    uri = "https://api.football-data.org/v4/competitions/PL/standings"
    headers = {"X-Auth-Token": api_token}

    # Step 1: Fetch data from API
    logging.info("Step 1: Fetching data from Football API...")
    try:
        response = requests.get(uri, headers=headers)
    except Exception as e:
        logging.error(f"API request failed: {e}")
        return

    # Step 2: Extract JSON
    logging.info("Step 2: Extracting JSON data...")
    api_json = extract_json(response)
    if api_json is None:
        return

    # Step 3: Transform to DataFrame
    logging.info("Step 3: Transforming data to DataFrame...")
    df = transform_standings(api_json)

    # Display standings
    logging.info("\n========== Premier League Standings ==========")
    logging.info(f'Total teams: {len(df)}')
    logging.info("==============================================\n")

    # Step 4: Save DataFrame to CSV
    logging.info("Step 4: Saving DataFrame to CSV file...")
    csv_filename = save_to_csv(df)
    if csv_filename is None:
        return

    # Step 5: Load CSV to MySQL
    logging.info("Step 5: Loading CSV data to MySQL...")
    csv_to_mysql(csv_filename)

    logging.info("✓ Pipeline completed successfully: API → DataFrame → CSV → MySQL")

# Run Program
if __name__ == "__main__":
    main()