# Premier League Standings ETL Pipeline

A Python-based ETL (Extract, Transform, Load) pipeline that fetches Premier League standings from the Football Data API, processes the data, and stores it in a MySQL database.

## Features

- ✅ Fetch live Premier League standings from Football Data API
- ✅ Transform JSON data into structured format
- ✅ Save data to CSV for backup/analysis
- ✅ Load data into MySQL database
- ✅ Comprehensive logging
- ✅ Error handling and validation

## Prerequisites

- Python 3.8+
- MySQL Server
- Football Data API key (get free tier at [football-data.org](https://www.football-data.org/))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Tartmo0097/Premier-League-standings-ETL-pipeline.git
cd Premier-League-standings-ETL-pipeline
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

5. Create MySQL database:
```sql
CREATE DATABASE mydatabase;
```

## Usage

Run the pipeline:
```bash
python pl_standing.py
```

The script will:
1. Fetch current Premier League standings
2. Transform the data
3. Save to CSV file (`pl_standings.csv`)
4. Load data into MySQL table

## Database Schema

The `pl_standings` table contains:
- `position` - Team position in table
- `team_name` - Team name
- `points` - Total points
- `playedGames` - Games played
- `won` - Games won
- `draw` - Games drawn
- `lost` - Games lost
- `goals_for` - Goals scored
- `goals_against` - Goals conceded
- `goal_difference` - Goal difference

## Configuration

Edit the following in your `.env` file:
- `FOOTBALL_API_TOKEN` - Your Football Data API token
- `MYSQL_*` - Your MySQL connection details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Acknowledgments

- Data provided by [Football-Data.org](https://www.football-data.org/)