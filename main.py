import discord
from discord.ext import commands
import traceback

# Import cogs
from src.cogs.profile import Profile
from src.cogs._map import Map

token_file = open("TOKEN.txt","r")
TOKEN = token_file.readline()
token_file.close()

def get_traceback(error: Exception) -> str:
    return ''.join(traceback.format_exception(type(error), error, error.__traceback__))

class Bot(commands.Bot):
    def __init__(self,**kwargs):
        super().__init__(command_prefix='$', fetch_offline_members=True,help_command = None)

    async def close(self):
        await super().close()

    async def on_command_error(self, ctx : commands.context, error : commands.CommandError):
        # Todo
        # Display error to the user
        # Display error to the console
        # Possible log the error
        print("[ERROR]" , commands.CommandError.__name__,": "," ".join(error.args))

        await ctx.send(" ".join(error.args))

    async def on_ready(self):
        print("[BOT] Ready")

    async def on_resumed(self):
        print("[BOT] Resumed")

if __name__ == "__main__":
    kogBot = Bot()
    kogBot.add_cog(Profile(kogBot))
    kogBot.add_cog(Map(kogBot))
    kogBot.run(TOKEN)
