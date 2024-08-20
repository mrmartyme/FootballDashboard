import streamlit as st
import pandas as pd
import plotly.express as px

# Set Streamlit to use dark mode
st.set_page_config(page_title="2023 Football Stats Dashboard", layout="wide", initial_sidebar_state="expanded")

# Page navigation (default to "Team Schedules")
page = st.sidebar.radio("Choose a page", ["Team Schedules", "Team Stats Dashboard"])

# Load data
df = pd.read_csv(r'TeamDataFiles/All_Teams_Combined.csv', parse_dates=['Date'])
statlist_df = pd.read_csv(r'statlist.csv')
colors_df = pd.read_csv(r'TeamColors.csv')  # Load the team colors from a CSV file

# Filter active columns and exclude the "Dimension" category
active_stats = statlist_df[(statlist_df['Active'] == 1) & (statlist_df['Category'] != 'Dimension')]

# Create a mapping of column names to short names
column_mapping = dict(zip(active_stats['Column'], active_stats['ShortName']))

# Create a dictionary to hold categorized stats, excluding "Dimension"
categories = active_stats['Category'].unique()
categorized_stats = {category: active_stats[active_stats['Category'] == category]['ShortName'].tolist()
                     for category in categories}

# Create "All Stats" category that includes all stats except "Dimension"
all_stats = active_stats['ShortName'].tolist()
categorized_stats['All Stats'] = all_stats

if page == "Team Stats Dashboard":
    # Title of the app
    st.title('B12 Stats Dashboard')

    # Sidebar filters
    team_options = df['TeamNM'].unique()
    team_options.sort()
    default_teams = ['BYU', 'Utah']

    team_filter = st.sidebar.multiselect('Select Team(s)', team_options, default=default_teams)
    date_range = st.sidebar.date_input('Select Date Range', [df['Date'].min(), df['Date'].max()])

    # Default the allow multiple stats option to be on
    allow_multiple_stats = st.sidebar.checkbox('Allow Multiple Stats', value=True)

    # Stat selection with category, excluding "Dimension"
    category_options = ['All Stats'] + [category for category in categories if category != 'Dimension']
    stat_category = st.sidebar.selectbox('Select Stat Category', category_options)

    # Default stats
    default_stats = ['RushNetYdsPer', 'PassYdsPerComp']

    # Stat selection dropdown, with the option for multiple if toggled
    if allow_multiple_stats:
        stat_to_plot = st.sidebar.multiselect('Select Stat(s) to Plot', categorized_stats[stat_category],
                                              default=default_stats)
    else:
        stat_to_plot = [st.sidebar.selectbox('Select Stat to Plot', categorized_stats[stat_category])]

    # Graph type selection with scatter plot as default
    graph_type = st.sidebar.selectbox(
        "Select Graph Type",
        ["Bar Chart", "Line Chart", "Area Chart", "Scatter Plot", "Box Plot"],
        index=0  # Default to scatter plot
    )

    # Calculate cumulative wins and add a "Win" flag
    df['Win'] = df['Result'].apply(lambda x: 1 if 'W' in x else 0)
    df['Cumulative Wins'] = df.groupby('TeamNM')['Win'].cumsum()

    # Add W/L to opponent label
    df['Opponent_Label'] = df['Opponent'] + ' (' + df['Result'].str[0] + ')'

    # Get the actual column names from the selected short names
    selected_columns = active_stats[active_stats['ShortName'].isin(stat_to_plot)]['Column'].tolist()

    # Convert the selected date range to datetime
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    # Filter data based on selection
    filtered_df = df[(df['TeamNM'].isin(team_filter)) & (df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # Sort by date to maintain chronological order
    filtered_df = filtered_df.sort_values(['TeamNM', 'Date'])

    # If multiple teams are selected, use game ordinality instead of date
    if len(team_filter) > 1:
        filtered_df['Game Number'] = filtered_df.groupby('TeamNM').cumcount() + 1
        filtered_df['Game Label'] = filtered_df['TeamNM'] + ' vs ' + filtered_df['Opponent_Label']
        x_axis = 'Game Number'
        x_label = 'Game Number (Multiple Teams)'
    else:
        x_axis = 'Date'
        x_label = 'Date'

    # Assign colors to teams based on the CSV file, with random colors for teams not listed
    color_map = {row['Team']: row['Color'] for _, row in colors_df.iterrows()}
    for team in team_filter:
        if team not in color_map:
            color_map[team] = None  # Plotly will assign a random color

    # Check if filtered_df is empty or if there are no valid selections
    if filtered_df.empty or not selected_columns:
        st.write("No data available for the selected filters or selections.")
    else:
        # Plot data based on the selected graph type
        for column in selected_columns:
            stat_name = active_stats[active_stats['Column'] == column]['ShortName'].values[0]

            if graph_type == "Bar Chart":
                fig = px.bar(filtered_df, x=x_axis, y=column, color='TeamNM',
                             text='Game Label' if len(team_filter) > 1 else 'Opponent_Label',
                             title=f'{stat_name} by {x_label}', color_discrete_map=color_map,
                             template='plotly_dark')  # Apply dark theme

                fig.update_layout(barmode='group')  # Set bar mode to 'group' for side-by-side bars

            elif graph_type == "Line Chart":
                fig = px.line(filtered_df, x=x_axis, y=column, color='TeamNM', title=f'{stat_name} by {x_label}',
                              markers=True, color_discrete_map=color_map, template='plotly_dark')  # Apply dark theme

            elif graph_type == "Area Chart":
                fig = px.area(filtered_df, x=x_axis, y=column, color='TeamNM', title=f'{stat_name} by {x_label}',
                              color_discrete_map=color_map, template='plotly_dark')  # Apply dark theme

            elif graph_type == "Scatter Plot":
                fig = px.scatter(filtered_df, x=x_axis, y=column, color='TeamNM', title=f'{stat_name} by {x_label}',
                                 trendline="ols", color_discrete_map=color_map, template='plotly_dark')  # Apply dark theme

            elif graph_type == "Box Plot":
                fig = px.box(filtered_df, x='TeamNM', y=column, color='TeamNM', title=f'{stat_name} Distribution',
                             color_discrete_map=color_map, template='plotly_dark')  # Apply dark theme

            # Update layout for better readability and responsive design
            fig.update_layout(
                xaxis_title=x_label,
                yaxis_title=stat_name,
                yaxis=dict(range=[0, None]),  # Set lower boundary to 0
                autosize=True,
                margin=dict(l=20, r=20, t=50, b=20),  # Adjust margins for responsiveness
                height=500,  # Set a base height
                width=None  # Let the width be responsive
            )
            st.plotly_chart(fig, use_container_width=True)

elif page == "Team Schedules":
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
