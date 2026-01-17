import mysql_value_checker as vc
from database import DatabaseManager

def display_presidents():
    """Display presidential candidates to voter"""
    try:
        print("** Vote for your preferred presidential candidate **")
        with DatabaseManager() as db:
            sql1 = "SELECT ID, political_party, presidential_candidate_name FROM presidents"
            db.execute_query(sql1)
            myr1 = db.fetch_all()
            for x, y, z in myr1:
                print(f"{x} {y} - {z}")
    except Exception as e:
        print(f"Error while retrieving presidential candidates: {e}")


def display_mp(voter_id):
    """Check the existence of the voter file and display MPs for the voter's constituency."""
    try:
        # Check if the voter ID exists in the database
        voterid_exists = vc.check_value_exists(table='voterinfo', column='voter_id', user_input=voter_id)

        if voterid_exists:
            print("ID successfully verified\n")

            with DatabaseManager() as db:
                # Retrieve the constituency for the given voter ID
                query_constituency = "SELECT constituency FROM voterinfo WHERE voter_id = %s"
                db.execute_query(query_constituency, (voter_id,))
                constituencies = db.fetch_all()

                # For each retrieved constituency, display MPs
                for constituency in constituencies:
                    constituency_name = constituency[0]
                    print(f"** Vote for your preferred MP for {constituency_name} **")

                    query_mps = "SELECT * FROM members_of_parliament WHERE constituency = %s"
                    db.execute_query(query_mps, (constituency_name,))
                    # Assuming logic: fetch ONE row which contains columns for MPs?
                    # The schema suggests 'members_of_parliament' might be pivoting columns (party names as columns?)
                    # Based on existing code logic: `mps = cur.fetchone()` and iterating it.
                    mps = db.fetch_one()
                    
                    if mps:
                        # Original logic skipped first 2 columns (id, constituency likely) -> index 0, 1
                        # The iteration `count = -2` and `if count > 0` implies skipping first 3 items?
                        # Let's clean this up. Assuming mps is a tuple (id, constituency, mp1, mp2...)
                        
                        # Get column names to make it clearer?
                        # For now, replicating original behavior but safer.
                        # Original: count starts at -2. 
                        # Item 0 (id): count=-1
                        # Item 1 (constituency): count=0
                        # Item 2 (first candidate): count=1 -> Print
                        
                        count = 0
                        # We skip ID and Constituency which are likely index 0 and 1
                        candidates = mps[2:] 
                        for mp in candidates:
                            count += 1
                            if mp:
                                print(f"{count}. {mp}")
                    else:
                        print(f"No MPs found for constituency {constituency_name}")

        else:
            print("Sorry, you have entered an invalid id. Try again")
            
    except Exception as e:
        print(f"Error in display_mp: {e}")
