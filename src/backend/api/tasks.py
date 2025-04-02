
import polyline
def create_rests_and_stops(route_data):

    result = {}
    number_of_breaks = 0
    number_of_fueling = 0
    number_of_off_duty = 0
    pickup_miles = 0
    dropoff_miles = 0
    

    def miles_to_meters(miles):
        return miles * 1609.34

    def meters_to_miles(meters):
        return meters * 0.000621371

    def seconds_to_hours(seconds):
        return seconds / 3600

    def hours_to_seconds(hours):
        return hours * 3600

    def create_stop_step(stop_type, duration_seconds, prev_way_points, route_geometry=None):
        start_idx = prev_way_points[1]
        
        coord = route_geometry[start_idx]
        offset_lat = 0.0001
        offset_lon = 0.0001
        stop_coord = [coord[0] + offset_lat, coord[1] + offset_lon]
        return {
            "distance": 0,
            "duration": duration_seconds,
            "type": 12,
            "instruction": f"{stop_type} stop",
            "name": "-",
            "way_points": [start_idx, start_idx],
            "stop_coord": stop_coord
        }


    geojson = route_data
    result['bbox'] = geojson['bbox']
    result['metadata'] = geojson['metadata']
    
    routes = geojson.get("routes", [])
    result['routes'] = []
    
    current_cycle_used_secs = hours_to_seconds(44)
    

    log_sheet_result = []
    current_day_log = []
    
    for route in routes:
        fueling_stop_break_tracker = 0
        pickup_tracker = 0
        pickup_tracker_status = False
        dropoff_tracker = 0
        dropoff_tracker_status = False
        eight_hours_driving_rest_tracker = 0
        current_breaks = 0
        max_driving_limit_hour_tracker = 0
        cumulative_on_duty = current_cycle_used_secs
        
        route_summary = route['summary']
        route_bbox = route['bbox']
        route_geometry_decoded = polyline.decode(route['geometry'])
        way_points = route['way_points']
        
        route_obj = {
            "summary": route_summary,
            "bbox": route_bbox,
            "segments": [],
            "geometry": route_geometry_decoded,
            "way_points": way_points,
        }
        
        segments = route['segments']
        for segment in segments:
            segment_distance = segment['distance']
            segment_duration = segment['duration']
            segment_steps = segment['steps']
                        
            segment_obj = {
                "distance": segment_distance,
                "duration": segment_duration,
                "steps": [],
            }
            
            for step in segment_steps:
                # Append current step
                segment_obj["steps"].append(step)
                
                # Accumulate for fueling stops and driving time
                fueling_stop_break_tracker += step["distance"]
                max_driving_limit_hour_tracker += step["duration"]
                
                current_day_log.append({
                    "name": "driving",
                    "hours": seconds_to_hours(step["duration"])
                })                
                
                print('max_driving_limit_hour_tracker ', seconds_to_hours(max_driving_limit_hour_tracker))
                # Fueling stop: every 1000 miles (converted to meters)
                if fueling_stop_break_tracker >= miles_to_meters(1000):
                    fueling_stop_break = create_stop_step("Fueling", 900, step['way_points'], route_geometry_decoded)
                    print("Fueling", meters_to_miles(fueling_stop_break_tracker))
                    current_day_log.append({
                        "name": "fueling",
                        "hours": seconds_to_hours(900)
                    })
                    number_of_fueling += 1
                    segment_obj["steps"].append(fueling_stop_break)
                    prev_idx = step['way_points'][1]
                    route_geometry_decoded.insert(prev_idx + 1, fueling_stop_break["stop_coord"])
                    current_breaks += 900
                    fueling_stop_break_tracker -= miles_to_meters(1000)
                
                # Pickup stop: only once per segment
                if not pickup_tracker_status:
                    pickup_tracker += step["distance"]
                    if pickup_tracker >= segment_distance:
                        pickup_tracker_status = True
                        pickup_stop_break = create_stop_step("Pickup", 1800, step['way_points'], route_geometry_decoded)
                        print("Pickup")
                        current_day_log.append({
                            "name": "pickup",
                            "hours": seconds_to_hours(1800)
                        })
                        pickup_miles = round(meters_to_miles(pickup_tracker), 2)
                        segment_obj["steps"].append(pickup_stop_break)
                        prev_idx = step['way_points'][1]
                        route_geometry_decoded.insert(prev_idx + 1, pickup_stop_break["stop_coord"])
                        current_breaks += 1800
                        
                # DropOff stop: when accumulated distance reaches route's total distance, create once
                dropoff_tracker += step["distance"]
                
                if dropoff_tracker >= route_summary['distance']:
                    
                    if dropoff_tracker_status:
                        dropoff_stop_break = create_stop_step("DropOff", 1800, step['way_points'], route_geometry_decoded)
                        print("DropOff")
                        dropoff_miles = round(meters_to_miles(dropoff_tracker))
                        segment_obj["steps"].append(dropoff_stop_break)
                        prev_idx = step['way_points'][1]
                        route_geometry_decoded.insert(prev_idx + 1, dropoff_stop_break["stop_coord"])
                        current_breaks += 1800
                        current_day_log.append({
                                "name": "dropoff",
                                "hours": seconds_to_hours(1800)
                        })
                    else:
                        dropoff_tracker_status = True
                        
                
                # 8-hour driving break: after 8 hours of driving time, take a 30-minute break
                eight_hours_driving_rest_tracker += step["duration"]
                if eight_hours_driving_rest_tracker >= hours_to_seconds(8):
                    eight_hours_driving_stop_break = create_stop_step("Break", 1800, step['way_points'], route_geometry_decoded)
                    print('Break')
                    current_day_log.append({
                        "name": "break",
                        "hours": seconds_to_hours(1800)
                    })
                    number_of_breaks += 1
                    segment_obj["steps"].append(eight_hours_driving_stop_break)
                    prev_idx = step['way_points'][1]
                    route_geometry_decoded.insert(prev_idx + 1, eight_hours_driving_stop_break["stop_coord"])
                    eight_hours_driving_rest_tracker -= hours_to_seconds(8)
                
                # 14-hour on-duty limit check (driving time + breaks)
                if (max_driving_limit_hour_tracker + current_breaks) >= hours_to_seconds(14) or max_driving_limit_hour_tracker >= hours_to_seconds(11):
                    print("14-hour on-duty limit reached:",
                          seconds_to_hours(max_driving_limit_hour_tracker + current_breaks), "hours")
                    day_on_duty = max_driving_limit_hour_tracker + current_breaks
                    cumulative_on_duty += day_on_duty
                    number_of_off_duty += 1
                    # Insert a mandatory 10-hour off-duty break
                    off_duty_break = create_stop_step("Off-Duty Break", hours_to_seconds(10), step['way_points'], route_geometry_decoded)
                    current_day_log.append({
                        "name": "off-duty",
                        "hours": 10
                    })
                    log_sheet_result.append(current_day_log.copy())
                    current_day_log = []
                    segment_obj["steps"].append(off_duty_break)
                    prev_idx = step['way_points'][1]
                    route_geometry_decoded.insert(prev_idx + 1, off_duty_break["stop_coord"])
                    # Reset on-duty trackers after off-duty break
                    max_driving_limit_hour_tracker = 0
                    current_breaks = 0
                    eight_hours_driving_rest_tracker = 0
                    
                if cumulative_on_duty >= hours_to_seconds(70):
                    print("70-hour/8-day limit reached:",
                            seconds_to_hours(cumulative_on_duty), "hours")
                    # Insert a 34-hour restart break to reset the 8-day cycle
                    restart_break = create_stop_step("34-Hour Restart", hours_to_seconds(34), step['way_points'], route_geometry_decoded)
                    print('34-Hour Restart')
                    current_day_log.append({
                         "name": "34-Hour Restart",
                         "hours": 34
                    })
                    segment_obj["steps"].append(restart_break)
                    prev_idx = step['way_points'][1]
                    route_geometry_decoded.insert(prev_idx + 1, restart_break["stop_coord"])
                    # Reset cumulative on-duty time after the restart
                    cumulative_on_duty = 0

                
            route_obj["segments"].append(segment_obj)
            
        result['routes'].append(route_obj)  
        
    if current_day_log:
        log_sheet_result.append(current_day_log)
    print('log_sheet_result ', log_sheet_result)  
    return {
        'log_sheet_result': log_sheet_result,
        'result': result,
        'number_of_breaks': number_of_breaks,
        'number_of_fueling': number_of_fueling,
        'number_of_off_duty': number_of_off_duty,
        'pickup_miles': pickup_miles,
        'dropoff_miles': dropoff_miles,
    }


