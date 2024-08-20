import os
import pandas as pd

# Step 1: Load the link texts from the CSV file and filter for active links
link_texts_df = pd.read_csv('link_texts.csv')
link_texts = link_texts_df[link_texts_df['active'] == 1]['link_text'].tolist()

# Step 2: Load the teams from the CSV file and filter for active teams
teams_df = pd.read_csv('teams.csv')
teams = teams_df[teams_df['active'] == 1].to_dict(orient='records')

# Directory where the CSV files are saved
output_directory = "./TeamDataFiles"  # Adjust this if files are saved in a different directory

# Step 3: Loop through each active team
for team in teams:
    combined_df = None  # Initialize an empty DataFrame for combining

    # Step 4: Loop through each active link text to load and combine the corresponding CSV files
    for link_text in link_texts:
        # Construct the filename based on the team name and link text
        filename = f"{team['name'].replace(' ', '_')}_{link_text.replace(' ', '_')}_Table_4.csv"
        filepath = os.path.join(output_directory, filename)

        # Load the CSV file into a DataFrame
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            print(f"Loaded {filename} with shape {df.shape}")

            # If this is the first file, keep the "Result" column
            if combined_df is None:
                combined_df = df  # Initialize with the first DataFrame
            else:
                # Drop the "Result" column from the new DataFrame before merging
                df = df.drop(columns=["Result", "Opponent"])
                # Merge the data horizontally on TeamNM, Date, and Opponent
                merge_columns = ["TeamNM", "Date"]
                combined_df = pd.merge(combined_df, df, on=merge_columns, how="outer")
        else:
            print(f"File {filename} not found.")

    # Step 5: Save the combined DataFrame for the team
    if combined_df is not None:
        combined_filename = f"{team['name'].replace(' ', '_')}_Combined.csv"
        combined_filepath = os.path.join(output_directory, combined_filename)
        combined_df.to_csv(combined_filepath, index=False)
        print(f"Combined file saved as {combined_filename} with shape {combined_df.shape}")
    else:
        print(f"No data to combine for team {team['name']}.")
