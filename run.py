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
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())
tree = app_commands
discord.utils.setup_logging()

class DiscordBot(commands.Bot): # Override setup hook
    async def setup_hook():
        pst = pytz.timezone('US/Pacific')
        psttime = datetime.datetime.now(pst)
        current_time = psttime.strftime('%I:%M %p PST.')
        print(f"READY: Bot readied at {current_time}")

        try:
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

        # Cog Setup
        await client.load_extension('Stats.points')
        await client.load_extension('Misc.Tee Render')
        await client.load_extension('Misc.Random Tee Render')
        await client.load_extension('test')
        await client.start(token) # Client token. NEVER share this with anyone, as it gives them access to your bot.

@client.tree.command(name='reload')
@tree.choices(command=[
    Choice(name='Points', value='Stats.points'),
    Choice(name='Render', value='Misc.Tee Render'),
    Choice(name='Random', value='Misc.Random Tee Render'),
    Choice(name='Test', value='test')
    ])

@commands.is_owner() # Make this command only available to the bot owner
async def reload(interaction: discord.Interaction, command: Choice[str]):
    await client.reload_extension(command.value)

    try:
        await client.tree.sync()
    except Exception as e:
        print(e)

    await interaction.response.send_message(f'{command.name} command reloaded!', ephemeral=True)

asyncio.run(DiscordBot.setup_hook())