# def create_rests_and_stops(route_data):
#     import polyline

#     result = {}
#     number_of_breaks = 0
#     number_of_fueling = 0
#     number_of_off_duty = 0
#     pickup_miles = 0
#     dropoff_miles = 0
    

#     def miles_to_meters(miles):
#         return miles * 1609.34

#     def meters_to_miles(meters):
#         return meters * 0.000621371

#     def seconds_to_hours(seconds):
#         return seconds / 3600

#     def hours_to_seconds(hours):
#         return hours * 3600

#     def create_stop_step(stop_type, duration_seconds, prev_way_points, route_geometry=None):
#         start_idx = prev_way_points[1]
        
#         coord = route_geometry[start_idx]
#         # Apply a small offset (adjust as needed)
#         offset_lat = 0.0001
#         offset_lon = 0.0001
#         stop_coord = [coord[0] + offset_lat, coord[1] + offset_lon]
#         return {
#             "distance": 0,
#             "duration": duration_seconds,
#             "type": 12,
#             "instruction": f"{stop_type} stop",
#             "name": "-",
#             "way_points": [start_idx, start_idx],
#             "stop_coord": stop_coord
#         }


#     geojson = route_data
#     result['bbox'] = geojson['bbox']
#     result['metadata'] = geojson['metadata']
    
