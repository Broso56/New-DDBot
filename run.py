from bottoken import token
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import datetime
import pytz
import asyncio


intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all(), owner_id=363896262522699776) # Broso56 ID
tree = app_commands
discord.utils.setup_logging()

class DiscordBot(commands.Bot): # Override setup hook
    async def setup_hook():
        pst = pytz.timezone('US/Pacific')
        psttime = datetime.datetime.now(pst)
        current_time = psttime.strftime('%I:%M %p PST.')
        print(f"READY: Bot readied at {current_time}")

        # Cog Setup
        await client.load_extension('Stats.points')
        await client.load_extension('Stats.mapinfo')
        await client.load_extension('Misc.Tee Render')
        await client.load_extension('Misc.Random Tee Render')
        await client.load_extension('test')
        await client.start(token) # Client token. NEVER share this with anyone, as it gives them access to your bot.

@client.tree.command(name='reload')
@tree.choices(command=[
    Choice(name='Points', value='Stats.points'),
    Choice(name='Map', value="Stats.mapinfo"),
    Choice(name='Render', value='Misc.Tee Render'),
    Choice(name='Random', value='Misc.Random Tee Render'),
    Choice(name='Test', value='test')
    ])

async def reload(interaction: discord.Interaction, command: Choice[str]):
    if not interaction.user.id == client.owner_id: # Make this only available to owner
        raise Exception("Only the bot owner can use this command.")

    await client.reload_extension(command.value)
    await interaction.response.send_message(f'{command.name} command reloaded!', ephemeral=True)

@reload.error
async def on_reload_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if "Command 'reload' raised an exception: Exception:" in str(error):
        error = str(error).replace("Command 'reload' raised an exception: Exception:", "")[1:]
    await interaction.response.send_message(f"```arm\nERROR: \"{error}\"\n```", ephemeral=True)

@client.command(name="sync")
@commands.is_owner()
async def sync(interaction: discord.Interaction):
    try:
        synced = await client.tree.sync()
        await interaction.response.send_message(f"Synced {len(synced)} command(s)", ephemeral=True)
        return
    except Exception as e:
        await interaction.response.send_message(str(e), ephemeral=True)
        return

asyncio.run(DiscordBot.setup_hook())
async def autosync():
    await client.tree.sync()

autosync()