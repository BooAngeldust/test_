from math import floor
from PIL import ImageFont, Image, ImageDraw
from io import BytesIO

import datetime

def AutoFont(font: ImageFont.FreeTypeFont, text: str, max_width: int,*, check) -> ImageFont.FreeTypeFont:
    if isinstance(font, tuple):
        font = ImageFont.truetype(*font)

    while check(font.getsize(text)[0], font.size) > max_width:
        font = ImageFont.truetype(font.path, font.size - 1)

    return font


def GetTextSize(text : str, font : ImageFont) -> tuple:
    fontWidth,_  = font.getsize(text)
    _,fontHeight = font.getsize("yA")
    return (fontWidth,fontHeight)

def NormalizeSeconds(seconds : int) -> str:
    seconds = seconds
    minutes = 0
    hours = 0
    days = 0
        
    if seconds >= 60:
        minutes, seconds = divmod(seconds, 60)
        if minutes >= 60:
            hours, minutes = divmod(minutes,60)
            if hours >= 24:
                days, hours = divmod(hours, 24)

    playTime = ""
        
    if days != 0:
        playTime += f"{days}d "
        playTime += f"{hours}h"
    elif hours != 0:
        playTime += f"{hours}h "
        playTime += f"{minutes}m"
    elif minutes != 0:
        playTime += f"{minutes}m "
        playTime += f"{seconds}s"

    return playTime

def ConvertTime(t : str) -> str:
    time = floor(float(t))
    minutes = time // 60
    time %= 60
    seconds = time

    if seconds < 10:
        seconds = "0" + str(seconds)

    return f"{minutes}:{seconds}"

def ConvertTimestamp(timestamp : str) -> str:
    try:
        _format = '%Y-%m-%d %H:%M:%S'
    
        dateObject = datetime.datetime.strptime(timestamp,_format)
        year  = str(dateObject.year)
        month = str(dateObject.month)
        day   = str(dateObject.day)
        dateObject = datetime.datetime.strptime(month, "%m")
        monthName = dateObject.strftime("%b")
        date = f"{monthName.upper()} {day} {year}"
    except:
        date = "UNKNOWN"
    finally:
        return date


def Center(size: int, area_size: int=0 ) -> int:
    return int((area_size - size) / 2)

def SaveToBytes(img : Image) -> BytesIO():
    img_bytes = BytesIO()

    img.save(img_bytes,format="png")
    img.close()
    img_bytes.seek(0)

    return img_bytes

# DDnet code
def RoundRect(size: tuple, radius: int, *, color: tuple) -> Image.Image:
    width, height = size

    radius = min(width, height, radius * 2)
    width *= 2
    height *= 2

    corner = Image.new('RGBA', (radius, radius))
    draw = ImageDraw.Draw(corner)
    xy = (0, 0, radius * 2, radius * 2)
    draw.pieslice(xy, 180, 270, fill=color)

    rect = Image.new('RGBA', (width, height), color=color)
    rect.paste(corner, (0, 0))                                          # upper left
    rect.paste(corner.rotate(90), (0, height - radius))                 # lower left
    rect.paste(corner.rotate(180), (width - radius, height - radius))   # lower right
    rect.paste(corner.rotate(270), (width - radius, 0))                 # upper right

    return rect.resize(size, resample=Image.LANCZOS, reducing_gap=1.0)