#     routes = geojson.get("routes", [])
#     result['routes'] = []
    
#     for route in routes:
#         # Reset trackers for each new route
#         fueling_stop_break_tracker = 0
#         pickup_tracker = 0
#         pickup_tracker_status = False
#         dropoff_tracker = 0
#         dropoff_tracker_status = False
#         eight_hours_driving_rest_tracker = 0
#         current_breaks = 0
#         max_driving_limit_hour_tracker = 0
#         cumulative_on_duty = 0
        
#         route_summary = route['summary']
#         route_bbox = route['bbox']
#         route_geometry_decoded = polyline.decode(route['geometry'])
#         way_points = route['way_points']
        
#         route_obj = {
#             "summary": route_summary,
#             "bbox": route_bbox,
#             "segments": [],
#             "geometry": route_geometry_decoded,
#             "way_points": way_points,
#         }
        
#         segments = route['segments']
#         for segment in segments:
#             segment_distance = segment['distance']
#             segment_duration = segment['duration']
#             segment_steps = segment['steps']
                        
#             segment_obj = {
#                 "distance": segment_distance,
#                 "duration": segment_duration,
#                 "steps": [],
#             }
            
#             for step in segment_steps:
#                 # Append current step
#                 segment_obj["steps"].append(step)
                
#                 # Accumulate for fueling stops and driving time
#                 fueling_stop_break_tracker += step["distance"]
#                 max_driving_limit_hour_tracker += step["duration"]
                
#                 # Fueling stop: every 1000 miles (converted to meters)
#                 if fueling_stop_break_tracker >= miles_to_meters(1000):
#                     fueling_stop_break = create_stop_step("Fueling", 1800, step['way_points'], route_geometry_decoded)
#                     print("Fueling")
#                     number_of_fueling += 1
#                     segment_obj["steps"].append(fueling_stop_break)
#                     prev_idx = step['way_points'][1]
#                     route_geometry_decoded.insert(prev_idx + 1, fueling_stop_break["stop_coord"])
#                     current_breaks += 1800
#                     fueling_stop_break_tracker -= miles_to_meters(1000)
                
