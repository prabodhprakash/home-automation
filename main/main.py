#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import requests
import pytz
from datetime import datetime

picdir = os.path.join("/home/prabodhprakash/automation/home-automation", "pic")
libdir = os.path.join("/home/prabodhprakash/automation/home-automation", 'lib')
print(libdir)
if os.path.exists(libdir):
    print("Found the path")
    sys.path.append(libdir)
else:
    print("Not found the path")

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image, ImageDraw, ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

width = epd7in5_V2.EPD_WIDTH
height = epd7in5_V2.EPD_HEIGHT

routine_json = {
  "routine": [
      {
        "date": "2023-12-12",
        "schedule": [
            {
                "start_time": "00:00",
                "end_time": "07:00",
                "routine_text": "Sleep"
            },
            {
                "start_time": "07:00",
                "end_time": "07:45",
                "routine_text": "Ready for School"
            },
            {
                "start_time": "07:45",
                "end_time": "13:15",
                "routine_text": "School"
            },
            {
                "start_time": "13:15",
                "end_time": "14:00",
                "routine_text": "Lunch"
            },
            {
                "start_time": "14:00",
                "end_time": "15:00",
                "routine_text": "Activity"
            },
            {
                "start_time": "15:00",
                "end_time": "15:45",
                "routine_text": "Chess"
            },
            {
                "start_time": "15:45",
                "end_time": "16:15",
                "routine_text": "Idle Time"
            },
            {
                "start_time": "16:15",
                "end_time": "18:00",
                "routine_text": "TT"
            },
            {
                "start_time": "18:00",
                "end_time": "19:30",
                "routine_text": "Leisure"
            },
            {
                "start_time": "19:30",
                "end_time": "20:00",
                "routine_text": "Prepare bag for school"
            },
            {
                "start_time": "20:00",
                "end_time": "20:30",
                "routine_text": "Dinner"
            },
            {
                "start_time": "20:30",
                "end_time": "00:00",
                "routine_text": "Sleep"
            }
        ]
      }
  ]
}


def convert_to_12_hour(time):
    return datetime.strptime(time, "%H:%M").strftime("%I:%M %p")


# Function to get current routine based on current time and date
def get_current_routine(routine_data):
    ist = pytz.timezone('Asia/Kolkata')
    current_date = datetime.now(ist).strftime("%Y-%m-%d")
    for item in routine_data:
        print(item['date'], current_date)
        if item['date'] == current_date:
            schedule = item['schedule']
            now = datetime.now(ist).time()
            for slot in schedule:
                start_time = datetime.strptime(slot['start_time'], "%H:%M").time()
                end_time = datetime.strptime(slot['end_time'], "%H:%M").time()
                if start_time <= now <= end_time:
                    return slot, schedule.index(slot), schedule[schedule.index(slot) + 1] if schedule.index(slot) < len(schedule) - 1 else None
    return None, None, None



def get_motivational_quote():
    # Replace this with your method of fetching a daily motivational quote
    # Example using an API (change URL and structure based on your chosen API)
    response = requests.get("https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en")
    if response.status_code == 200:
        data = response.json()
        quote = data.get('quoteText', 'Motivational quote not available')
        return quote
    else:
        return 'Failed to fetch quote'


def display_content(quote, routine, chess_puzzle):
    # Create an image with a white background
    logging.info("epd7in5_V2 Demo")
    epd = epd7in5_V2.EPD()

    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font48 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 48)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    image = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    # Set initial coordinates and line height for quote
    quote_x, quote_y = 10, 130
    line_height = 24  # Change this value according to your font size

    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    date = now.strftime("%Y-%m-%d")
    day = now.strftime("%A")

    # Draw horizontal line above the quote
    draw.line([(10, quote_y - 10), (width - 10, quote_y - 10)], fill=0, width=2)

    # Display date and day (left aligned)
    draw.text((10, 10), date, font=font48, fill=0)
    draw.text((10, 70), day, font=font24, fill=0)

    # Write "Delilah's Kingdom" (right aligned)
    kingdom_text = "Delilah's Kingdom"
    kingdom_text_width = draw.textsize(kingdom_text, font=font24)[0]
    draw.text((width - kingdom_text_width - 10, 10), kingdom_text, font=font24, fill=0)

    # Split the quote into multiple lines if it exceeds a certain width
    max_quote_width = width - 20  # Adjust this according to your display width
    quote_lines = []
    current_line = ''
    words = quote.split()
    for word in words:
        if draw.textsize(current_line + ' ' + word, font=font24)[0] <= max_quote_width:
            current_line += ' ' + word
        else:
            quote_lines.append(current_line.strip())
            current_line = word
    if current_line:
        quote_lines.append(current_line.strip())

    # Display the multiline quote
    for line in quote_lines:
        draw.text((quote_x, quote_y), line, font=font24, fill=0)
        quote_y += line_height

    # Draw a horizontal line after the quote
    line_y = quote_y + 10  # Adjust the position of the line
    draw.line([(10, line_y), (width - 10, line_y)], fill=0, width=2)  # Adjust width as needed

    # Draw a vertical line below the horizontal line
    vertical_line_x = width // 2
    vertical_line_end_y = line_y + 200  # Ending point of vertical line
    draw.line([(vertical_line_x, line_y + 5), (vertical_line_x, vertical_line_end_y)], fill=0, width=2)

    # Get current routine and next routine
    current_routine, current_index, next_routine = get_current_routine(routine_json["routine"])
    # Write text on the left side of the vertical line (Left aligned)
    left_text = "NOW"
    draw.text((10, line_y + 15), left_text, font=font48, fill=0)

    draw.text(
        (150, line_y + 35),
        f"{convert_to_12_hour(current_routine['start_time'])} - {convert_to_12_hour(current_routine['end_time'])}",
        font=font18,
        fill=0
    )

    # Write text below "Left text here"
    below_left_text = current_routine["routine_text"]
    draw.text((10, line_y + 100), below_left_text, font=font24, fill=0)

    # Write text on the right side of the vertical line (Right aligned)
    right_text = f"Next"
    right_text_width = draw.textsize(right_text, font=font48)[0]
    draw.text((vertical_line_x + 10, line_y + 15), right_text, font=font48, fill=0)

    draw.text(
        (vertical_line_x + 130, line_y + 35),
        f"{convert_to_12_hour(next_routine['start_time'])} - {convert_to_12_hour(next_routine['end_time'])}",
        font=font18,
        fill=0
    )

    # Write text below "Right text here" (Right aligned)
    below_right_text = next_routine["routine_text"]
    draw.text((vertical_line_x + 10, line_y + 100), below_right_text, font=font24, fill=0)

    draw.line([(10, vertical_line_end_y), (width - 10, vertical_line_end_y)], fill=0, width=2)  # Adjust width as needed

    epd.display(epd.getbuffer(image))
    epd.sleep()


try:
    # Get a motivational quote
    motivational_quote = get_motivational_quote()

    # Define your routine and chess puzzle for the day
    daily_routine = "Your daily routine goes here."
    chess_puzzle = "Your chess puzzle goes here."

    # Display content on the e-paper display
    display_content(motivational_quote, daily_routine, chess_puzzle)

except KeyboardInterrupt:
    print("Keyboard Interrupt")
    epd7in5_V2.epdconfig.module_exit()
    exit()
