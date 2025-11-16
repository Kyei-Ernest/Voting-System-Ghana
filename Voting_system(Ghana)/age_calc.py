import math
from datetime import datetime

def age(date_of_birth):
    """
    Calculate the age in years based on the date of birth.
    
    Parameters:
    date_of_birth (datetime): The date of birth of the individual.

    Returns:
    int: Age in completed years.
    """
    now = datetime.now()
    delta = now - date_of_birth
    age_years = delta.days / 365.25  # more precise considering leap years
    return math.floor(age_years)
