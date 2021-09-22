from discord.ext import commands

import discord
import urllib.parse
import re 

class CleanContent(commands.clean_content):
    def __init__(self):
        super().__init__(fix_channel_mentions=True)

    async def convert(self, ctx: commands.Context, argument: str) -> str:
        if argument[0] == '"' and argument[-1] == '"':
            argument = argument[1:-1]  # strip quotes

        argument = argument.replace('\ufe0f', '')  # remove VS16
        argument = re.sub(r'<a?(:[a-zA-Z0-9_]+:)[0-9]{17,21}>', r'\1', argument)
        return await super().convert(ctx, argument)

def EscapeBackticks(text: str) -> str:
    return text.replace('`', '`\u200b')

def EscapeCustomEmoji(text: str) -> str:
    return re.sub(r'<(a)?:([a-zA-Z0-9_]+):([0-9]{17,21})>', r'<%s\1:\2:\3>' % '\u200b', text)

def Escape(text: str, markdown: bool=True, mentions: bool=True, custom_emojis: bool=True) -> str:
    if markdown:
        text = discord.utils.escape_markdown(text)
    if mentions:
        text = discord.utils.escape_mentions(text)
    if custom_emojis:
        text = EscapeCustomEmoji(text)

    return text

def ToStars(diff : int) -> str:
    return ("★" * diff) + ("☆" * (5 - diff))

def ParseToUrl(text : str) -> str:
    return urllib.parse.quote(text,safe="")

def HumanizeDifficulty(text : str, _reversed = False) -> str:
    if not _reversed:
        if text == "ESY": 
            return "easy"
        if text == "MN": 
            return "main"
        if text == "HRD":
            return "hard"
        if text == "INS":
            return "insane"
        return "mods"
    
    if text == "easy":
        return "ESY"
    if text == "main":
        return "MN"
    if text == "hard":
        return "HRD"
    if text == "insane":
        return "INS"
    return "MODS"

def HumanizePoints(points: int) -> str:
    if points < 1000:
        return str(points)
    else:
        points = round(points / 1000, 1)
        if points % 1 == 0:
            points = int(points)

        return f'{points}K'

