import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime
import re

# Page configuration
st.set_page_config(page_title="Premier League 2020-21 Dashboard", layout="wide", page_icon="⚽")

# Load and process data
@st.cache_data
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

@st.cache_data
def calculate_standings(df):
    """Calculate league standings after each round"""
    teams = sorted(set(df['Team 1'].unique()) | set(df['Team 2'].unique()))

    # Initialize team stats
    team_stats = {team: {
        'points': [],
        'position': [],
        'goals_for': [],
        'goals_against': [],
        'wins': 0,
        'draws': 0,
        'losses': 0,
        'matches': []
    } for team in teams}

    # Process matches round by round
    for round_num in range(1, 39):
        round_matches = df[df['Round'] == round_num]

        # Update team stats for this round
        for _, match in round_matches.iterrows():
            team1 = match['Team 1']
            team2 = match['Team 2']
            goals1 = int(match['Team1_Goals'])
            goals2 = int(match['Team2_Goals'])

            # Determine result
            if goals1 > goals2:
                points1, points2 = 3, 0
                result1, result2 = 'W', 'L'
            elif goals1 < goals2:
                points1, points2 = 0, 3
                result1, result2 = 'L', 'W'
            else:
                points1, points2 = 1, 1
                result1, result2 = 'D', 'D'

            # Update team 1
            team_stats[team1]['matches'].append({
                'round': round_num,
                'opponent': team2,
                'home': True,
                'goals_for': goals1,
                'goals_against': goals2,
                'points': points1,
                'result': result1,
                'date': match['Date']
            })

            # Update team 2
            team_stats[team2]['matches'].append({
                'round': round_num,
                'opponent': team1,
                'home': False,
                'goals_for': goals2,
                'goals_against': goals1,
                'points': points2,
                'result': result2,
                'date': match['Date']
            })

        # Calculate cumulative stats and positions for this round
        round_standings = []
        for team in teams:
            team_matches = [m for m in team_stats[team]['matches'] if m['round'] <= round_num]

            if team_matches:
                total_points = sum(m['points'] for m in team_matches)
                total_gf = sum(m['goals_for'] for m in team_matches)
                total_ga = sum(m['goals_against'] for m in team_matches)
                gd = total_gf - total_ga

                round_standings.append({
                    'team': team,
                    'points': total_points,
                    'gf': total_gf,
                    'ga': total_ga,
                    'gd': gd,
                    'played': len(team_matches)
                })

        # Sort by points, then goal difference, then goals for
        round_standings.sort(key=lambda x: (x['points'], x['gd'], x['gf']), reverse=True)

        # Assign positions
        for pos, standing in enumerate(round_standings, 1):
            team = standing['team']
            team_stats[team]['points'].append(standing['points'])
            team_stats[team]['position'].append(pos)
            team_stats[team]['goals_for'].append(standing['gf'])
            team_stats[team]['goals_against'].append(standing['ga'])

    # Calculate final season stats
    for team in teams:
        team_matches = team_stats[team]['matches']
        team_stats[team]['wins'] = sum(1 for m in team_matches if m['result'] == 'W')
        team_stats[team]['draws'] = sum(1 for m in team_matches if m['result'] == 'D')
        team_stats[team]['losses'] = sum(1 for m in team_matches if m['result'] == 'L')

    return team_stats

@st.cache_data
def calculate_streaks(team_stats, team):
    """Calculate best and worst 5-game streaks"""
    matches = team_stats[team]['matches']

    if len(matches) < 5:
        return None, None

    best_streak = {'points': -1, 'start': 0, 'end': 4}
    worst_streak = {'points': 999, 'start': 0, 'end': 4}

    for i in range(len(matches) - 4):
        streak_matches = matches[i:i+5]
        streak_points = sum(m['points'] for m in streak_matches)

        if streak_points > best_streak['points']:
            best_streak = {'points': streak_points, 'start': i, 'end': i+4}

        if streak_points < worst_streak['points']:
            worst_streak = {'points': streak_points, 'start': i, 'end': i+4}

    return best_streak, worst_streak

# Load data
df = load_data()
team_stats = calculate_standings(df)
teams = sorted(team_stats.keys())

# Dashboard title
st.title("⚽ Premier League 2020-21 Season Performance Dashboard")
st.markdown("---")

# Team selection
selected_team = st.selectbox("Select Team", teams, index=teams.index("Liverpool") if "Liverpool" in teams else 0)

# Get team data
team_data = team_stats[selected_team]

