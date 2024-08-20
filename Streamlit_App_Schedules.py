import streamlit as st
import pandas as pd

# Inject custom CSS to force light mode
st.markdown(
    """
    <style>
    body {
        background-color: white !important;
        color: black !important;
    }
    .reportview-container {
        background-color: white !important;
        color: black !important;
    }
    .schedule-table th, .schedule-table td {
        background-color: white !important;
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load data
teams_df = pd.read_csv('teams.csv')
colors_df = pd.read_csv('TeamColors.csv')
schedule_df = pd.read_csv('Schedule2024.csv')

# Set default selected teams
default_teams = ['BYU', 'Utah']

# Create a checkbox for selecting all teams
select_all = st.checkbox('Select All Teams')

# If 'Select All' is checked, select all teams; otherwise, allow individual selection
if select_all:
    selected_teams = st.multiselect('Select Specific Teams', teams_df['name'], default=teams_df['name'].tolist())
else:
    selected_teams = st.multiselect('Select Specific Teams', teams_df['name'], default=default_teams)

# Convert the 'Start Date' column to datetime format to easily extract day of the week
schedule_df['Start Date'] = pd.to_datetime(schedule_df['Start Date'])

# Add a new column 'Day' for the day of the week abbreviation
schedule_df['Day'] = schedule_df['Start Date'].dt.strftime('%a')

# Get the maximum week number in the schedule
max_week = schedule_df['Week'].max()

# Generate a list of all weeks to ensure every week is covered
all_weeks = list(range(1, max_week + 1))

# Filter schedule data based on selected teams
filtered_schedule = schedule_df[(schedule_df['HomeTeam'].isin(selected_teams)) |
                                (schedule_df['AwayTeam'].isin(selected_teams))]

# Display schedule in grid format by week with color coding
if selected_teams:
    grid_data = []

    for week in all_weeks:
        week_data = {"Week": week}
        for team in selected_teams:
            team_color = colors_df[colors_df['Team'] == team]['Color'].values[0]
            team_schedule = filtered_schedule[(filtered_schedule['Week'] == week) &
                                              ((filtered_schedule['HomeTeam'] == team) |
                                               (filtered_schedule['AwayTeam'] == team))]
            if not team_schedule.empty:
                game = team_schedule.iloc[0]
                opp = f"@{game['HomeTeam']}" if game['AwayTeam'] == team else game['AwayTeam']
                # Format date with day of the week (e.g., 08/31/2024 (Sat)) and remove leading zeros
                formatted_date = f"{game['Start Date'].strftime('%m/%d/%Y').lstrip('0').replace('/0', '/')} ({game['Day']})"
                # Only highlight when the team is at home
                if game['HomeTeam'] == team:
                    week_data[
                        team] = f"<div style='background-color:{team_color};color:white;padding:5px;border-radius:5px;'>{formatted_date} {opp}</div>"
                else:
                    week_data[team] = f"{formatted_date} {opp}"
            else:
                # No game scheduled, so mark as 'bye'
                week_data[team] = "bye"
        grid_data.append(week_data)

    grid_df = pd.DataFrame(grid_data)

    # Display the schedule in a grid with colors and gridlines
    st.markdown(
        """
        <style>
        .schedule-table {
            border-collapse: collapse;
            width: 100%;
        }
        .schedule-table th, .schedule-table td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        .schedule-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Convert DataFrame to HTML with custom styling
    st.markdown(grid_df.to_html(index=False, escape=False, classes='schedule-table'), unsafe_allow_html=True)
