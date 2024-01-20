import csv
from datetime import datetime

file_path = '/home/john/Desktop/library_new.csv'
column_name = 'Date Read'

date_added_column = 'Date Added'
date_read_column = 'Date Read'
# Dictionary to store converted datetime values
converted_dates = {}

default_date = '1970-01-01'

with open(file_path, newline='') as file:
    reader = csv.DictReader(file)

    for row in reader:
        # Convert 'Date Added' column
        datetime_added_str = row.get(date_added_column, '')
        try:
            if datetime_added_str:
                formatted_datetime_added = datetime.strptime(datetime_added_str, '%Y/%m/%d').strftime('%Y-%m-%d')
            else:
                formatted_datetime_added = default_date
        except ValueError:
            formatted_datetime_added = default_date

        # Convert 'Date Read' column
        datetime_read_str = row.get(date_read_column, '')
        try:
            if datetime_read_str:
                formatted_datetime_read = datetime.strptime(datetime_read_str, '%Y/%m/%d').strftime('%Y-%m-%d')
            else:
                formatted_datetime_read = default_date
        except ValueError:
            formatted_datetime_read = default_date

        print(f"{date_read_column}: {formatted_datetime_read}")

# Now you can access the converted datetime values using converted_dates dictionary
print("Converted Date Values:")
print(converted_dates)