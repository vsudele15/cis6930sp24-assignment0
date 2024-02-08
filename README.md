Name: Vaidehi Sudele


ASSIGNMENT DESCRIPTION:
THIS IS ASSIGNMENT 0 IN THE CIS6930 DATA ENGINEERING COURSE. THE ASSIGNMENT FOCUSES ON EXTRACTING DATA. IN THIS ASSIGNMENT GRAB AN INCIDENTS PDF FILE FORM THE NORMAN, OKLAHAMA POLICE DEPARTMENT'S WEBSITE AND THEN EXTRACT THE DATA FROM THIS PDF AND PRINT OUT THE DIFFERENT CATEGORIES OF THE INCIDENTS.


## Demo


https://github.com/vsudele15/cis6930sp24-assignment0/assets/145212301/79f7eaa7-50b3-49ac-8297-765e2e5dccc8



__FUNCTIONS__

1. db_delete(): This function deletes the SQLite database file (normanpd.db) if it exists in the specified directory (resources/).

2. fetch_incidents(url): This function takes a URL as input and retrieves the content from that URL.
It uses urllib.request to make a request to the URL and fetches the data. It returns the fetched data.

3. extract_incidents(f_data): This function takes the fetched data (assumed to be from a PDF file) as input. It utilizes PyPDF2 library to extract text from the PDF. It parses the extracted text to identify incident records, including incident time, number, location, nature, and originating agency. It returns a list of dictionaries, where each dictionary represents an incident record.

4. split_record_components(incident): This function takes an incident record as input and splits it into individual components (time, incident number, middle parts, originating agency).
It returns the separated components.

5. adjust_incident_number(inc_num, middle): This function adjusts the incident number and middle components if the incident number is longer than 13 characters. It returns the adjusted incident number and middle components.

6. is_location_component(component):

This function checks if a component of an incident record is likely to be part of the location information.
It returns a boolean indicating whether the component is likely to be part of the location.

7. create_db(): This function creates a SQLite database (normanpd.db) if it doesn't already exist. It returns a connection to the database.

8. populate_db(db, inc_records): This function populates the SQLite database with the provided incident records. It inserts each incident record into the database. It commits the changes to the database.

9. status(db): This function retrieves and prints the count of incidents grouped by nature from the SQLite database.It executes a SELECT query to count incidents grouped by nature and prints the results.

10. main(url): This is the main function of the script.
It orchestrates the entire process of parsing incident summaries from a URL, creating and populating a database, and printing statistics.
It deletes any existing database, fetches incident data from the provided URL, extracts incident records, creates a database, populates it with incident records, and prints statistics.

11. __name__ == '__main__' block:

This block of code is executed only if the script is run directly (not imported as a module).
It parses command-line arguments using argparse, specifically the incident summary URL.
It calls the main() function with the provided URL.

__DATABASE DEVELOPEMENT__
1. Create the Incidents Table (createdb()): Execute an SQL statement to create a table named "incidents" in the database.
Define the columns of the table, such as incident_time, incident_number, incident_location, nature, and incident_ori.
Use appropriate data types for each column (e.g., TEXT).

2. Populate the Incidents Table (populatedb(db, inc_records)): For each incident entry in the extracted data:
Construct an SQL INSERT statement to insert the data into the "incidents" table.
Execute the INSERT statement using the cursor.
Commit the changes to the database.

3. Query and Sort Incident Data (status(db)): Execute an SQL query to get the count of incidents grouped by nature from the "incidents" table.
Sort the results first by count (in descending order) and then alphabetically by nature.

4. Delete the Incidents Table (deletedb()): Execute an SQL statement to drop the "incidents" table if it already exists.
This step is usually performed before creating a new table to avoid conflicts.

__Bugs and Assumptions__

1. It is assumed that the layout of the given pdf will be consistent and will not change.
