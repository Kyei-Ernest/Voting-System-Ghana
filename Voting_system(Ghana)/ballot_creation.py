import mysql.connector
import mysql_value_checker as vc
from mysql.connector import Error

# Database configurations
db_config_1 = {
    'user': 'root',
    'password': 'admin123',
    'host': 'localhost',
    'database': 'mydb'
}

conn = mysql.connector.connect(**db_config_1)
cur = conn.cursor()


def display_presidents():
    """Display presidential candidates to the voter."""
    try:
        print("** Vote for your preferred presidential candidate **")

        query = """
            SELECT ID, political_party, presidential_candidate_name
            FROM presidents
        """
        cur.execute(query)
        rows = cur.fetchall()

        for id_, party, name in rows:
            print(f"{id_} {party} - {name}")

    except Error as e:
        print(f"Error retrieving presidential candidates: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def display_mp(voter_id):
    """
    Verify voter ID, retrieve the voter’s constituency,
    and display the list of MPs for that constituency.
    """
    try:
        table = 'voterinfo'
        column = 'voter_id'

        # Check if voter ID exists
        voter_exists = vc.check_value_exists(db_config_1, table, column, voter_id)

        if not voter_exists:
            print("Sorry, you have entered an invalid ID. Try again.")
            return

        print("ID successfully verified\n")

        # Get constituency
        query = "SELECT constituency FROM voterinfo WHERE voter_id = %s"
        cur.execute(query, (voter_id,))
        constituencies = cur.fetchall()

        for (constituency_name,) in constituencies:
            print("** Vote for your preferred MP **")

            query_mps = """
                SELECT *
                FROM members_of_parliament
                WHERE constituency = %s
            """
            cur.execute(query_mps, (constituency_name,))
            mps = cur.fetchone()

            if not mps:
                print(f"No MPs found for constituency {constituency_name}")
                continue

            # Display all MP names except the first two columns (likely ID & constituency)
            count = 1
            for mp in mps[2:]:  # skip the first two fields
                if mp is not None:
                    print(count, mp)
                    count += 1

    except Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
