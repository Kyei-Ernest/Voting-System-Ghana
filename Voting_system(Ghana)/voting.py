import ballot_creation as bc
import mysql.connector
import bcrypt

pc = bc

# Database connection
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="admin123",
    database="mydb"
)
cur = conn.cursor()

voters_id = ""


# PASSWORD VERIFICATION
def verify_password(stored_password, provided_password):
    """Compare password hash with provided password"""
    return bcrypt.checkpw(provided_password.encode(), stored_password)


# VOTE FOR MP
def vote_mp():
    global voters_id
    voters_id = input("Enter voter ID: ")

    # Check if voter has voted already
    votesql = "SELECT voted FROM voterinfo WHERE voter_id = %s"
    cur.execute(votesql, (voters_id,))
    result = cur.fetchone()

    if not result:
        print("Invalid voter ID")
        return

    voted_already = result[0]

    if not voted_already:
        # Ask for password
        password = input("Enter password: ")

        pass_query = "SELECT password FROM pass_table WHERE voter_id = %s"
        cur.execute(pass_query, (voters_id,))
        pw = cur.fetchone()

        if not pw:
            print("Password not found for this voter ID")
            return

        stored_hash = pw[0].encode("utf-8")

        # Verify password
        if verify_password(stored_hash, password):
            # Display MP candidates
            bc.file_existence_and_mpdisplay(voters_id)

            voter_choice_mp = input("Cast vote ->> ")

            # Update MP vote
            sql = "UPDATE voterinfo SET mp_vote = %s WHERE voter_id = %s"
            cur.execute(sql, (voter_choice_mp, voters_id))
            conn.commit()

            # Continue to presidential vote
            return vote_president()

        else:
            print("Incorrect password!")
            return

    else:
        print("Sorry, but it seems you have already cast your vote.")


# VOTE FOR PRESIDENT
def vote_president():
    try:
        pc.display_presidents()

        voter_choice_president = input("Cast vote ->> ").strip()

        if not voter_choice_president:
            raise ValueError("Invalid vote. Candidate ID required.")

        # Update presidential vote
        sql = "UPDATE voterinfo SET president_vote = %s WHERE voter_id = %s"
        cur.execute(sql, (voter_choice_president, voters_id))

        # Mark as voted
        sql2 = "UPDATE voterinfo SET voted = 1 WHERE voter_id = %s"
        cur.execute(sql2, (voters_id,))

        conn.commit()
        print("Vote successfully cast!")

    except ValueError as ve:
        print(f"Error: {ve}")

    except mysql.connector.Error as db_err:
        print(f"Database Error: {db_err}")
        conn.rollback()

    except Exception as e:
        print(f"Unexpected error: {e}")
        conn.rollback()


# VOTER CONFIRMATION
def display_poll():
    while True:
        try:
            voter_entry = input(
                "Are you sure you want to vote now?\n"
                "1. Yes\n"
                "2. No\n"
            ).strip()

            if voter_entry == "1":
                vote_mp()
                break

            elif voter_entry == "2":
                print("You have chosen not to vote at this time.")
                break

            else:
                raise ValueError("Invalid entry. Please enter 1 or 2.")

        except ValueError as ve:
            print(f"Error: {ve}")

        except Exception as e:
            print(f"Unexpected error: {e}")
