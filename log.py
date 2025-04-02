[
    [
        {
            "driving": [
                {"name": "break", "hours": 0.5},
                {"name": "driving", "hours": 14.462555555555555},
                {"name": "off-duty", "hours": 10},
            ],
            "miles": 604.1809576963001,
            "date": "",
        }
    ],
    [
        {
            "driving": [
                {"name": "pickup", "hours": 0.5},
                {"name": "break", "hours": 0.5},
                {"name": "fueling", "hours": 0.25},
                {"name": "driving", "hours": 11.299972222222223},
                {"name": "off-duty", "hours": 10},
            ],
            "miles": 476.8670107643,
        }
    ],
    [
        {
            "driving": [
                {"name": "34-Hour Restart", "hours": 34},
                {"name": "dropoff", "hours": 0.5},
                {"name": "driving", "hours": 7.098944444444445},
            ],
            "miles": 299.4290536495,
        }
    ],
]



from datetime import datetime, timedelta

# Create a date from a string (format: month/day/year)
current_date = datetime.now()
formatted_date = current_date.strftime("%m/%d/%y")
date_str = formatted_date
date_obj = datetime.strptime(date_str, "%m/%d/%y")
print("Original date:", date_obj.strftime("%m/%d/%y"))

# Increase the date by a certain number of days (e.g., 5 days)
days_to_add = 5
new_date = date_obj + timedelta(days=days_to_add)
print("New date after adding", days_to_add, "days:", new_date.strftime("%m/%d/%y"))
