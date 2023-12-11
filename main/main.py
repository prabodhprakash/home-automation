#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import requests

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
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    image = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    draw.text((10, 10), quote, font=font18, fill=0)

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
