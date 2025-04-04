
import polyline
from pprint import pprint
from datetime import datetime as Datetime, timedelta
import datetime
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from io import BytesIO
import os
from django.conf import settings
from django.http import HttpResponse
from django.contrib.staticfiles import finders

def create_rests_and_stops(route_data, current_cycle_used=0):

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
        # Use the ending way_point of the previous step, then increment for the next
        start_idx = prev_way_points[1]
        
        coord = route_geometry[start_idx]
        # Apply a small offset (adjust as needed)
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
    
    current_cycle_used_secs = hours_to_seconds(current_cycle_used)
    

    log_sheet_result = []
    current_date = Datetime.now()
    formatted_date = current_date.strftime("%m/%d/%y")
    # print('formatted_date', formatted_date)
    current_day_log = [
        {
            'driving': [],
            'miles': 0,
            'date': Datetime.now(),
        }
    ]
    current_day_log_obj = {
        "name": "driving",
        "hours": 0
    }
    miles_trucker = 0
    
    for route in routes:
        # Reset trackers for each new route
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
                
                current_day_log_obj["name"] = "driving"
                current_day_log_obj["hours"] += seconds_to_hours(step["duration"])
                miles_trucker += meters_to_miles(step["distance"])
                # current_day_log[0]["date"] += seconds_to_hours(step["duration"])
          
                
                # Fueling stop: every 1000 miles (converted to meters)
                if fueling_stop_break_tracker >= miles_to_meters(1000):
                    fueling_stop_break = create_stop_step("Fueling", 900, step['way_points'], route_geometry_decoded)
                    # print("Fueling", meters_to_miles(fueling_stop_break_tracker))
                    current_day_log[0]["driving"].append({
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
                        # print("Pickup")
                        current_day_log[0]["driving"].append({
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
                        # print("DropOff")
                        dropoff_miles = round(meters_to_miles(dropoff_tracker))
                        segment_obj["steps"].append(dropoff_stop_break)
                        prev_idx = step['way_points'][1]
                        route_geometry_decoded.insert(prev_idx + 1, dropoff_stop_break["stop_coord"])
                        current_breaks += 1800
                        current_day_log[0]["driving"].append({
                                "name": "dropoff",
                                "hours": seconds_to_hours(1800)
                        })
                    else:
                        dropoff_tracker_status = True
                        
                
                # 8-hour driving break: after 8 hours of driving time, take a 30-minute break
                eight_hours_driving_rest_tracker += step["duration"]
                if eight_hours_driving_rest_tracker >= hours_to_seconds(8):
                    eight_hours_driving_stop_break = create_stop_step("Break", 1800, step['way_points'], route_geometry_decoded)
                    # print('Break')
                    current_day_log[0]["driving"].append({
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
                    # print("14-hour on-duty limit reached:",
                        #   seconds_to_hours(max_driving_limit_hour_tracker + current_breaks), "hours")
                    day_on_duty = max_driving_limit_hour_tracker + current_breaks
                    cumulative_on_duty += day_on_duty
                    number_of_off_duty += 1
                    # Insert a mandatory 10-hour off-duty break
                    off_duty_break = create_stop_step("Off-Duty Break", hours_to_seconds(10), step['way_points'], route_geometry_decoded)
                    current_day_log[0]["driving"].append(current_day_log_obj)
                    current_day_log[0]["miles"] = miles_trucker
                    # print("#" * 99)

                    
                    current_date = current_day_log[0]["date"] + timedelta(days=1)
                    # print("current_date", current_day_log[0]["date"] )
                    # current_date + timedelta(days=1)
                    
                    # print("#" * 99)
                        
                    current_day_log[0]["driving"].append({
                        "name": "off-duty",
                        "hours": 10
                    })
                    current_day_log_obj = {
                        "name": "driving",
                        "hours": 0
                    }
                    miles_trucker = 0
                    log_sheet_result.append(current_day_log.copy())
                    # current_day_log = []
                    current_day_log = [
                        {
                            'driving': [],
                            'miles': 0,
                            "date": current_date,
                        }
                    ]
                    segment_obj["steps"].append(off_duty_break)
                    prev_idx = step['way_points'][1]
                    route_geometry_decoded.insert(prev_idx + 1, off_duty_break["stop_coord"])
                    # Reset on-duty trackers after off-duty break
                    max_driving_limit_hour_tracker = 0
                    current_breaks = 0
                    eight_hours_driving_rest_tracker = 0
                    
                if cumulative_on_duty >= hours_to_seconds(70):
                    # print("70-hour/8-day limit reached:",
                            # seconds_to_hours(cumulative_on_duty), "hours")
                    # Insert a 34-hour restart break to reset the 8-day cycle
                    restart_break = create_stop_step("34-Hour Restart", hours_to_seconds(34), step['way_points'], route_geometry_decoded)
                    # print('34-Hour Restart')
                    
                    
                    current_day_log[0]["driving"].append({
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
    
    if miles_trucker:
        current_day_log[0]["miles"] = miles_trucker
    if current_day_log_obj:
        current_day_log[0]["driving"].append(current_day_log_obj)
        current_day_log_obj = {
                        "name": "driving",
                        "hours": 0
                    }
        # print('current_day_log_obj', current_day_log_obj)
    
    if current_day_log:
        log_sheet_result.append(current_day_log)
        
        
    # print('log_sheet_result', log_sheet_result)
    return {
        'log_sheet_result': log_sheet_result,
        'result': result,
        'number_of_breaks': number_of_breaks,
        'number_of_fueling': number_of_fueling,
        'number_of_off_duty': number_of_off_duty,
        'pickup_miles': pickup_miles,
        'dropoff_miles': dropoff_miles,
    }


def adjust_hours(log_sheet_result):
    MAX_DRIVING = 11.0
    result = []
    dropoff = {}
    counter = 0
    remaining_driving_hours = 0
    while counter < len(log_sheet_result):
        record = log_sheet_result[counter][0]
        driving_results = []
        remaining_break = {}
        for activity in record["driving"]:
            if activity['name'] == "driving":
                total_driving = activity["hours"] + remaining_driving_hours
                if total_driving > MAX_DRIVING:
                    remaining_driving_hours = total_driving - MAX_DRIVING
                    # print('remaining miles', (record["miles"] / total_driving) * remaining_driving_hours)
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
                if activity['name'] != "break" and activity['name'] != "dropoff":
                    driving_results.append(activity)
                    
            if activity['name'] == "dropoff":
                dropoff = activity
            
        result[-1][0]['miles'] = record["miles"]
        result[-1][0]['date'] = record["date"]
        counter += 1
    
    
    if remaining_driving_hours > 0:
        # if remaining_driving_hours > 11:
        x = [
            {
                "driving": [
                    {"name": "driving", "hours": remaining_driving_hours},
                    dropoff
                ],
                "miles": 0,
                "date": result[-1][0]['date'] + datetime.timedelta(days=1),
            }
        ]
        result.append(x)
        
        # print(result)
        
    else:
        result[-1][0].get('driving', []).append(dropoff)
        
        
    return result
        
        


def draw_log(data, output_pdf="log_output.pdf"):
    # # status = False
    x = 64
    start_x_position = 64 + (7 * 16.2)
    # start_x_position = 64
    # total_x_position = 64 + (24 * 16.2)
    
    
    off_duty_y_position = 194
    sleeper_berth_y_position = 212
    driving_y_position = 224
    on_duty_y_position = 242
    off_duty_hour_position = (469, 190)
    sleeper_berth_hour_position = (469, 206)
    driving_hour_position = (469, 224)
    on_duty_hour_position = (469, 241)
    total_hour_position = (469, 266)
    # image_name = "blank-paper-log.png"
    
    image_name = finders.find('imgs/blank-paper-log.png')
    print('image_name', image_name)
    if not image_name:
        print("Static image not found. Check your static files configuration.")
        return None
    
    images = [] 
    image_objects = [] # List to store modified images
    current_step_position = None
    for i in data:
        hours_passed = 0
        current_step_position = None
        previous_y_position = 0
        previous_x_position = 0
        driving_hour_tracker = 0
        off_duty_hour_tracker = 7
        on_duty_hour_tracker = 0
        
        try:
            base_img = Image.open(image_name).convert("RGBA")  # Load the base image
        except FileNotFoundError:
            print(f"Error: '{image_name}' not found.")
            return
        
        # Create a white background to prevent transparency issues
        white_bg = Image.new("RGBA", base_img.size, (255, 255, 255, 255))
        # Make a fresh copy of the image for each entry
        img = Image.alpha_composite(white_bg, base_img).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Load fonts
        try:
            text_font = ImageFont.truetype("arial.ttf", 8)
            number_font = ImageFont.truetype("arial.ttf", 10)
        except IOError:
            print("Warning: 'arial.ttf' not found. Using default font.")
            text_font = ImageFont.load_default()
            number_font = ImageFont.load_default()

        # Extract and format the date
        dt = i[0].get('date')
        month = dt.strftime("%m")
        day = dt.strftime("%d")
        year = dt.strftime("%y")
        
        draw.text((79, 67), f"{round(i[0].get('miles'), 2)}", font=number_font, fill="green")

        # Draw text on the image
        draw.text((180, 4), month, font=number_font, fill="green")
        draw.text((220, 4), day, font=number_font, fill="green")
        draw.text((265, 4), year, font=number_font, fill="green")
        
        
        line = ((x, off_duty_y_position), (start_x_position, off_duty_y_position))
        draw.line(line, fill="green", width=2)
        previous_y_position = off_duty_y_position
        previous_x_position = start_x_position
        
        for d in i[0].get('driving', []):
            if d['name'] == "driving":
                driving_hour_tracker += d['hours']
                if not current_step_position:
                    step = start_x_position + (d['hours'] * 16.2)
                else:
                    step = current_step_position + (d['hours'] * 16.2) 

                line_x = ((previous_x_position, previous_y_position), (previous_x_position, driving_y_position))
                draw.line(line_x, fill="green", width=2)
                hours_passed += d['hours']
                
                line = ((current_step_position or start_x_position, driving_y_position), (step, driving_y_position))
                draw.line(line, fill="green", width=2)
                current_step_position = step
                previous_x_position = current_step_position
                previous_y_position = driving_y_position
                
            elif d['name'] == "break":
                # if current_step_position:
                off_duty_hour_tracker += d['hours']
                if not current_step_position:
                    step = start_x_position + (d['hours'] * 16.2)
                else:
                    step = current_step_position + (d['hours'] * 16.2) 

                line_x = ((previous_x_position, previous_y_position), (previous_x_position, off_duty_y_position))
                draw.line(line_x, fill="green", width=2)
                hours_passed += d['hours']
                line = ((current_step_position or start_x_position, off_duty_y_position), (step, off_duty_y_position))
                draw.line(line, fill="green", width=2)
                current_step_position = step
                previous_x_position = current_step_position
                previous_y_position = off_duty_y_position
                
            elif d['name'] == "off-duty":
                pass
                # if current_step_position:
                #     step = current_step_position + (total_x_position - (d['hours'] * 16.2))

                #     line = ((current_step_position, sleeper_berth_y_position), (step, sleeper_berth_y_position))
                #     draw.line(line, fill="green", width=2)
                    
                #     current_step_position = step
                # x_position_tracker += d['hours']
            elif d['name'] == "pickup":
                on_duty_hour_tracker += d['hours']
                if not current_step_position:
                    step = start_x_position + (d['hours'] * 16.2)
                else:
                    step = current_step_position + (d['hours'] * 16.2) 
                    
                line_x = ((previous_x_position, previous_y_position), (previous_x_position, on_duty_y_position))
                draw.line(line_x, fill="green", width=2)
                hours_passed += d['hours']
                line = ((current_step_position or start_x_position, on_duty_y_position), (step, on_duty_y_position))
                draw.line(line, fill="green", width=2)
                current_step_position = step
                previous_x_position = current_step_position
                previous_y_position = on_duty_y_position
                
            elif d['name'] == "fueling":
                on_duty_hour_tracker += d['hours']
                if not current_step_position:
                    step = start_x_position + (d['hours'] * 16.2)
                else:
                    step = current_step_position + (d['hours'] * 16.2) 

                line_x = ((previous_x_position, previous_y_position), (previous_x_position, on_duty_y_position))
                draw.line(line_x, fill="green", width=2)
                hours_passed += d['hours']
                line = ((current_step_position or start_x_position, on_duty_y_position), (step, on_duty_y_position))
                draw.line(line, fill="green", width=2)
                current_step_position = step
                previous_x_position = current_step_position
                previous_y_position = on_duty_y_position
            elif d['name'] == "dropoff":
                on_duty_hour_tracker += d['hours']
                if not current_step_position:
                    step = start_x_position + (d['hours'] * 16.2)
                else:
                    step = current_step_position + (d['hours'] * 16.2) 
                    
                line_x = ((previous_x_position, previous_y_position), (previous_x_position, on_duty_y_position))
                draw.line(line_x, fill="green", width=2)
                hours_passed += d['hours']
                line = ((current_step_position or start_x_position, on_duty_y_position), (step, on_duty_y_position))
                draw.line(line, fill="green", width=2)
                current_step_position = step
                previous_x_position = current_step_position
                previous_y_position = on_duty_y_position
            
        remaining_hours = 24 - hours_passed
        step = current_step_position + ((remaining_hours - 7) * 16.2) 
        line = ((current_step_position, sleeper_berth_y_position), (step, sleeper_berth_y_position))
        draw.line(line, fill="green", width=2)
        draw.text(sleeper_berth_hour_position, f"{round((remaining_hours - 7), 2)}", font=number_font, fill="red")
        
        line_x = ((previous_x_position, previous_y_position), (previous_x_position, sleeper_berth_y_position))
        draw.line(line_x, fill="green", width=2)
        
        total_day_hours = (remaining_hours - 7) + (driving_hour_tracker + off_duty_hour_tracker + on_duty_hour_tracker)
        draw.text(driving_hour_position, f"{round(driving_hour_tracker, 2)}", font=number_font, fill="red")
        draw.text(off_duty_hour_position, f"{round(off_duty_hour_tracker, 2)}", font=number_font, fill="red")
        draw.text(on_duty_hour_position, f"{round(on_duty_hour_tracker, 2)}", font=number_font, fill="red")
        draw.text(total_hour_position, f"{round(total_day_hours, 2)}", font=number_font, fill="red")
        
        img_io = BytesIO()
        img.save(img_io, format="JPEG")
        img_io.seek(0)
        image_objects.append(img_io)
        images.append(img.copy())

    if image_objects:
        first_img = Image.open(image_objects[0])
        width, height = first_img.size
        
        # pdf_path = output_pdf
        pdf_path = os.path.join(settings.MEDIA_ROOT, output_pdf)
        pdf = canvas.Canvas(pdf_path, pagesize=(width, height))

        for img_io in image_objects:
            img = Image.open(img_io)
            pdf.drawInlineImage(img, 0, 0, width, height)  # Add image to PDF
            pdf.showPage()  # Move to next page

        pdf.save()
        print(f"PDF saved successfully: {pdf_path}")
        return f"{settings.MEDIA_URL}{output_pdf}"
    else:
        print("No images to save.")


