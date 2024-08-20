import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
import os

# Define the URL to inspect
url_to_inspect = "https://stats.ncaa.org/players/8105308?year_stat_category_id=15057"

# Set up Edge WebDriver
edge_options = Options()
edge_options.use_chromium = True  # Ensure Chromium is used
edge_driver_path = "C:/Users/mhump/Downloads/edgedriver_win64/msedgedriver.exe"  # Adjust this path as needed

service = EdgeService(executable_path=edge_driver_path)
driver = webdriver.Edge(service=service, options=edge_options)

# Load the URL
driver.get(url_to_inspect)

# Get the page source and parse it with BeautifulSoup
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# Find all tables in the page
tables = soup.find_all("table")

# Output: Number of tables found
print(f"Found {len(tables)} tables on the page.")

# Create an output directory for the CSV files
output_directory = os.path.join(".", "TableExports")
os.makedirs(output_directory, exist_ok=True)

# Loop through each table, convert it to a DataFrame, and save it to a CSV file
for i, table in enumerate(tables):
    # Get headers and rows
    headers = [header.text.strip() for header in table.find_all('th')]
    rows = table.find_all('tr')

    data = []
    for row in rows:
        columns = row.find_all('td')
        row_data = [column.text.strip() for column in columns]
        if row_data:  # Only add rows with data
            data.append(row_data)

    # Create a DataFrame
    df = pd.DataFrame(data, columns=headers if headers else None)

    # Save the DataFrame to a CSV file
    csv_filename = os.path.join(output_directory, f"DataTestTable{i + 1}.csv")
    df.to_csv(csv_filename, index=False)

    # Output: Confirm the file was saved
    print(f"Table {i + 1} saved as {csv_filename}")

# Close the WebDriver
driver.quit()
