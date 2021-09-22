import itertools
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import datetime

from src.libs.resourses import Resources
from src.libs.utils import Center, AutoFont, SaveToBytes
from src.libs.text import HumanizePoints

class Player:
    def __init__(self, name : str, points : list, dates : list):
        self.name = name
        self.points = list(itertools.accumulate(map(int,points)))
        self.dates = [datetime.date(int(i[:4]),int(i[5:]),1) for i in dates]
        self.draw_total = True

# TODO: Make graph look neater
class Graph:
    @staticmethod
    def __NormalizeFields(players : list):
        # Comapare dates 
        lowest_date = players[0].dates[0]
        highest_date = players[0].dates[-1]

        # Find lowest/highest date
        for player in players:
            if player.dates[0] < lowest_date:
                lowest_date = player.dates[0]
            if player.dates[-1] > highest_date:
                highest_date = player.dates[-1]
        
        # Insert lowest highest dates and points
        for player in players:
            if player.dates[0] > lowest_date:
                if (lowest_date - player.dates[0]).days > 31:
                    player.dates.insert(0, lowest_date) 
                    player.points.insert(0,player.points[0])
                player.dates.insert(0, lowest_date) 
                player.points.insert(0,player.points[0])
            if player.dates[-1] < highest_date:
                player.dates.append(highest_date)
                player.points.append(player.points[-1])

    @staticmethod
    def Create(players : list) -> BytesIO:
        Graph.__NormalizeFields(players)
        color_light = (100, 100, 100)
        color_dark = (50, 50, 50)
        colors = (
            'orange',
            'red',
            'forestgreen',
            'dodgerblue',
            'orangered',
            'orchid',
            'burlywood',
            'darkcyan',
            'royalblue',
            'olive',
        )

        font_small = Resources.GetFonts()["small"]

        base = Resources.GetResources()["points_bg"].copy()
        draw = ImageDraw.Draw(base)

        
        
        width, height = base.size
        margin = 50

        plot_width = width - margin * 2
        plot_height = height - margin * 2

        end_date = max([player.dates[-1] for player in players])
        is_leap = end_date.month == 2 and end_date.month == 29
        start_date = min([player.dates[0] for player in players])
        start_date = min(start_date, end_date.replace(year=end_date.year - 1, day=end_date.day - is_leap))

        total_points = max(player.points[-1] for player in players)
        total_points = max(total_points, 1000)

        days_mult = plot_width / (end_date - start_date).days
        points_mult = plot_height / total_points

        # draw area bg
        bg = Image.new('RGBA', (plot_width, plot_height), color=(0, 0, 0, 100))
        base.alpha_composite(bg, dest=(margin, margin))

        # draw years
        prev_x = margin
        for year in range(start_date.year, end_date.year + 2):
            date = datetime.datetime(year=year, month=1, day=1).date()
            if date < start_date:
                continue

            if date > end_date:
                x = width - margin
            else:
                x = margin + (date - start_date).days * days_mult
                xy = ((x, margin), (x, height - margin))
                draw.line(xy, fill=color_dark, width=1)

            text = str(year - 1)
            w, h = font_small.getsize(text)
            area_width = x - prev_x
            if w <= area_width:
                xy = (prev_x + Center(w, area_width), height - margin + h)
                draw.text(xy, text, fill=color_light, font=font_small)

            prev_x = x
        
        # draw points
        thresholds = {
            15000: 5000,
            10000: 2500,
            5000:  2000,
            3000:  1000,
            1000:  500,
            0:     250,
        }

        steps = next(s for t, s in thresholds.items() if total_points > t)
        w, _ = font_small.getsize('00.0K')  # max points label width
        points_margin = Center(w, margin)
        for points in range(0, total_points + 1, int(steps / 5)):
            y = height - margin - points * points_mult
            xy = ((margin, y), (width - margin - 1, y))

            if points % steps == 0:
                draw.line(xy, fill=color_light, width=2)

                text = HumanizePoints(points)
                w, h = font_small.getsize(text)
                xy = (margin - points_margin - w, y + Center(h))
                draw.text(xy, text, fill=color_light, font=font_small)
            else:
                draw.line(xy, fill=color_dark, width=1)

        # draw players
        extra = 2
        size = (plot_width * 2, (plot_height + extra * 2) * 2)
        plot = Image.new('RGBA', size, color=(0, 0, 0, 0))
        plot_draw = ImageDraw.Draw(plot)

        labels = []
        for *dates, color in zip([player.dates for player in players],[player.points for player in players],colors):
            x = -extra
            y = (plot_height + extra) * 2
            xy = [(x, y)]

            prev_date = start_date
            for date, points in zip(dates[0],dates[1]):
                delta = (date - prev_date).days * days_mult * 2
                x += delta
                if delta / (plot_width * 2) > 0.1:
                    xy.append((x, y))

                y = (plot_height)*2 - (points * points_mult * 2)
                xy.append((x, y))

                prev_date = date

            if prev_date != end_date:
                xy.append((plot_width * 2, y))

            plot_draw.line(xy, fill=color, width=6)

            labels.append((margin - extra + y / 2, color))

        size = (plot_width, plot_height + extra * 2)
        plot = plot.resize(size, resample=Image.LANCZOS, reducing_gap=1.0)  # antialiasing
        base.alpha_composite(plot, dest=(margin, margin - extra))

        # remove overlapping labels TODO: optimize
        _, h = font_small.getsize('0')
        offset = Center(h)
        for _ in range(len(labels)):
            labels.sort()
            for i, (y1, _) in enumerate(labels):
                if i == len(labels) - 1:
                    break

                y2 = labels[i + 1][0]
                if y1 - offset >= y2 + offset and y2 - offset >= y1 + offset:
                    labels[i] = ((y1 + y2) / 2, 'white')
                    del labels[i + 1]
        
        # draw player points
        for y, color in labels:
            points = int((height - margin - y) / points_mult)
            text = HumanizePoints(points)
            xy = (width - margin + points_margin, y + offset)
            draw.text(xy, text, fill=color, font=font_small)

        # draw header
        def check(w: int, size: int) -> float:
            return w + (size / 3) * (4 * max(len(player.name) for player in players) - 2)

        font = AutoFont(Resources.GetFonts()["medium"], ''.join(player.name for player in players), plot_width, check=check)
        space = font.size / 3

        x = margin
        for player, color in zip([player.name for player in players], colors):
            y = Center(space, margin)
            xy = ((x, y), (x + space, y + space))
            draw.rectangle(xy, fill=color)
            x += space * 2

            w, _ = font.getsize(player)
            _, h = font.getsize('yA')  # max name height, needs to be hardcoded to align names
            xy = (x, Center(h, margin))
            draw.text(xy, player, fill='white', font=font)
            x += w + space * 2
        
        return SaveToBytes(base.convert('RGB'))

    # Only for debug purposes
    @staticmethod
    def Create_Debug(players : list) -> BytesIO:
        Graph.__NormalizeFields(players)

        img_bytes = BytesIO()

        # Setup axis, format labels etc...
        fig = plt.figure(figsize=(8,5)) #figsize is in inches
        ax = fig.add_subplot(xlim=(players[0].dates[0], players[0].dates[-1])) 
        rend = fig.canvas.get_renderer()
        offset = (10,410)

        ax.set_xlim(players[0].dates[0], players[0].dates[-1])
        ax.xaxis.set_major_locator(mdates.YearLocator()) 
        ax.xaxis.set_minor_locator(mdates.MonthLocator()) 
        ax.set_axisbelow(True)
        ax.grid(linestyle='-', linewidth='0.8',color="black",alpha=0.4,axis="x")

        # Add lines
        for i, player in enumerate(players):
            ax.plot_date(player.dates, player.points, Graph.__colors[i]) 
            pText = ax.annotate(f"{player.name}",offset,xycoords="axes pixels",color=plt.gca().lines[-1].get_color())
            size = pText.get_window_extent(renderer=rend)
            width = size.width
            offset = (offset[0] + width + 10, offset[1])


        # Check if there is enough space to draw current points
        _, y_lim = ax.get_ylim()

        for i, player in enumerate(players):
            for player2 in players:
                if (player.draw_total and player2.draw_total) and (player.name != player2.name):
                    ratio = abs(player.points[-1] - player2.points[-1]) / y_lim
                    if ratio < Graph.__min_ratio:
                        player.draw_total = False

        for i, player in enumerate(players):
            if player.draw_total == True:
                ax.annotate(f"{player.points[-1]}",(player.dates[-1],player.points[-1]),xytext=(5,0),textcoords="offset points",color=Graph.__colors[i])
                
        # Save to bytes and return
        plt.savefig(img_bytes,transparent=True,format="PNG")
        
        img_bytes.seek(0)

        return img_bytes