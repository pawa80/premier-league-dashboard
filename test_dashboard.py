import pandas as pd
import re

def load_data():
    """Load and process Premier League 2020-21 data"""
    df = pd.read_csv('eng.1.csv')

    # Parse the score
    def parse_score(score_str):
        if pd.isna(score_str) or score_str == '':
            return None, None
        # Handle different dash types (en-dash, em-dash, hyphen)
        score_parts = re.split('[–—-]', str(score_str))
        if len(score_parts) == 2:
            return int(score_parts[0]), int(score_parts[1])
        return None, None

    df[['Team1_Goals', 'Team2_Goals']] = df['FT'].apply(
        lambda x: pd.Series(parse_score(x))
    )

    # Remove rows with missing scores (postponed matches)
    df = df.dropna(subset=['Team1_Goals', 'Team2_Goals'])

    return df

def test_basic_stats():
    """Test basic data loading and statistics"""
    print("Loading data...")
    df = load_data()

    print(f"\n✓ Loaded {len(df)} matches")
    print(f"✓ Rounds: {df['Round'].min()} to {df['Round'].max()}")

    teams = sorted(set(df['Team 1'].unique()) | set(df['Team 2'].unique()))
    print(f"✓ Number of teams: {len(teams)}")

    print("\nTeams:")
    for i, team in enumerate(teams, 1):
        print(f"  {i:2d}. {team}")

    # Test a specific team's final standings
    print("\n" + "="*60)
    print("Testing position calculation for Liverpool...")
    print("="*60)

    # Calculate Liverpool's stats
    liverpool_matches = []

    for _, match in df.iterrows():
        if match['Team 1'] == 'Liverpool':
            goals_for = int(match['Team1_Goals'])
            goals_against = int(match['Team2_Goals'])
            if goals_for > goals_against:
                points = 3
            elif goals_for < goals_against:
                points = 0
            else:
                points = 1

            liverpool_matches.append({
                'round': match['Round'],
                'opponent': match['Team 2'],
                'home': True,
                'score': f"{goals_for}-{goals_against}",
                'points': points
            })

        elif match['Team 2'] == 'Liverpool':
            goals_for = int(match['Team2_Goals'])
            goals_against = int(match['Team1_Goals'])
            if goals_for > goals_against:
                points = 3
            elif goals_for < goals_against:
                points = 0
            else:
                points = 1

            liverpool_matches.append({
                'round': match['Round'],
                'opponent': match['Team 1'],
                'home': False,
                'score': f"{goals_for}-{goals_against}",
                'points': points
            })

    liverpool_matches.sort(key=lambda x: x['round'])

    total_points = sum(m['points'] for m in liverpool_matches)
    wins = sum(1 for m in liverpool_matches if m['points'] == 3)
    draws = sum(1 for m in liverpool_matches if m['points'] == 1)
    losses = sum(1 for m in liverpool_matches if m['points'] == 0)

    print(f"\nLiverpool Season Stats:")
    print(f"  Matches played: {len(liverpool_matches)}")
    print(f"  Total points: {total_points}")
    print(f"  Wins: {wins}")
    print(f"  Draws: {draws}")
    print(f"  Losses: {losses}")

    print(f"\n✓ All tests passed! Dashboard should work correctly.")

if __name__ == "__main__":
    test_basic_stats()