# Create three columns layout
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.subheader(f"📈 {selected_team} - League Position Chart")

    # Create position chart
    rounds = list(range(1, len(team_data['position']) + 1))
    positions = team_data['position']

    # Create color mapping based on position
    colors = []
    for pos in positions:
        if pos == 1:
            colors.append('green')
        elif 2 <= pos <= 4:
            colors.append('blue')
        elif 18 <= pos <= 20:
            colors.append('red')
        else:
            colors.append('black')

    fig = go.Figure()

    # Add the line with color segments
    for i in range(len(rounds) - 1):
        fig.add_trace(go.Scatter(
            x=[rounds[i], rounds[i+1]],
            y=[positions[i], positions[i+1]],
            mode='lines+markers',
            line=dict(color=colors[i], width=3),
            marker=dict(size=8, color=colors[i]),
            showlegend=False,
            hovertemplate=f'Round: %{{x}}<br>Position: %{{y}}<extra></extra>'
        ))

    # Add last point
    fig.add_trace(go.Scatter(
        x=[rounds[-1]],
        y=[positions[-1]],
        mode='markers',
        marker=dict(size=8, color=colors[-1]),
        showlegend=False
    ))

    # Add colored zones
    fig.add_hrect(y0=0.5, y1=1.5, fillcolor="green", opacity=0.1, line_width=0)
    fig.add_hrect(y0=1.5, y1=4.5, fillcolor="blue", opacity=0.1, line_width=0)
    fig.add_hrect(y0=17.5, y1=20.5, fillcolor="red", opacity=0.1, line_width=0)

    fig.update_layout(
        xaxis_title="Round",
        yaxis_title="League Position",
        yaxis=dict(
            autorange="reversed",
            tickmode='linear',
            tick0=1,
            dtick=1,
            range=[20.5, 0.5]
        ),
        xaxis=dict(
            tickmode='linear',
            tick0=1,
            dtick=2,
            range=[0.5, 38.5]
        ),
        height=500,
        hovermode='closest'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Legend
    st.markdown("""
    **Position Zones:**
    🟢 Position 1 (Champion) | 🔵 Positions 2-4 (Champions League) | ⚫ Positions 5-17 (Mid-table) | 🔴 Positions 18-20 (Relegation)
    """)

with col2:
    st.subheader("📊 Season Summary")

    final_position = positions[-1]
    final_points = team_data['points'][-1]
    final_gf = team_data['goals_for'][-1]
    final_ga = team_data['goals_against'][-1]

    # Display cards
    st.metric("Final Position", f"{final_position}", delta=None)
    st.metric("Total Points", final_points)
    st.metric("Goals For", final_gf)
    st.metric("Goals Against", final_ga)
    st.metric("Goal Difference", final_gf - final_ga)

    st.markdown("---")

    col_w, col_d, col_l = st.columns(3)
    with col_w:
        st.metric("Wins", team_data['wins'])
    with col_d:
        st.metric("Draws", team_data['draws'])
    with col_l:
        st.metric("Losses", team_data['losses'])

with col3:
    st.subheader("🔥 Momentum Analysis")

    best_streak, worst_streak = calculate_streaks(team_stats, selected_team)

    if best_streak:
        st.markdown("**Best 5-Game Streak**")
        st.success(f"**{best_streak['points']} points**")

        best_matches = team_data['matches'][best_streak['start']:best_streak['end']+1]
        st.caption(f"Round {best_matches[0]['round']} to {best_matches[-1]['round']}")

        # Show first and last match
        first_match = best_matches[0]
        last_match = best_matches[-1]

        st.markdown(f"""
        **Start:** {first_match['date']}
        {'🏠' if first_match['home'] else '✈️'} vs {first_match['opponent']}
        {first_match['goals_for']}-{first_match['goals_against']} ({first_match['result']})

        **End:** {last_match['date']}
        {'🏠' if last_match['home'] else '✈️'} vs {last_match['opponent']}
        {last_match['goals_for']}-{last_match['goals_against']} ({last_match['result']})
        """)

    st.markdown("---")

    if worst_streak:
        st.markdown("**Worst 5-Game Streak**")
        st.error(f"**{worst_streak['points']} points**")

        worst_matches = team_data['matches'][worst_streak['start']:worst_streak['end']+1]
        st.caption(f"Round {worst_matches[0]['round']} to {worst_matches[-1]['round']}")

        # Show first and last match
        first_match = worst_matches[0]
        last_match = worst_matches[-1]

        st.markdown(f"""
        **Start:** {first_match['date']}
        {'🏠' if first_match['home'] else '✈️'} vs {first_match['opponent']}
        {first_match['goals_for']}-{first_match['goals_against']} ({first_match['result']})

        **End:** {last_match['date']}
        {'🏠' if last_match['home'] else '✈️'} vs {last_match['opponent']}
        {last_match['goals_for']}-{last_match['goals_against']} ({last_match['result']})
        """)

# Match-by-match results table
st.markdown("---")
st.subheader(f"📅 {selected_team} - Match Results")

# Create a dataframe from matches
matches_df = pd.DataFrame(team_data['matches'])
matches_df['Score'] = matches_df.apply(lambda x: f"{x['goals_for']}-{x['goals_against']}", axis=1)
matches_df['Venue'] = matches_df['home'].apply(lambda x: 'Home' if x else 'Away')
matches_df['Result'] = matches_df['result'].apply(lambda x: {'W': '✅ Win', 'D': '➖ Draw', 'L': '❌ Loss'}[x])

display_df = matches_df[['round', 'date', 'opponent', 'Venue', 'Score', 'Result', 'points']].copy()
display_df.columns = ['Round', 'Date', 'Opponent', 'Venue', 'Score', 'Result', 'Points']

st.dataframe(display_df, use_container_width=True, height=400)

# Footer
st.markdown("---")
st.caption("Premier League 2020-21 Season | Data from eng.1.csv")
