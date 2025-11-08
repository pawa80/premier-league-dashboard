# Premier League 2020-21 Season Performance Dashboard

An interactive web dashboard for analyzing Premier League 2020-21 season performance, featuring team-by-team analysis with position tracking, season statistics, and momentum analysis.

## Features

### 1. League Position Chart
- Interactive line graph showing selected team's position (1-20) across all 38 rounds
- Color-coded zones:
  - 🟢 Green: Position 1 (Champion)
  - 🔵 Blue: Positions 2-4 (Champions League qualification)
  - ⚫ Black: Positions 5-17 (Mid-table)
  - 🔴 Red: Positions 18-20 (Relegation zone)

### 2. Season Summary
- Final league position
- Total points earned
- Goals for and against
- Goal difference
- Wins, draws, and losses breakdown

### 3. Momentum Analysis
- **Best 5-game streak**: Period with most points, showing first and last matches
- **Worst 5-game streak**: Period with fewest points, showing first and last matches

### 4. Match-by-Match Results
- Complete fixture list with dates, opponents, venues, scores, and points

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure the CSV file `eng.1.csv` is in the same directory as `dashboard.py`

2. Run the dashboard:
```bash
streamlit run dashboard.py
```

3. The dashboard will open in your default web browser at `http://localhost:8501`

4. Use the dropdown menu to select different teams and explore their season performance

## Data Format

The dashboard expects a CSV file with the following columns:
- `Round`: Match round number (1-38)
- `Date`: Match date
- `Team 1`: Home team name
- `FT`: Final score (format: "X–Y" or "X-Y")
- `Team 2`: Away team name

## Technical Details

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas
- **Caching**: Streamlit's caching mechanism for optimal performance

## Dashboard Components

### Position Calculation
The dashboard calculates league positions after each round using the standard Premier League ranking criteria:
1. Points (3 for win, 1 for draw, 0 for loss)
2. Goal difference
3. Goals scored

### Streak Detection
The momentum analysis identifies the best and worst consecutive 5-game periods by:
- Sliding window approach across all matches
- Summing points for each 5-match window
- Identifying maximum and minimum point totals

## Browser Compatibility

The dashboard works best on:
- Chrome/Edge (recommended)
- Firefox
- Safari

## Credits

Data source: England Football League 2020-21 season statistics
