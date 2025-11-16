import random
import string
from datetime import datetime
import mysql.connector
import bcrypt

from age_calc import age
import mysql_value_checker as vc
import mysql_delete as de


#                   DATABASE CONFIG + HELPERS

DB1 = {
    'user': 'root',
    'password': 'admin123',
    'host': 'localhost',
    'database': '<database_name>'
}

DB2 = {
    'user': 'root',
    'password': 'admin123',
    'host': 'localhost',
    'database': '<database_name>'
}


def get_connection(config):
    """Returns a database connection + cursor."""
    conn = mysql.connector.connect(**config)
    cur = conn.cursor(buffered=True)
    return conn, cur


def random_id(length=8):
    """Generate a random voter ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def hash_password(password: str):
    """Return a bcrypt hashed password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt)


def parse_date(date_str):
    """Converts dd/mm/yyyy into a MySQL format date."""
    try:
        python_date = datetime.strptime(date_str, "%d/%m/%Y")
        mysql_date = python_date.strftime("%Y-%m-%d")
        return python_date, mysql_date
    except ValueError:
        return None, None


#                 VOTER REGISTRATION CLASS

class RegisterVoter:
    def __init__(self, voter_id, name, dob, contact, email,
                 personal_id, occupation, constituency,
                 password, confirm):

        self.voter_id = voter_id
        self.name = name
        self.dob = dob
        self.contact = contact
        self.email = email
        self.personal_id = personal_id
        self.occupation = occupation
        self.constituency = constituency
        self.password = password
        self.confirm = confirm

        self.age = 0

        self.conn, self.cur = get_connection(DB1)

    # ---------------- AGE CALCULATION -------------------

    def calculate_age(self):
        python_date, _ = parse_date(self.dob)

        if not python_date:
            print("❌ Invalid date format. Use dd/mm/yyyy.")
            return False

        self.age = age(python_date)
        return True

    # ---------------- VALIDATION -------------------------

    def validate(self):
        """Validates voter info (no recursion)."""

        # ID already exists
        if vc.check_value_exists(DB1, "voterinfo", "voter_id", self.voter_id):
            print("⚠ This voter ID already exists. Generating a new one...")
            self.voter_id = random_id()

        if self.age < 18:
            print("❌ You must be at least 18 years old to register.")
            return False

        if not self.name.strip():
            print("❌ Name cannot be empty.")
            return False

        if not vc.check_value_exists(DB2, "ecowas_identity", "personal_id", self.personal_id):
            print("❌ Personal ID does not exist in ECOWAS database.")
            return False

        if not self.occupation.strip():
            print("❌ Occupation is required.")
            return False

        if len(self.contact) != 10 or not self.contact.isdigit():
            print("❌ Contact must be exactly 10 digits.")
            return False

        if not vc.check_value_exists(DB1, "members_of_parliament", "constituency", self.constituency):
            print("❌ Constituency does not exist.")
            return False

        if self.password != self.confirm:
            print("❌ Passwords do not match.")
            return False

        if len(self.password) < 10:
            print("❌ Password must be at least 10 characters long.")
            return False

        return True

    # ---------------- SAVE TO DATABASE --------------------

    def save(self):
        python_date, mysql_date = parse_date(self.dob)
        hashed = hash_password(self.password)

        try:
            sql = """
                INSERT INTO voterinfo
                (voter_id, name, contact, email, date_of_birth, personal_id,
                 occupation, constituency, voted)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            self.cur.execute(sql, (
                self.voter_id, self.name, self.contact, self.email,
                mysql_date, self.personal_id, self.occupation,
                self.constituency, 0
            ))
            self.conn.commit()

            sql2 = "INSERT INTO pass_table (voter_id, password) VALUES (%s, %s)"
            self.cur.execute(sql2, (self.voter_id, hashed))
            self.conn.commit()

            print("\n✔ REGISTRATION SUCCESSFUL!")
            print("--------------------------------")
            print(f"Voter ID:      {self.voter_id}")
            print(f"Name:          {self.name}")
            print(f"Age:           {self.age}")
            print(f"Constituency:  {self.constituency}")
            print("--------------------------------")

        except mysql.connector.Error as err:
            self.conn.rollback()
            print("❌ Database Error:", err)


#              PRESIDENT REGISTRATION CLASS

class RegisterPresident:
    def __init__(self, party, name):
        self.party = party
        self.name = name
        self.conn, self.cur = get_connection(DB1)

    def save(self):
        try:
            sql = "INSERT INTO presidents (political_party, presidential_candidate_name) VALUES (%s, %s)"
            self.cur.execute(sql, (self.party, self.name))

            alter = f"ALTER TABLE members_of_parliament ADD COLUMN {self.party} VARCHAR(255)"
            self.cur.execute(alter)

            self.conn.commit()
            print("✔ Presidential candidate registered.")

        except mysql.connector.Error as err:
            print("❌ Error:", err)
            self.conn.rollback()


# ============================================================
#              PARLIAMENTARY REGISTRATION CLASS
# ============================================================

class RegisterMP:
    def __init__(self, constituency):
        self.constituency = constituency
        self.conn, self.cur = get_connection(DB1)

    def save_constituency(self):
        try:
            self.cur.execute(
                "SELECT constituency FROM members_of_parliament WHERE constituency = %s",
                (self.constituency,)
            )
            result = self.cur.fetchone()

            if not result:
                self.cur.execute(
                    "INSERT INTO members_of_parliament (constituency) VALUES (%s)",
                    (self.constituency,)
                )
                self.conn.commit()
                print("✔ Constituency added.")
            else:
                print("⚠ Constituency already exists.")

        except mysql.connector.Error as err:
            print("❌ Error:", err)
            self.conn.rollback()


# ============================================================
#                     MENU SYSTEMS
# ============================================================

def start_voter_registration_process():
    try:
        while True:
            choice = input("""
