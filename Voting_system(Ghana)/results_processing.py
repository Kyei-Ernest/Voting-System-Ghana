import mysql.connector


#               DATABASE CONNECTION

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="admin123",
    database="mydb"
)
cur = conn.cursor()


#               PRESIDENTIAL VOTE COUNT

def president_vote_count():
    try:
        # Get list of presidents
        cur.execute("SELECT ID FROM presidents")
        presidents = cur.fetchall()

        for president in presidents:
            president_id = president[0]

            # Count votes for the president
            cur.execute(
                "SELECT COUNT(*) FROM voterinfo WHERE president_vote = %s",
                (president_id,)
            )
            votes_count = cur.fetchone()[0]

            # Update number_of_votes
            cur.execute(
                "UPDATE presidents SET number_of_votes = %s WHERE ID = %s",
                (votes_count, president_id)
            )
            conn.commit()

            # Total votes cast
            cur.execute("SELECT COUNT(*) FROM voterinfo WHERE voted = '1'")
            total_votes = cur.fetchone()[0]

            # Calculate percentage
            percent = round((votes_count / total_votes) * 100, 1) if total_votes > 0 else 0

            # Update percentage
            cur.execute(
                "UPDATE presidents SET vote_percentage = %s WHERE ID = %s",
                (f"{percent}%", president_id)
            )
            conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")


#          CHECK & CREATE MP TABLE IF NOT EXISTS

def create_mp_table(constituency):
    try:
        # Check if constituency exists in MP table
        cur.execute(
            "SELECT * FROM members_of_parliament WHERE constituency = %s",
            (constituency,)
        )
        row = cur.fetchone()

        if row is None:
            print(f"No MPs registered for constituency '{constituency}'.")
            return []

        data = list(row)
        mp_list = data[2:]  # MPs start from column 3

        # Create table if it does not exist
        cur.execute(f"SHOW TABLES LIKE '{constituency}'")
        exists = cur.fetchone()

        if not exists:
            cur.execute(
                f"CREATE TABLE {constituency} ("
                "id INT AUTO_INCREMENT PRIMARY KEY, "
                "name VARCHAR(255), "
                "number_of_votes INT DEFAULT 0)"
            )
            conn.commit()

        # Insert MPs into table (ignore duplicates)
        for name in mp_list:
            if name:
                insert_mp_name(constituency, name)

        return mp_list

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return []


def insert_mp_name(table, name):
    # Check if already exists
    cur.execute(
        f"SELECT EXISTS(SELECT 1 FROM {table} WHERE name = %s)",
        (name,)
    )
    exists = cur.fetchone()[0]

    if not exists:
        cur.execute(
            f"INSERT INTO {table} (name) VALUES (%s)",
            (name,)
        )
        conn.commit()


#                  MP VOTE COUNTING

def insert_mp_votes(constituency, mp_id):
    try:
        # Count votes for MP
        cur.execute(
            "SELECT COUNT(*) FROM voterinfo "
            "WHERE constituency = %s AND mp_vote = %s",
            (constituency, mp_id)
        )
        votes = cur.fetchone()[0]

        # Update
        cur.execute(
            f"UPDATE {constituency} SET number_of_votes = %s WHERE id = %s",
            (votes, mp_id)
        )
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()


def mp_vote_count():
    cur.execute("SELECT constituency FROM members_of_parliament")
    constituencies = cur.fetchall()

    last_constituency = None

    for (constituency,) in constituencies:
        last_constituency = constituency

        # Create MP table & insert names
        create_mp_table(constituency)

        # Get MPs (IDs) from the constituency table
        cur.execute(f"SELECT id FROM {constituency}")
        mp_ids = cur.fetchall()

        for (mp_id,) in mp_ids:
            insert_mp_votes(constituency, mp_id)

    return last_constituency


#                  DISPLAY RESULTS

def display_results():
    try:
        print("\n--- PRESIDENTIAL RESULTS ---")
        cur.execute("SELECT * FROM presidents")
        for row in cur.fetchall():
            print(f"{row[0]} | {row[1]} - {row[2]} | Votes: {row[3]} | {row[4]}")

        # MP results
        constituency = mp_vote_count()

        if constituency:
            print(f"\n--- MP RESULTS ({constituency}) ---")
            cur.execute(f"SELECT * FROM {constituency}")
            mp_rows = cur.fetchall()

            for row in mp_rows:
                print(f"{row[0]} | {row[1]} | Votes: {row[2]}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cur.close()
        conn.close()


#                  EXECUTE WHEN RUN

if __name__ == "__main__":
    president_vote_count()
    display_results()
