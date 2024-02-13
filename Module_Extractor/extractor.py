import os
import json
import pandas as pd
from bs4 import BeautifulSoup
from prettytable import PrettyTable

# Function to extract module names from HTML file
def extract_module_names_from_html(html_file_name):
    module_names = []
    try:
        with open(html_file_name, 'r') as html_file:
            soup = BeautifulSoup(html_file, 'html.parser')
            module_summary_table = soup.find('table', id='component_summary')
            if module_summary_table:
                module_rows = module_summary_table.find_all('tr')
                for row in module_rows[1:]:
                    module_name = row.find('td', style="text-align: left")
                    if module_name:
                        module_names.append(module_name.get_text())
    except FileNotFoundError:
        print(f"HTML file '{html_file_name}' not found.")
    except Exception as e:
        print(f"An error occurred while reading HTML file '{html_file_name}': {e}")
    return module_names

# Function to extract module names from JSON file based on the "name" field and "skip" condition
def extract_module_names_from_json(json_file_name):
    module_names = []
    try:
        with open(json_file_name, 'r') as json_file:
            json_data = json.load(json_file)
            for testcase in json_data.get("testcases", []):
                name = testcase.get('name')
                skip = testcase.get('skip', False)
                if name and not skip:
                    module_names.append(name)
    except FileNotFoundError:
        print(f"JSON file '{json_file_name}' not found.")
    except Exception as e:
        print(f"An error occurred while reading JSON file '{json_file_name}': {e}")
    return module_names

# Get file names from the user
json_file_name = input("Enter the JSON file name (e.g., data.json): ")
html_file_name = input("Enter the HTML file name (e.g., myfile.html): ")

# Check if files exist and handle errors
if os.path.exists(json_file_name) and os.path.exists(html_file_name):
    # Extract module names from HTML
    html_module_names = extract_module_names_from_html(html_file_name)
    
    # Extract module names from JSON based on the "name" field and "skip" condition
    json_module_names = extract_module_names_from_json(json_file_name)
    
    # Create a DataFrame with aligned module names
    max_length = max(len(json_module_names), len(html_module_names))
    json_module_names += [""] * (max_length - len(json_module_names))
    html_module_names += [""] * (max_length - len(html_module_names))
    
    # Create a PrettyTable for printing the table
    table = PrettyTable()
    table.field_names = ["JSON Modules", "HTML Modules", "Missing Modules"]
    
    for json_module, html_module in zip(json_module_names, html_module_names):
        table.add_row([json_module, html_module, json_module if json_module not in html_module_names else ""])
    
    # Print the table
    print(table)
    
    # Save the DataFrame as a CSV file
    df = pd.DataFrame({
        "JSON Modules": json_module_names,
        "HTML Modules": html_module_names
    })
    df['Missing Modules'] = [module if module not in html_module_names else "" for module in json_module_names]
    df.to_csv("output.csv", index=False)

    print("Output has been saved to 'output.csv'.")
else:
    print("File not found. Please make sure both files exist in the current directory.")
