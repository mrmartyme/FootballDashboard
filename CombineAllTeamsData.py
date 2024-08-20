import os
import pandas as pd

# Step 1: Load the teams from the CSV file and filter for active teams
teams_df = pd.read_csv('teams.csv')
active_teams = teams_df[teams_df['active'] == 1]['name'].tolist()

# Step 2: Define the directory where the team files are located
input_directory = os.path.join(".", "TeamDataFiles")

# Step 3: List all combined team files for active teams in the directory
team_files = [
    f for f in os.listdir(input_directory)
    if f.endswith("_Combined.csv") and f.split('_Combined')[0].replace('_', ' ') in active_teams
]

# Initialize an empty list to hold DataFrames
dfs = []

# Step 4: Loop through each team file and load it into a DataFrame
for team_file in team_files:
    filepath = os.path.join(input_directory, team_file)

    # Load the CSV file into a DataFrame
    df = pd.read_csv(filepath)
    print(f"Loaded {team_file} with shape {df.shape}")

    # Remove any trailing '/' from all columns
    df = df.apply(lambda x: x.str.rstrip('/') if x.dtype == "object" else x)

    # Sort by the week of play (assumed to be in the "Date" column) before calculating cumulative wins
    df = df.sort_values(by="Date")

    # Convert relevant columns to numeric, coercing errors to NaN and filling them with 0
    df["Rushing_Rush YdsGained"] = pd.to_numeric(df["Rushing_Rush YdsGained"], errors='coerce').fillna(0)
    df["Rushing_Rush Attempts"] = pd.to_numeric(df["Rushing_Rush Attempts"], errors='coerce').fillna(0)
    df["Passing_Pass Yards"] = pd.to_numeric(df["Passing_Pass Yards"], errors='coerce').fillna(0)
    df["Passing_Pass Attempts"] = pd.to_numeric(df["Passing_Pass Attempts"], errors='coerce').fillna(0)
    df["Redzone_RZPts"] = pd.to_numeric(df["Redzone_RZPts"], errors='coerce').fillna(0)
    df["Redzone_RZAtt"] = pd.to_numeric(df["Redzone_RZAtt"], errors='coerce').fillna(0)
    df["Redzone_RZ Rush TD"] = pd.to_numeric(df["Redzone_RZ Rush TD"], errors='coerce').fillna(0)
    df["Redzone_RZ Pass TD"] = pd.to_numeric(df["Redzone_RZ Pass TD"], errors='coerce').fillna(0)
    df["Turnover Margin_FumblesLost"] = pd.to_numeric(df["Turnover Margin_FumblesLost"], errors='coerce').fillna(0)
    df["Turnover Margin_Interceptions"] = pd.to_numeric(df["Turnover Margin_Interceptions"], errors='coerce').fillna(0)
    df["Turnover Margin_Fumbles Recovered"] = pd.to_numeric(df["Turnover Margin_Fumbles Recovered"], errors='coerce').fillna(0)
    df["Turnover Margin_Int"] = pd.to_numeric(df["Turnover Margin_Int"], errors='coerce').fillna(0)

    # Calculate new columns
    df["Cumulative Wins"] = df["Result"].apply(lambda x: 1 if "W" in x else 0).cumsum()
    df["Rushing_GainedYdsPerRush"] = (df["Rushing_Rush YdsGained"] / df["Rushing_Rush Attempts"]).round(2)
    df["Passing_YdsPerAttempt"] = (df["Passing_Pass Yards"] / df["Passing_Pass Attempts"]).round(2)
    df["Redzone_RZPtsPerRZAtt"] = (df["Redzone_RZPts"] / df["Redzone_RZAtt"]).round(2)
    df["Redzone_RZScoresPerRZAtt"] = (df["Redzone_RZScores"] / df["Redzone_RZAtt"]).round(2)
    df["Redzone_RZTDConvPct"] = ((df["Redzone_RZ Rush TD"] + df["Redzone_RZ Pass TD"]) / df["Redzone_RZAtt"]).round(4)
    df["Turnover Margin_TurnoverMargin"] = (
        (df["Turnover Margin_FumblesLost"] + df["Turnover Margin_Interceptions"]) * -1 +
        (df["Turnover Margin_Fumbles Recovered"] + df["Turnover Margin_Int"])
    ).round(2)
    df["Total Offense_TOP_Converted"] = df["Total Offense_TOP"].apply(
        lambda x: round(int(x.split(":")[0]) + int(x.split(":")[1]) / 60, 2) if isinstance(x, str) else 0
    )

    # Insert new columns into their respective positions
    result_index = df.columns.get_loc("Result") + 1  # Define result_index before using it
    df = pd.concat([
        df.iloc[:, :result_index],  # Columns up to "Result"
        df[["Cumulative Wins"]],  # Insert "Cumulative Wins"
        df.iloc[:, result_index:],  # Columns after "Result"
        df[["Rushing_GainedYdsPerRush", "Passing_YdsPerAttempt",
            "Redzone_RZPtsPerRZAtt", "Redzone_RZScoresPerRZAtt", "Redzone_RZTDConvPct",
            "Turnover Margin_TurnoverMargin", "Total Offense_TOP_Converted"]]
    ], axis=1)

    # Append the DataFrame to the list
    dfs.append(df)

# Step 5: Concatenate all the DataFrames vertically
if dfs:  # Ensure there is data to concatenate
    combined_df = pd.concat(dfs, ignore_index=True)

    # Step 6: Replace empty values with 0
    combined_df.fillna(0, inplace=True)

    # Step 7: Save the combined DataFrame to a new CSV file
    output_filename = "All_Teams_Combined.csv"
    output_filepath = os.path.join(input_directory, output_filename)
    combined_df.to_csv(output_filepath, index=False)

    # Output: Confirm that the file was saved
    print(f"All teams combined file saved as {output_filepath} with shape {combined_df.shape}")
else:
    print("No active team files found to combine.")
