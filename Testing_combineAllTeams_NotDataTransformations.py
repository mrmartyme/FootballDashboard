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

    # Calculate cumulative wins based on the "Result" column
    df["Cumulative Wins"] = df["Result"].apply(lambda x: 1 if "W" in x else 0).cumsum()

    # Insert the "Cumulative Wins" column after the "Result" column
    result_index = df.columns.get_loc("Result") + 1
    columns = df.columns.tolist()
    columns.remove("Cumulative Wins")
    columns.insert(result_index, "Cumulative Wins")
    df = df[columns]

    # Convert "Total Offense_TOP" to decimal minutes and round to 2 decimal places
    df["Total Offense_TOP_Converted"] = df["Total Offense_TOP"].apply(
        lambda x: round(int(x.split(":")[0]) + int(x.split(":")[1]) / 60, 2) if isinstance(x, str) else 0
    )

    # Insert "Total Offense_TOP_Converted" after "Total Offense_TOP"
    top_index = df.columns.get_loc("Total Offense_TOP") + 1
    if "Total Offense_TOP_Converted" in columns:
        columns.remove("Total Offense_TOP_Converted")
    columns.insert(top_index, "Total Offense_TOP_Converted")
    df = df[columns]

    # Append the DataFrame to the list
    dfs.append(df)

# Step 5: Concatenate all the DataFrames vertically
if dfs:  # Ensure there is data to concatenate
    combined_df = pd.concat(dfs, ignore_index=True)

    # Step 6: Replace empty values with 0
    combined_df.fillna(0, inplace=True)

    # # Step 7: Calculate "Rushing_GainedYdsPerRush" and round to 2 decimal places
    # combined_df["Rushing_GainedYdsPerRush"] = (
    #     combined_df["Rushing_Rush YdsGained"] / combined_df["Rushing_Rush Attempts"]
    # ).fillna(0).round(2)
    #
    # # Insert the new column after "Rushing_Rush YdsGained"
    # gained_yards_index = combined_df.columns.get_loc("Rushing_Rush YdsGained") + 1
    # if "Rushing_GainedYdsPerRush" in columns:
    #     columns.remove("Rushing_GainedYdsPerRush")
    # columns.insert(gained_yards_index, "Rushing_GainedYdsPerRush")
    # combined_df = combined_df[columns]
    #
    # # Step 8: Calculate "Passing_YdsPerAttempt" and round to 2 decimal places
    # combined_df["Passing_YdsPerAttempt"] = (
    #     combined_df["Passing_Pass Yards"] / combined_df["Passing_Pass Attempts"]
    # ).fillna(0).round(2)
    #
    # # Insert the new column after "Passing_Yds PerCompletion"
    # yds_per_completion_index = combined_df.columns.get_loc("Passing_Yds PerCompletion") + 1
    # if "Passing_YdsPerAttempt" in columns:
    #     columns.remove("Passing_YdsPerAttempt")
    # columns.insert(yds_per_completion_index, "Passing_YdsPerAttempt")
    # combined_df = combined_df[columns]
    #
    # # Step 9: Calculate "Redzone_RZPtsPerRZAtt" and round to 2 decimal places
    # combined_df["Redzone_RZPtsPerRZAtt"] = (
    #     combined_df["Redzone_RZPts"] / combined_df["Redzone_RZAtt"]
    # ).fillna(0).round(2)
    #
    # # Step 10: Calculate "Redzone_RZScoresPerRZAtt" and round to 2 decimal places
    # combined_df["Redzone_RZScoresPerRZAtt"] = (
    #     combined_df["Redzone_RZScores"] / combined_df["Redzone_RZAtt"]
    # ).fillna(0).round(2)
    #
    # # Step 11: Calculate "Redzone_RZTDConvPct" and round to 4 decimal places
    # combined_df["Redzone_RZTDConvPct"] = (
    #     (combined_df["Redzone_RZ Rush TD"] + combined_df["Redzone_RZ Pass TD"]) / combined_df["Redzone_RZAtt"]
    # ).fillna(0).round(4)
    #
    # # Step 12: Insert the Redzone columns after "Redzone_RZEndDowns"
    # redzone_end_downs_index = combined_df.columns.get_loc("Redzone_RZEndDowns") + 1
    # if "Redzone_RZPtsPerRZAtt" in columns:
    #     columns.remove("Redzone_RZPtsPerRZAtt")
    # if "Redzone_RZScoresPerRZAtt" in columns:
    #     columns.remove("Redzone_RZScoresPerRZAtt")
    # if "Redzone_RZTDConvPct" in columns:
    #     columns.remove("Redzone_RZTDConvPct")
    # columns.insert(redzone_end_downs_index, "Redzone_RZPtsPerRZAtt")
    # columns.insert(redzone_end_downs_index + 1, "Redzone_RZScoresPerRZAtt")
    # columns.insert(redzone_end_downs_index + 2, "Redzone_RZTDConvPct")
    # combined_df = combined_df[columns]
    #
    # # Step 13: Calculate "Turnover Margin_TurnoverMargin"
    # combined_df["Turnover Margin_TurnoverMargin"] = (
    #     ((combined_df["Turnover Margin_FumblesLost"] + combined_df["Turnover Margin_Interceptions"]) * -1) +
    #     (combined_df["Turnover Margin_Fumbles Recovered"] + combined_df["Turnover Margin_Int"])
    # ).fillna(0)

    # Step 14: Save the combined DataFrame to a new CSV file
    output_filename = "All_Teams_Combined.csv"
    output_filepath = os.path.join(input_directory, output_filename)
    combined_df.to_csv(output_filepath, index=False)

    # Output: Confirm that the file was saved
    print(f"All teams combined file saved as {output_filepath} with shape {combined_df.shape}")
else:
    print("No active team files found to combine.")
