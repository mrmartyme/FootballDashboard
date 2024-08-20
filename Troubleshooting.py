import pandas as pd

# Load the Schedule2024.csv without parsing dates to inspect column names
schedule_df = pd.read_csv(r'Schedule2024.csv')

# Display the column names
print(schedule_df.columns)
