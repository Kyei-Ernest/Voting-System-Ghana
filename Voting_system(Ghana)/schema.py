import mysql.connector
import sys

# ===============================
#   MySQL CREATE TABLE STATEMENTS
# ===============================

create_voterinfo_table = """
CREATE TABLE IF NOT EXISTS voterinfo (
    Voter_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    contact VARCHAR(255),
    email VARCHAR(255),
    personal_id VARCHAR(50),
    occupation VARCHAR(100),
    constituency VARCHAR(100),
    voted BOOLEAN DEFAULT FALSE,
    president_vote VARCHAR(255),
    mp_vote VARCHAR(255),
    password VARCHAR(255)
);
"""

create_president_table = """
CREATE TABLE IF NOT EXISTS presidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    political_party VARCHAR(100),
    presidential_candidate_name VARCHAR(255) NOT NULL,
    number_of_votes INT DEFAULT 0,
    vote_percentage VARCHAR(255)
);
"""

create_mpvotesinfo_table = """
CREATE TABLE IF NOT EXISTS members_of_parliament (
    id INT AUTO_INCREMENT PRIMARY KEY,
    constituency VARCHAR(100)
);
"""

create_pass_table = """
CREATE TABLE IF NOT EXISTS pass_table (
    Voter_id VARCHAR(255),
    password VARCHAR(255),
    PRIMARY KEY (Voter_id),
    FOREIGN KEY (Voter_id) REFERENCES voterinfo(Voter_id)
);
"""

#   DATABASE CREATION PROCESS

dbname = input("Enter database name: ").strip()

if dbname == "":
    print("Your database schema must have a name")
    sys.exit(1)

# Connect to MySQL without specifying a database
try:
    mydb_connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="admin123",  # <-- make sure this is correct
        port=3306
    )
except mysql.connector.Error as err:
    print("Error connecting to MySQL:", err)
    sys.exit(1)

cursor = mydb_connection.cursor()
cursor.execute("SHOW DATABASES")
database_list = [db[0] for db in cursor.fetchall()]

if dbname in database_list:
    print("The database name already exists. Use another unique name instead.")
    sys.exit(1)

# Create the new database
try:
    cursor.execute(f"CREATE DATABASE {dbname} CHARACTER SET utf8 COLLATE utf8_general_ci;")
    print(f"Database '{dbname}' created successfully!")

    # Connect to the new database
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="admin123",  # <-- make sure this matches your MySQL root password
        database=dbname,
        port=3306
    )
    cursor = mydb.cursor()

    # Create tables
    cursor.execute(create_voterinfo_table)
    cursor.execute(create_president_table)
    cursor.execute(create_mpvotesinfo_table)
    cursor.execute(create_pass_table)

    mydb.commit()
    print("Tables created successfully!")

except mysql.connector.Error as err:
    print("Error creating tables:", err)
    sys.exit(1)

finally:
    cursor.close()
    mydb_connection.close()
    if 'mydb' in locals():
        mydb.close()