======== VOTER REGISTRATION ========
1. Register Voter
2. Exit
Choose: """)

            if choice == "1":
                voter_id = random_id()
                name = input("Full Name: ")
                dob = input("Date of Birth (dd/mm/yyyy): ")
                contact = input("Contact (10 digits): ")
                email = input("Email: ")
                pid = input("Personal ID: ")
                occupation = input("Occupation: ")
                constituency = input("Constituency: ")
                password = input("Password: ")
                confirm = input("Confirm Password: ")

                voter = RegisterVoter(
                    voter_id, name, dob, contact, email,
                    pid, occupation, constituency,
                    password, confirm
                )

                if voter.calculate_age() and voter.validate():
                    voter.save()

            elif choice == "2":
                print("Exiting voter registration...")
                break

            else:
                print("❌ Invalid choice. Try again.")

    except Exception as e:
        print("❌ Error:", e)


def start_other_registration():
    try:
        while True:
            choice = input("""
======== ADMIN REGISTRATION ========
1. Add Presidential Candidate
2. Add Constituency
3. Exit
Choose: """)

            if choice == "1":
                party = input("Political Party: ")
                name = input("Presidential Candidate Name: ")

                if vc.check_value_exists(DB1, "presidents", "political_party", party):
                    print("❌ Party already registered.")
                else:
                    president = RegisterPresident(party, name)
                    president.save()

            elif choice == "2":
                const_name = input("Constituency Name: ")
                mp = RegisterMP(const_name)
                mp.save_constituency()

            elif choice == "3":
                print("Exiting...")
                break

            else:
                print("❌ Invalid choice.")

    except Exception as e:
        print("❌ Error:", e)


# ============================================================
#                  MAIN PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":
    while True:
        main_choice = input("""
=========== MAIN MENU ===========
1. Voter Registration
2. Other Registrations (Admin)
3. Exit
Choose: """)

        if main_choice == "1":
            start_voter_registration_process()
        elif main_choice == "2":
            start_other_registration()
        elif main_choice == "3":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice.")
