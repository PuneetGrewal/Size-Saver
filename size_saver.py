import csv
import subprocess
import pandas as pd
import re
from bs4 import BeautifulSoup

# Creates initial CSV file with ticket numbers
def create_csv():

    start_value = 7550
    end_value = 7600
    numbers = list(range(start_value, end_value + 1))
    csv_file = "test.csv"

    with open(csv_file, mode = 'w', newline='') as file:

        writer  = csv.writer(file)
        writer.writerow(["Name"])

        for i in numbers:
            writer.writerow([i])

    print("CSV File has been created")

def saver():

    csv_file = 'test.csv'
    df = pd.read_csv(csv_file)
    numbers = []

    with open(csv_file, 'r') as file:

        reader = csv.reader(file)
        next(reader)

        for row in reader:
            number = row[0]
            numbers.append(number)


    url = "REMOVED FOR PRIVACY"

    urls = [f"{url}{number}" for number in numbers]

    for url in urls:

        ticket_number = url.split("/")[-1]

        wget_command = ["wget", "--no-check-certificate", "--http-user=REMOVED", "--http-password=REMOVED", "--auth-no-challenge", "-q", url]

        try:

            output = subprocess.check_output(wget_command, stderr=subprocess.STDOUT, text=True)
            print(output)

        except subprocess.CalledProcessError as e:
            print("File not found for" + url )
            df = df[df['Name'] != int(ticket_number)]

    df.to_csv(csv_file, index=False)

    print("All html files have been saved")

def parser():

    csv_file1 = 'test.csv'

    numbers = []

    results_dfs = []

    with open(csv_file1, 'r') as file:

        reader = csv.reader(file)
        next(reader)

        for row in reader:
            number = row[0]
            numbers.append(number)


    for html_file_name in numbers:

    # Read the local HTML file

        with open(html_file_name, "r", encoding="utf-8") as html_file:
                html_content = html_file.read()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all <span> elements with class "size"
        size_elements = soup.find_all('span', class_='size')

        # Initialize variables to count the number of attachments and calculate the total size
        attachment_count = 0
        total_size = 0
        largest_attachment_size = 0

        # Loop through the found size elements
        for size_element in size_elements:
            # Use a regular expression to extract the size value in parentheses
            match = re.search(r'\(([\d.]+ [KMGT]B)\)', size_element.get_text())
            if match:
                attachment_count += 1
                size_text = match.group(1)

                # Parse the size text to extract the numeric value and unit
                size_value, size_unit = size_text.split()
                size_value = float(size_value)

                # Convert the size to a common unit (e.g., MB)
                if size_unit == "KB":
                    size_value /= 1024
                elif size_unit == "GB":
                    size_value *= 1024
                elif size_unit == "TB":
                    size_value *= 1024**2

                total_size += size_value
                largest_attachment_size = max(largest_attachment_size, size_value)

        largest_attachment_size = format(largest_attachment_size, '.2f')

        result_df = pd.DataFrame({"Name": [html_file_name],
                                "Number of Attachments": [attachment_count],
                                "Total Size (MB)": [total_size],
                                "Largest Attachment Size (MB)": [largest_attachment_size]})

        results_dfs.append(result_df)

    #print(results_dfs)

    existing_data = pd.read_csv("test.csv")

    existing_data["Name"] = existing_data["Name"].astype(str)

    #print(existing_data)

    merged_data = existing_data.merge(pd.concat(results_dfs, ignore_index=True), left_on="Name",right_on="Name", how="inner")

    merged_data.to_csv("merged.csv", index=False)

    # Read the CSV file into a DataFrame, skipping the header row
    df = pd.read_csv('merged.csv')

    # Sort the DataFrame by the 13th column
    sorted_df = df.sort_values(by=df.columns[3], ascending=False)

    # Save the sorted DataFrame back to a CSV file without the header row
    sorted_df.to_csv('sorted_file.csv', index=False)

    # Read the CSV file into a DataFrame
    df = pd.read_csv('sorted_file.csv')

    # Modify the values in the first column by adding a prefix (e.g., 'www.google.com/')
    df['Name'] = 'REMOVED' + df['Name'].astype(str)

    # Save the modified DataFrame back to a CSV file
    df.to_csv('final.csv', index=False)

    print("Results saved to final.csv")


def main():
    create_csv()
    saver()
    parser()

if __name__ == "__main__":
    main()
