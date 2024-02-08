import os
import io
import re
import sqlite3
import argparse
import urllib.request
from pypdf import PdfReader

# Delete the existing SQLite database file if it exists
def db_delete():
    db_file = 'normanpd.db'
    try:
        if os.path.exists(f'resources/{db_file}'):
            os.remove(f'resources/{db_file}')
    except Exception as err:
        print("Error: ", err)


# Fetch incident data from the provided URL
def fetch_incidents(url):
    try:
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (HTML, like Gecko) Chrome/24.0.1312.27 "
                          "Safari/537.17"}
        data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()
        return data
    except Exception as err:
        print("Error: ", err)

# Extract incident records from the fetched PDF data
def extract_incidents(f_data):
    io_data = io.BytesIO(f_data)
    pdf = PdfReader(io_data)

    inc_rec = []
    # Regex pattern for date (MM/DD/YYYY or M/D/YYYY)
    date_pattern = r'\b(?:0?[1-9]|1[0-2])/(?:0?[1-9]|[12][0-9]|3[01])/(?:20\d{2})\b'

    for i_page in range(len(pdf.pages)):
        page = pdf.pages[i_page]
        page_con = page.extract_text()

        # Adjust the extraction for the first page if necessary
        if i_page == 0:
            page_con = page_con[57:-55]

        # Split the content using the date regex, keeping the dates as part of the result
        ext_cont = re.split(f'({date_pattern})', page_con)

        # Reconstruct the incidents with their dates
        inc_con = []
        for i in range(1, len(ext_cont), 2):
            inc_con.append(ext_cont[i] + ext_cont[i + 1])
        # If it's the last page, remove the last line after splitting by date
        if i_page == len(pdf.pages) - 1:
            inc_con = inc_con[:-1]
        # Extract records from the reconstructed text
        for txt in inc_con:
            inc_record = get_inc_details([txt])
            inc_rec.extend(inc_record)

    return inc_rec


# Split incident record into components
def split_record_components(incident):
    components = incident.split()
    _, time, incident_num, *middle, ori = components
    return time, incident_num, middle, ori


# Adjust incident number if it's longer than 13 characters
def adjust_incident_number(inc_num, middle):
    if len(inc_num) > 13:
        return inc_num[:13], [inc_num[13:]] + middle
    return inc_num, middle


# Check if a component is likely to be part of the location
def is_location_component(component):
    return (
            component not in ["MVA", "COP", "EMS", "RAMPMVA"] and
            (component.isdecimal() or component.isupper() or component == "/" or ';' in component or component == '1/2')
    )


# Process middle components of an incident record
def process_middle_components(middle):
    loc, nat = [], []
    for rec in middle:
        if len(nat) == 0 and is_location_component(rec):
            loc.append(rec)
        elif rec in ['HWYMotorist', 'RAMPMotorist']:
            loc.append(rec.split('Motorist')[0])
            nat.append('Motorist')
        elif rec == "RAMPMVA":
            loc.append('RAMP')
            nat.insert(0, 'MVA')
        else:
            nat.append(rec)
    return loc, nat


# Handle a specific edge case in location components
def handle_numeric_edge_case_in_location(loc, nat):
    if loc and loc[-1].isdigit() and len(loc[-1]) != 1:
        nat.insert(0, loc.pop())
    return loc, nat


# Create an incident record dictionary
def create_inc_record(time, inc_num, loc, nat, ori):
    return {
        "inc_time": time,
        "inc_number": inc_num,
        "inc_location": " ".join(loc),
        "inc_nature": " ".join(nat),
        "inc_ori": ori,
    }


# Get details of incident records
def get_inc_details(pg_con):
    inc_list = []
    for inc in pg_con:
        time, inc_num, middle, ori = split_record_components(inc)
        inc_num, middle = adjust_incident_number(inc_num, middle)
        loc, nat = process_middle_components(middle)
        loc, nat = handle_numeric_edge_case_in_location(loc, nat)
        inc_record = create_inc_record(time, inc_num, loc, nat, ori)
        inc_list.append(inc_record)
    return inc_list


# Create SQLite database
def create_db():
    try:
        db_conn = sqlite3.connect('resources/normanpd.db')
        db_cursor = db_conn.cursor()
        query = ''' CREATE TABLE IF NOT EXISTS
                    incidents (
                            incident_time TEXT,
                            incident_number TEXT,
                            incident_location TEXT,
                            nature TEXT,
                            incident_ori TEXT
                        ) '''

        db_cursor.execute(query)
    except Exception as err:
        print("Error: ", err)
    return db_conn


# Populate SQLite database with incident records
def populate_db(db, inc_records):
    db_cursor = db.cursor()
    try:
        for inc in inc_records:
            db_cursor.execute("""INSERT INTO incidents (incident_time, incident_number, incident_location, nature, incident_ori)
                        VALUES(?,?,?,?,?)""",
                              (
                                  inc["inc_time"],
                                  inc["inc_number"],
                                  inc["inc_location"],
                                  inc["inc_nature"],
                                  inc["inc_ori"]
                              ),
                              )
        db.commit()
    except Exception as err:
        print("Error: ", err)


# Print all data from SQLite database
def print_data_from_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('resources/normanpd.db')
        cursor = conn.cursor()
        query = "SELECT * FROM incidents"
        # Select all data from the specified table
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()
        # Print the data
        for row in rows:
            print(row)

    except sqlite3.Error as err:
        print(f"Error reading data from the database: {err}")

    finally:
        # Close the connection
        if conn:
            conn.close()


# Print incident nature statistics
def status(db):
    try:
        db_cursor = db.cursor()
        # Select non-empty natures
        db_cursor.execute('''SELECT nature, COUNT(*) as count 
                       FROM incidents 
                        GROUP BY nature ORDER BY count DESC, nature ASC''')
        all_records = db_cursor.fetchall()
        blank = 0
        for rec in all_records:
            print(f"{rec[0]}|{rec[1]}")

    except Exception as err:
        print("Error: ", err)
    finally:
        db_cursor.close()

#all functions are called in main function 
def main(url):
    db_delete()

    # Download data
    inc_data = fetch_incidents(url)

    # Extract data
    inc_records = extract_incidents(inc_data)

    # Create new database
    db = create_db()
    populate_db(db, inc_records)
    status(db)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True,
                        help="Incident summary url.")

    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)
