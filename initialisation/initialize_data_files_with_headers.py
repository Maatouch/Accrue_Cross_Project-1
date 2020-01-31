import csv
from os import chdir

chdir("..")
chdir("data files")


def initialize_data_files_with_headers():
    with open("success.csv", "w", newline='') as f:
        f_names = ["symbol", "golden", "deaths", "last_update", "number-of-added-dates"]
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=f_names )
        writer.writeheader()

    with open("errors.csv", "w", newline='') as f:
        f_names = ["symbol", "date", "error_type", "error_code"]
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=f_names)
        writer.writeheader()

    with open("update_errors.csv", "w", newline='') as f:
        f_names = ["symbol", "date", "error_type", "error_code"]
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=f_names)
        writer.writeheader()

    with open("update_summary_file.csv", "w", newline='') as f:
        f_names = ['date', 'number_of_processed_symbs', 'number_of_modified_symbs', 'nbr_dates_added', 'nbr_errors']
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=f_names)
        writer.writeheader()
