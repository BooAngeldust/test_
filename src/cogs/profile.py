from PIL import Image, ImageFont, ImageDraw
from discord.ext import commands
import discord
from io import BytesIO

from src.libs.https_request import Request 
from src.libs.text import CleanContent, ToStars, HumanizeDifficulty
from src.libs.utils import RoundRect, NormalizeSeconds, ConvertTime, SaveToBytes, GetTextSize
from src.libs.resourses import Resources

from src.libs.graph import Player, Graph



class Profile(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot

        self.fonts       = Resources.GetFonts()
        self.colours     = Resources.GetColours()
        self.resources   = Resources.GetResources()
        self.thresholds = {}

        # Init thresholds
        self.thresholds["insane"] = 0.9
        self.thresholds["hard"]   = 0.7
        self.thresholds["main"]   = 0.4
        self.thresholds["easy"]   = 0.0
    
    def GeneratePointsImage(self, players : list) -> BytesIO:
        return Graph.Create(players)

    def GenerateProfileImage(self, player_name : str) -> BytesIO:
        try:
            player_info = Request.PlayerInfo(player_name)["profile"]
        except Exception as e:
            raise commands.CommandError(e.args[0])
        
        if player_info["Name"] == None:
            raise commands.CommandError(f"Player `{player_name}` not found")

        # Convert nulls to 0 
        if player_info["gold"] == None: 
            player_info["gold"] = "0"
        if player_info["silver"] == None: 
            player_info["silver"] = "0"
        if player_info["bronze"] == None:
            player_info["bronze"] = "0"

        player_info["PvPpoints"] = str(int(float(player_info["PvPpoints"])))
        player_info["TotalTime"] = NormalizeSeconds(int(player_info["TotalTime"]))
        player_info["LastTime"] = ConvertTime(player_info["LastTime"])

        
        # Decide on theme based of maps finished ratio
        maps_passed_ratio = int(player_info["MapsPassed"]) / int(player_info["MapsAmount"])

        if maps_passed_ratio >= self.thresholds["insane"]:
            active_colour = self.colours["pink"]
            img           = self.resources["bg_insane"].copy()

        elif maps_passed_ratio >= self.thresholds["hard"]:
            active_colour = self.colours["blue"]
            img           = self.resources["bg_hard"].copy()

        elif maps_passed_ratio >= self.thresholds["main"]:
            active_colour = self.colours["light_blue"]
            img           = self.resources["bg_main"].copy()

        else:
            active_colour = self.colours["green"]
            img           = self.resources["bg_easy"].copy()

        # Create image 
        overlay_img = Image.new("RGBA",img.size,(0,0,0,0))

        # Create dark and name round rectangle
        overlay_img = Image.alpha_composite(overlay_img,self.resources["dark_rect_profile"].copy())

        # Add medals
        overlay_img.paste(self.resources["medal_gold"],(420,8),self.resources["medal_gold"])
        overlay_img.paste(self.resources["medal_silver"],(510,8),self.resources["medal_silver"])
        overlay_img.paste(self.resources["medal_bronze"],(600,8),self.resources["medal_bronze"])

        # ImageDraw object
        draw = ImageDraw.Draw(overlay_img)

        # Add name  
        draw.text((220 - GetTextSize(player_name,self.fonts["medium"])[0] // 2,13), player_name, fill=self.colours["white"], font=self.fonts["medium"])

        # Add medal values
        draw.text((465,23),player_info["gold"],fill=self.colours["white"],font=self.fonts["medium"])
        draw.text((555,23),player_info["silver"],fill=self.colours["white"],font=self.fonts["medium"])
        draw.text((645,23),player_info["bronze"],fill=self.colours["white"],font=self.fonts["medium"])

        # POINTS
        draw.text((60,60),"POINTS",fill=self.colours["white"],font=self.fonts["medium_bold"])

        # Add points values
        # Fixed points
        points_rank_size = GetTextSize(f"#{player_info['PointsRank']}", self.fonts["medium"])[0]
        draw.text((60,120), f"#{player_info['PointsRank']}", fill=active_colour, font=self.fonts["medium"])
        draw.line((70 + points_rank_size, 125, 70 + points_rank_size, 143), width=2, fill=self.colours["white"])
        draw.text((83 + points_rank_size, 99), f"{player_info['Points']}", fill=active_colour, font=self.fonts["extreme"])
        draw.text((60,150), "FIXED", fill=self.colours["white"], font=self.fonts["medium_bold"])

        # Season points
        points_rank_size = GetTextSize(f"#{player_info['SPointsRank']}", self.fonts["medium"])[0]
        draw.text((60,210), f"#{player_info['SPointsRank']}", fill=active_colour, font=self.fonts["medium"])
        draw.line((70 + points_rank_size, 215, 70 + points_rank_size, 233), width=2, fill=self.colours["white"])
        draw.text((83 + points_rank_size, 189), f"{player_info['Seasonpoints']}", fill=active_colour, font=self.fonts["extreme"])
        draw.text((60,240), "SEASON", fill=self.colours["white"], font=self.fonts["medium_bold"])

        # PvP points
        points_rank_size = GetTextSize(f"#{player_info['PvPPointsRank']}", self.fonts["medium"])[0]
        draw.text((60,300), f"#{player_info['PvPPointsRank']}", fill=active_colour, font=self.fonts["medium"])
        draw.line((70 + points_rank_size, 305, 70 + points_rank_size, 323), width=2, fill=self.colours["white"])
        draw.text((83 + points_rank_size, 279), f"{player_info['PvPpoints']}", fill=active_colour, font=self.fonts["extreme"])
        draw.text((60,330), "PVP", fill=self.colours["white"], font=self.fonts["medium_bold"])

        # TEAMMATES 
        draw.text((355,60),"TOP 3 TEAMMATES", fill=self.colours["white"], font=self.fonts["medium_bold"])

        # Add top teammates
        player_info.setdefault("Teammate",[])
        player_info.setdefault("TeamFinishes",[])

        teammates_y_pos = 100
        for teammate, finishes in zip(player_info["Teammate"],player_info["TeamFinishes"]):
            teammate_name_size = GetTextSize(teammate, self.fonts["medium"])[0]
            finishes_size = GetTextSize(finishes,self.fonts["medium"])[0]
            draw.text((360,teammates_y_pos),teammate, fill=active_colour, font=self.fonts["medium"])
            draw.line((370 + teammate_name_size, teammates_y_pos+5, 370 + teammate_name_size, teammates_y_pos+22), width=2, fill=self.colours["white"])
            draw.text((383 + teammate_name_size,teammates_y_pos), finishes, fill=active_colour, font=self.fonts["medium"])
            draw.text((388 + teammate_name_size + finishes_size,teammates_y_pos + 7),"FINISHES",fill=self.colours["white"],font=self.fonts["small"])
            teammates_y_pos += 30

        # Add map finishes
        # MAP FINISHES
        draw.text((355,210), "MAP FINISHES", fill=self.colours["white"], font=self.fonts["medium_bold"])

        # Total maps passed
        maps_passed_size = GetTextSize(player_info["MapsPassed"],font=self.fonts["large"])[0]
        maps_total_size = GetTextSize(f"/{player_info['MapsAmount']}",font=self.fonts["large"])[0]

        draw.text((355,250),player_info["MapsPassed"],fill=active_colour,font=self.fonts["large"])
        draw.text((355 + maps_passed_size,250),f"/{player_info['MapsAmount']}",fill=self.colours["white"],font=self.fonts["large"])
        draw.line((365 + maps_passed_size + maps_total_size,255,365 + maps_passed_size + maps_total_size,282),width=2,fill=self.colours["white"])
        draw.text((378 + maps_passed_size + maps_total_size,250),player_info["TotalTime"],fill=active_colour,font=self.fonts["large"])
        draw.text((355,285),"TOTAL MAPS PASSED", fill=self.colours["white"],font=self.fonts["small"])

        # Last map passed
        map_size = GetTextSize(player_info["LastMap"],self.fonts["medium"])[0]
        draw.text((355, 310), player_info["LastMap"],fill=active_colour,font=self.fonts["medium"])
        draw.line((365 + map_size, 315, 365 + map_size, 333), width=2, fill=self.colours["white"])
        draw.text((378 + map_size, 310), player_info["LastTime"], fill=active_colour, font=self.fonts["medium"])
        draw.text((355,340),"LAST MAP PASSED",fill=self.colours["white"],font=self.fonts["small"])


        # Add lines
        draw.line((55,90,310,90), width=2, fill=self.colours["white"])
        draw.line((350,90,660,90), width=2, fill=self.colours["white"])
        draw.line((350,240,660,240), width=2, fill=self.colours["white"])

       # Composing
        img = Image.alpha_composite(img,overlay_img)

        return SaveToBytes(img)
    
    @commands.command(aliases=["p"])
    async def profile(self, ctx : commands.context,*, player : CleanContent = None):
        await ctx.trigger_typing()
        player = player or ctx.author.display_name
        # rework this
        if player == "@deleted-user":
            raise commands.CommandError("No player with that name")
        
        img_bytes = self.GenerateProfileImage(player)
        file = discord.File(img_bytes,f"{player}.png")
        await ctx.channel.send(file=file)

        img_bytes.close()

    @commands.command(aliases=["pts"])
    async def points(self,ctx : commands.context, *players : CleanContent):
        await ctx.trigger_typing()


        if len(players) == 0:
            players = (ctx.author.display_name,)

        _players = []

        # Max players = 5
        if len(players) > 5:
            raise commands.CommandError("It is possible to request 5 players at max")

        # Fetch info from api
        for player in players:
            info = Request.PointsInfo(player)
            # Player not found
            if info["points"] == None:
                if player == "@deleted-user":
                    raise commands.CommandError(f"No player with that name")
                raise commands.CommandError(f"No player with name: `{player}`")
            
            info = info["points"]
            _players.append(Player(player,info["Points"],info["Date"]))
        
        img_bytes = self.GeneratePointsImage(_players)
        file = discord.File(img_bytes,f"{'_'.join(players)}.png")
        await ctx.channel.send(file=file)

        img_bytes.close()

    @commands.command(aliases=["unf"])
    async def unfinished(self, ctx : commands.context, player : CleanContent, diff : str = None):
        await ctx.trigger_typing()

        if diff == None:
            raise commands.CommandError("Server category is missing.")

        diff = diff.lower()

        if diff not in ["easy","main","mods","hard","insane"]:
            raise commands.CommandError("Invalid Server category.")

        _diff = HumanizeDifficulty(diff, True)

        info = Request.UnfinishedInfo(player, _diff)
        info = info["points"]

        # Fetch info
        if info == None:
            await ctx.channel.send(f"Player `{player}` finished all maps")
            return

        

        maps_per_page = 8
        cur_page = 0
        max_page = len(info) // maps_per_page

        def GenerateEmbed() -> discord.Embed:
            embed = discord.Embed(title=f"{player} | Unfinished | {diff.title()} | {cur_page+1}/{max_page+1}", color=0x003366)
            for field in range(cur_page * maps_per_page,cur_page * maps_per_page + maps_per_page):
                if field < len(info):
                    embed.add_field(name=f"{info[field]['Map']} | {info[field]['Mapper']}", value=f"{ToStars(int(info[field]['Stars']))} | {info[field]['Points']} points", inline=False)
                else:
                    break

            return embed

        embed = GenerateEmbed()

        msg = await ctx.channel.send(embed=embed, delete_after=300)

        await msg.add_reaction('⬆')
        await msg.add_reaction('⬇')

        while True:
            reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id)
            
            if reaction.message.id == msg.id:
                if str(reaction.emoji) == '⬆':
                    if cur_page >= 1:
                        cur_page -= 1
                    embed = GenerateEmbed()
                    await msg.edit(embed=embed)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == '⬇':
                    if cur_page < max_page:
                        cur_page += 1
                    embed = GenerateEmbed()
                    await msg.edit(embed=embed)
                    await msg.remove_reaction(reaction, user)
            
        
