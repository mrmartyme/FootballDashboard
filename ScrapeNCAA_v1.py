import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Step 1: Load the link texts from the CSV file and filter for active links
link_texts_df = pd.read_csv('link_texts.csv')
link_texts = link_texts_df[link_texts_df['active'] == 1]['link_text'].tolist()

# Step 2: Load the teams from the CSV file and filter for active teams
teams_df = pd.read_csv('teams.csv')
teams = teams_df[teams_df['active'] == 1].to_dict(orient='records')

# Step 3: Set up Edge WebDriver
edge_options = Options()
edge_options.use_chromium = True  # Ensure Chromium is used
edge_driver_path = "C:/Users/mhump/Downloads/edgedriver_win64/msedgedriver.exe"

service = EdgeService(executable_path=edge_driver_path)
driver = webdriver.Edge(service=service, options=edge_options)

# Output: Confirm WebDriver setup
print("Edge WebDriver setup completed.")

# Step 4: Set up the output directory
output_directory = os.path.join(".", "TeamDataFiles")
os.makedirs(output_directory, exist_ok=True)

# Step 5: Loop through each active team
for team in teams:
    # Construct the team-specific URL
    url = f"https://stats.ncaa.org/players/{team['id']}"
    driver.get(url)

    # Output: Confirm navigation
    print(f"Navigated to {url} for team {team['name']}.")

    # Step 6: Loop through each active link text, click, and extract Table 4
    for link_text in link_texts:
        try:
            # Wait until the link is clickable and click it
            navigation_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, link_text))
            )
            navigation_link.click()
            print(f"Clicked on the link: {link_text}")

            # Wait for the new page to load (adjust the condition as needed)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print(f"New page loaded for: {link_text}")

            # Get the new page source
            new_html = driver.page_source
            new_soup = BeautifulSoup(new_html, "html.parser")

            # Find the fourth table and extract the data
            new_tables = new_soup.find_all("table")

            if len(new_tables) >= 4:
                table = new_tables[3]  # Index 3 corresponds to the fourth table (0-based index)

                headers = [header.text.strip() for header in table.find_all('th')]
                rows = table.find_all('tr')

                data = []
                for row in rows:
                    columns = row.find_all('td')

                    # Extract row data
                    row_data = [column.text.strip() for column in columns]
                    if row_data:  # Ensure the row has data
                        data.append(row_data)
                        # Print row data for debugging
                        print(f"Row data: {row_data}")

                # Create a DataFrame from the extracted data
                if data:
                    df = pd.DataFrame(data, columns=headers)

                    # Remove the last two columns
                    df = df.iloc[:, :-2]

                    # Remove rows where the first column (Date) is "Totals" or "Defensive Totals"
                    df = df[~df.iloc[:, 0].isin(["Totals", "Defensive Totals"])]

                    # Insert the team name at the beginning of the DataFrame
                    df.insert(0, "TeamNM", team['name'])

                else:
                    print(f"{link_text} Table 4 has no data.")
                    continue

                # Output: Show the DataFrame shape and the first few rows
                print(f"DataFrame shape: {df.shape}")
                print(df.head())

                # Save the DataFrame to a CSV file named by team name, link text, and table number
                csv_filename = f"{team['name'].replace(' ', '_')}_{link_text.replace(' ', '_')}_Table_4.csv"
                csv_filepath = os.path.join(output_directory, csv_filename)
                df.to_csv(csv_filepath, index=False)

                # Output: Confirm that CSV was saved
                print(f"Table 4 saved as {csv_filepath} for team {team['name']} and link {link_text}.")
            else:
                print(f"Less than 4 tables found on the page for {link_text}.")

            # Optional: Adding a short delay before moving to the next link
            time.sleep(1)

            # Navigate back to the original page to click the next link
            driver.back()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, link_texts[0]))
            )
            print(f"Navigated back to the main page for team {team['name']}.")

        except Exception as e:
            print(f"Error processing {link_text} for team {team['name']}: {e}")

# Step 7: Close the Edge WebDriver
driver.quit()

# Output: Confirm WebDriver closure
print("Edge WebDriver closed.")
