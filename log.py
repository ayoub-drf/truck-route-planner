
import datetime
from pprint import pprint

data = [
    [
        {
            "driving": [
                {"name": "break", "hours": 0.5},
                {"name": "driving", "hours": 14.462555555555555},
                {"name": "off-duty", "hours": 10},
            ],
            "miles": 604.1809576963001,
            "date": datetime.datetime(2025, 4, 2, 5, 2, 45, 772172),
        }
    ],
    [
        {
            "driving": [
                {"name": "pickup", "hours": 0.5},
                {"name": "break", "hours": 0.5},
                {"name": "fueling", "hours": 0.25},
                {"name": "driving", "hours": 4.299972222222223},
                {"name": "off-duty", "hours": 10},
            ],
            "miles": 476.8670107643,
            "date": datetime.datetime(2025, 4, 3, 5, 2, 45, 772172),
        }
    ],
    [
        {
            "driving": [
                {"name": "34-Hour Restart", "hours": 34},
                {"name": "dropoff", "hours": 0.5},
                {"name": "driving", "hours": 17.098944444444445},
            ],
            "miles": 299.4290536495,
            "date": datetime.datetime(2025, 4, 4, 5, 2, 45, 772172),
        }
    ],
    
]


MAX_DRIVING = 11.0
result = []

counter = 0
remaining_driving_hours = 0
while counter < len(data):
    record = data[counter][0]
    driving_results = []
    remaining_break = {}
    for activity in record["driving"]:
        if activity['name'] == "driving":
            total_driving = activity["hours"] + remaining_driving_hours
            if total_driving > MAX_DRIVING:
                remaining_driving_hours = total_driving - MAX_DRIVING
                activity["hours"] = 8
                
                driving_results.append(activity)
                driving_results.append({'hours': 0.5, 'name': 'break'})
                    
                driving_results.append({'name': 'driving', 'hours': 3})
                result.append([
                    {
                        "driving": driving_results
                    }
                ])
                
            else:
                remaining_driving_hours = 0
                driving_results.append({'hours': total_driving, 'name': 'driving'})
                
                result.append([
                    {
                        "driving": driving_results
                    }
                ])
                
            
        else:
            if activity['name'] != "break":
                driving_results.append(activity)
        
    result[-1][0]['miles'] = record["miles"]
    result[-1][0]['date'] = record["date"]
    counter += 1
  
  
if remaining_driving_hours > 0:
    # if remaining_driving_hours > 11:
    x = [
        {
            "driving": [
                {"name": "driving", "hours": remaining_driving_hours},
            ],
            "miles": 0,
            "date": result[-1][0]['date'] + datetime.timedelta(days=1),
        }
    ]
    result.append(x)
    
    print(result)
    
    




