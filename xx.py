
import datetime
from pprint import pprint
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from io import BytesIO

data = [
    [
        {
            "driving": [
                {"name": "driving", "hours": 8},
                {"hours": 0.5, "name": "break"},
                {"name": "driving", "hours": 3},
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
                {"name": "fueling", "hours": 0.25},
                {"hours": 7.762527777777779, "name": "driving"},
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
                {"name": "driving", "hours": 8},
                {"hours": 0.5, "name": "break"},
                {"name": "driving", "hours": 3},
            ],
            "miles": 299.4290536495,
            "date": datetime.datetime(2025, 4, 4, 5, 2, 45, 772172),
        }
    ],
    [
        {
            "driving": [{"name": "driving", "hours": 6.098944444444445}],
            "miles": 0,
            "date": datetime.datetime(2025, 4, 5, 5, 2, 45, 772172),
        }
    ],
]



def draw_log(data, output_pdf="log_output.pdf"):
    x = 64
    start_x_position = 64 + (7 * 16.2)
    total_x_position = 64 + (24 * 16.2)
    off_duty_y_position = 194
    sleeper_berth_y_position = 212
    driving_y_position = 224
    on_duty_y_position = 242
    image_name = "blank-paper-log.png"
    images = [] 
    image_objects = [] # List to store modified images
    current_step_position = None
    for i in data:
        current_step_position = None
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
            number_font = ImageFont.truetype("arial.ttf", 16)
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
        
        for d in i[0].get('driving', []):
            if d['name'] == "driving":
                if not current_step_position:
                    step = 64 + (d['hours'] * 16.2)
                else:
                    step = current_step_position + (d['hours'] * 16.2) 

                line = ((current_step_position or 64, driving_y_position), (step, driving_y_position))
                draw.line(line, fill="green", width=2)

                current_step_position = step 

            elif d['name'] == "break":
                if current_step_position:
                    step = current_step_position + (d['hours'] * 16.2)

                    line = ((current_step_position, off_duty_y_position), (step, off_duty_y_position))
                    draw.line(line, fill="green", width=2)

                    current_step_position = step
                
            elif d['name'] == "off-duty":
                if current_step_position:
                    step = current_step_position + (d['hours'] * 16.2)

                    line = ((current_step_position, sleeper_berth_y_position), (step, sleeper_berth_y_position))
                    draw.line(line, fill="green", width=2)

                    current_step_position = step
                print('off-duty', current_step_position)
            elif d['name'] == "pickup":
                pass
            elif d['name'] == "fueling":
                pass
            elif d['name'] == "dropoff":
                pass
        
        print("#"*99)
        img_io = BytesIO()
        img.save(img_io, format="JPEG")
        img_io.seek(0)
        image_objects.append(img_io)
        images.append(img.copy())

    if image_objects:
        first_img = Image.open(image_objects[0])
        width, height = first_img.size
        pdf = canvas.Canvas(output_pdf, pagesize=(width, height))

        for img_io in image_objects:
            img = Image.open(img_io)
            pdf.drawInlineImage(img, 0, 0, width, height)  # Add image to PDF
            pdf.showPage()  # Move to next page

        pdf.save()
        print(f"PDF saved successfully: {output_pdf}")
    else:
        print("No images to save.")



draw_log(data)

