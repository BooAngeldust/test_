from PIL import Image, ImageFont, ImageDraw, ImageOps
from discord.ext import commands
import discord
from io import BytesIO

from src.libs.https_request import Request
from src.libs.utils import ConvertTime, NormalizeSeconds, ConvertTimestamp, SaveToBytes, GetTextSize
from src.libs.text import ToStars, CleanContent, HumanizeDifficulty
from src.libs.resourses import Resources


class Map(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot

        self.fonts = Resources.GetFonts()
        self.colours = Resources.GetColours()
        self.resources = Resources.GetResources()

    def GenerateMapImage(self, map_name : str, player : str):
        # Get map info, and check if the map exists
        try:
            map_info = Request.MapInfo(map_name, player)["mapinfo"]
        except:
            raise commands.CommandError("Unable to fetch data")
        finally:
            if map_info["Server"] == None:
                raise commands.CommandError(f"No map named '{map_name}' ")

        if "PlayerName" in map_info.keys():
            if map_info["PlayerTime"] == None:
                raise commands.CommandError(f"Player `{player}` did not finish the map.")
        
        # Start with map bg, if not found use plain picture
        try:
            img = Image.open(f"data/images/maps/{map_name}.png")
            img.convert("RGBA")
        except:
            img = Image.new("RGBA",(800,500),color=(50,50,50,255))

        # Design the map
        overlay_img = Image.new("RGBA",img.size,(0,0,0,0))

        # Create dark round rect
        overlay_img = Image.alpha_composite(overlay_img, self.resources["dark_rect_map"])
        
        # ImageDraw object
        draw = ImageDraw.Draw(overlay_img)
        
        # Map name round rect

        # Get rid of the author if map name is too long
        map_name = f"   {map_name} by {map_info['Mapper']}   "
        name_size = GetTextSize(map_name,self.fonts["large"])[0]
        if name_size > 650:
            map_name = map_info["Map"]
            name_size = GetTextSize(map_name,self.fonts["large"])[0]

        #Image.resize(size, resample=0)
        # Left
        temp_left_img = self.resources["bar_side_l"].resize((self.resources["bar_side_l"].size[0], self.resources["bar_side_l"].size[1] + 5))
        overlay_img.paste(temp_left_img,(50,35),temp_left_img)
        # Middle
        temp_mid_img = self.resources["bar_middle"].resize((name_size,self.resources["bar_middle"].size[1] + 5))
        overlay_img.paste(temp_mid_img,(61,35),temp_mid_img)
        # Right
        temp_right_img = self.resources["bar_side_r"].resize((self.resources["bar_side_r"].size[0], self.resources["bar_side_r"].size[1] + 5))
        overlay_img.paste(temp_right_img,(61+name_size,35),temp_right_img)

        # Map name (Title)
        draw.text((61,36), f"{map_name}", font=self.fonts["large"],fill=self.colours["white"])

        # Difficulty
        diff_size = GetTextSize(HumanizeDifficulty(map_info['Server']).upper(),self.fonts["large"])[0]
        draw.text((200 - (diff_size // 2) + 20,100),HumanizeDifficulty(map_info['Server']).upper(),font=self.fonts["large"],fill=self.colours["white"])

        # Stars
        stars_size = GetTextSize(ToStars(5),font=self.fonts["large"])[0]
        draw.text((200 - (stars_size // 2) + 20,160), ToStars(int(map_info["Stars"])),font=self.fonts["large"],fill=self.colours["white"])

        # Points
        points_size = GetTextSize(f"{map_info['Points']} POINTS",font=self.fonts["medium"])[0]
        points_num_size = GetTextSize(f"{map_info['Points']}",font=self.fonts["medium"])[0]
        draw.text((200 - (points_size // 2) + 20,220), f"{map_info['Points']}", font=self.fonts["medium"],fill=self.colours["blue"])
        draw.text((200 - (points_size // 2) + points_num_size + 20,220)," POINTS", font=self.fonts["medium"],fill=self.colours["white"])

        # Finishes
        finishes_size = GetTextSize(f"{map_info['Finishes']} FINISHES",font=self.fonts["medium"])[0]
        finishes_num_size = GetTextSize(f"{map_info['Finishes']}",font=self.fonts["medium"])[0]
        draw.text((200 - (finishes_size // 2) + 20,270), f"{map_info['Finishes']}", font=self.fonts["medium"],fill=self.colours["blue"])
        draw.text((200 - (finishes_size // 2) + finishes_num_size + 20,270)," FINISHES", font=self.fonts["medium"],fill=self.colours["white"])

        # Release
        release_size = GetTextSize(f"RELEASED {ConvertTimestamp(map_info['Timestamp'])}",font=self.fonts["medium"])[0]
        release_text_size = GetTextSize("RELEASED",font=self.fonts["medium"])[0]
        draw.text((200 - (release_size // 2) + 20,320),"RELEASED", font=self.fonts["medium"],fill=self.colours["white"])
        draw.text((200 - (release_size // 2) + release_text_size + 20,320), f" {ConvertTimestamp(map_info['Timestamp'])}", font=self.fonts["medium"],fill=self.colours["blue"])

        # Top 10
        player_posy = 100
        count = 1
        for p, time in zip(map_info["Players"],map_info["Times"]):
            time = ConvertTime(time)
            time_size = GetTextSize(time,font=self.fonts["small"])[0]
            draw.text((420, player_posy), f"#{count}", font=self.fonts["small"], fill=self.colours["white"])
            draw.text((460, player_posy), time, font=self.fonts["small"], fill=self.colours["blue"])
            draw.text((460 + time_size + 10, player_posy), p, font=self.fonts["small"], fill=self.colours["white"])
            
            player_posy += 25
            count += 1
        
        # Player Requested
        
        
        if player != None:
            player_posy += 25
            time = ConvertTime(map_info["PlayerTime"])
            time_size = GetTextSize(time,font=self.fonts["small"])[0]
            rank_size = GetTextSize(f"#{map_info['PlayerRank']}  ",font=self.fonts["small"])[0]
            draw.text((420, player_posy), f"#{map_info['PlayerRank']}", font=self.fonts["small"], fill=self.colours["white"])
            draw.text((420 + rank_size, player_posy), time, font=self.fonts["small"], fill=self.colours["blue"])
            draw.text((420 + rank_size + time_size + 10, player_posy), map_info["PlayerName"], font=self.fonts["small"], fill=self.colours["white"])



        # Lines
        # Vertical
        draw.line((400,90,400,460),width=3,fill=self.colours["white"])
        # Horizontal
        draw.line((40,370,380,370),width=3,fill=self.colours["white"])

        # Compose and save to bytes
        img = Image.alpha_composite(img,overlay_img)

        return SaveToBytes(img)




    @commands.command()
    async def map(self, ctx : commands.context, map_name : str, *, player : CleanContent = None):
        img_bytes = self.GenerateMapImage(map_name, player)

        file = discord.File(img_bytes,f"{map_name}.png")
        await ctx.channel.send(file=file)

        img_bytes.close()
