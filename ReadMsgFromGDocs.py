''' 
Title: Decoding a Secret Message 
Author: Matt Davies
Date: April 22, 2025

Pre-requisits: 
- Make sure you enable Google Docs API key for your google
account for the specific project.
- Make sure you make a credentials.json file in this directory 
that allows the API to work.
- Make sure you give editior access using the share button to 
python-api@tutorial-gdocs.iam.gserviceaccount.com which is given
in the Google docs API dashboard.
- Make sure your document has correct format for a secret message.

Description:
This program untilizes Google Docs API to extract cells from a users private
document that has a table with symbols and associated x and y coordinates for the
given symbol. This program parses each symbol with its xy-coordinates 
and then plots each symbol on a 2D-plane revealing a secret message.
'''

import os.path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# The ID of the private Google Docs document
DOCUMENT_ID = "1aaG1NfQZOua69XbBsqrWx0KgXwN0oFWTFj0A4go5scg"

# Define the scopes for the Google Docs API
scopes = ["https://www.googleapis.com/auth/documents.readonly"]

# Path to the service account credentials file
SERVICE_ACCOUNT_FILE = "/Users/mattdavies/Desktop/Projects/Python/GoogleDocsAPI/credentials.json"

# Authenticate using the service account
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)

# Build the service object for Google Docs API
service = build('docs', 'v1', credentials=creds)

def get_data_from_doc():
    try:
        # Fetch the document's content
        document = service.documents().get(documentId=DOCUMENT_ID).execute()
        print("Document fetched successfully.")

        # Extract the table data from the document
        tables = document.get('body').get('content')
        data = []

        for element in tables:
            if 'table' in element:   # 'Table' is a keyword for the API
                rows = element['table']['tableRows']
                for row in rows:
                    row_data = []
                    cells = row['tableCells']
                    for cell in cells:
                        text_elements = cell.get('content', [])
                        for text_element in text_elements:
                            if 'paragraph' in text_element:
                                for paragraph_element in text_element['paragraph']['elements']:
                                    if 'textRun' in paragraph_element:
                                        text = paragraph_element['textRun']['content'].strip()
                                        if text:
                                            row_data.append(text)
                                           # print(f"Cell text: '{text}'")
                    if len(row_data) == 3:
                        try:
                            # Try both formats: [x, y, char] and [x, char, y]
                            if row_data[1] in ['█', '░', '▀']:
                                x = int(row_data[0])
                                char = row_data[1]
                                y = int(row_data[2])
                            elif row_data[2] in ['█', '░', '▀']:
                                x = int(row_data[0])
                                y = int(row_data[1])
                                char = row_data[2]
                            else:
                                raise ValueError("Invalid character format")
                            
                            data.append((x, y, char))
                           # print(f"Extracted: x={x}, y={y}, char={char}")
                        except ValueError:
                            print(f"Skipping invalid row: {row_data}")
        print(f"Total data extracted: {len(data)} entries.")
        return data
    except HttpError as err:
        print(f"An error occurred: {err}")
        return []

# Function to print the 2D grid
def print_grid(grid):
    print(f"Decoded Secret Message: \n")
    for row in grid:
        if all(cell == ' ' for cell in row):
            continue  # Skip this row (you could also remove it if you're modifying the grid)
        
        for item in row:
            if item in ['█', '░']:
                print(item, end="")
            else:
                print('', end=" ")  # Notice the space in the else clause
        print()


# Convert the data array of tuples into a grid and insert the whitespace where needed
# symbols are plotted at valid xy-coordinates
    # Convert the data array of tuples into a grid and insert the whitespace where needed
    # symbols are plotted at valid xy-coordinates
def convert_data_to_grid(data):
    if not data:
        return []
    max_x = max(x for x, y, _ in data) + 1   # These lines figure out how wide and tall the grid needs to be.
    max_y = max(y for x, y, _ in data) + 1
    grid = [[' ' for _ in range(max_x)] for _ in range(max_y)]
    for x, y, char in data:
        grid[y][x] = char
    return grid

def main():
    data = get_data_from_doc()
    if data:
        grid = convert_data_to_grid(data)
        print_grid(grid)
    else:
        print("No valid data found.")

if __name__ == "__main__":
    main()