#                 # Pickup stop: only once per segment
#                 if not pickup_tracker_status:
#                     pickup_tracker += step["distance"]
#                     if pickup_tracker >= segment_distance:
#                         pickup_tracker_status = True
#                         pickup_stop_break = create_stop_step("Pickup", 3600, step['way_points'], route_geometry_decoded)
#                         print("Pickup")
#                         pickup_miles = round(meters_to_miles(pickup_tracker), 2)
#                         segment_obj["steps"].append(pickup_stop_break)
#                         prev_idx = step['way_points'][1]
#                         route_geometry_decoded.insert(prev_idx + 1, pickup_stop_break["stop_coord"])
#                         current_breaks += 3600
                        
#                 # DropOff stop: when accumulated distance reaches route's total distance, create once
#                 dropoff_tracker += step["distance"]
#                 if dropoff_tracker >= route_summary['distance'] and not dropoff_tracker_status:
#                     dropoff_stop_break = create_stop_step("DropOff", 3600, step['way_points'], route_geometry_decoded)
#                     print("DropOff")
#                     dropoff_miles = round(miles_to_meters(dropoff_tracker))
#                     segment_obj["steps"].append(dropoff_stop_break)
#                     prev_idx = step['way_points'][1]
#                     route_geometry_decoded.insert(prev_idx + 1, dropoff_stop_break["stop_coord"])
#                     current_breaks += 3600
#                     dropoff_tracker_status = True
                
#                 # 8-hour driving break: after 8 hours of driving time, take a 30-minute break
#                 eight_hours_driving_rest_tracker += step["duration"]
#                 if eight_hours_driving_rest_tracker >= hours_to_seconds(8):
#                     eight_hours_driving_stop_break = create_stop_step("Break", 1800, step['way_points'], route_geometry_decoded)
#                     print('Break')
#                     number_of_breaks += 1
#                     segment_obj["steps"].append(eight_hours_driving_stop_break)
#                     prev_idx = step['way_points'][1]
#                     route_geometry_decoded.insert(prev_idx + 1, eight_hours_driving_stop_break["stop_coord"])
#                     # current_breaks += 1800
#                     eight_hours_driving_rest_tracker -= hours_to_seconds(8)
                
#                 # 14-hour on-duty limit check (driving time + breaks)
#                 if (max_driving_limit_hour_tracker + current_breaks) >= hours_to_seconds(14):
#                     # print("14-hour on-duty limit reached:",
#                     #       seconds_to_hours(max_driving_limit_hour_tracker + current_breaks), "hours")
#                     day_on_duty = max_driving_limit_hour_tracker + current_breaks
#                     cumulative_on_duty += day_on_duty
#                     number_of_off_duty += 1
#                     # Insert a mandatory 10-hour off-duty break
#                     off_duty_break = create_stop_step("Off-Duty Break", hours_to_seconds(10), step['way_points'], route_geometry_decoded)
#                     print('Off-Duty Break')
#                     segment_obj["steps"].append(off_duty_break)
#                     prev_idx = step['way_points'][1]
#                     route_geometry_decoded.insert(prev_idx + 1, off_duty_break["stop_coord"])
#                     # Reset on-duty trackers after off-duty break
#                     max_driving_limit_hour_tracker = 0
#                     current_breaks = 0
#                     eight_hours_driving_rest_tracker = 0
                    
#                 if cumulative_on_duty >= hours_to_seconds(70):
#                         # print("70-hour/8-day limit reached:",
#                             #   seconds_to_hours(cumulative_on_duty), "hours")
#                         # Insert a 34-hour restart break to reset the 8-day cycle
#                         restart_break = create_stop_step("34-Hour Restart", hours_to_seconds(34), step['way_points'], route_geometry_decoded)
#                         print('34-Hour Restart')
#                         segment_obj["steps"].append(restart_break)
#                         prev_idx = step['way_points'][1]
#                         route_geometry_decoded.insert(prev_idx + 1, restart_break["stop_coord"])
#                         # Reset cumulative on-duty time after the restart
#                         cumulative_on_duty = 0

                
#             route_obj["segments"].append(segment_obj)
            
#         result['routes'].append(route_obj)  
        
#     return {
#         'result': result,
#         'number_of_breaks': number_of_breaks,
#         'number_of_fueling': number_of_fueling,
#         'number_of_off_duty': number_of_off_duty,
#         'pickup_miles': pickup_miles,
#         'dropoff_miles': dropoff_miles,
#     }
