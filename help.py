import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())
tree = app_commands


class HelpCommand(commands.Cog):

    @client.tree.command(name="help", description="Displays info about commands")
    @tree.choices(
        command=[
        Choice(name="Render", value="Render"),
        Choice(name="Random", value="Random"),
        Choice(name="Points", value="Points"),
        Choice(name="Map", value="Map")])
    async def help(self, interaction: discord.Interaction, command: Choice[str]):
        em = discord.Embed(title=f"{command.value} Info")

        if command.value == "Render":
            em.add_field(name="\u200b", value=
"""```html\n
[<USE: Renders a Tee from an asset image.>]

<Image: Attachment | Image to render the tee with> \n[<REQUIRED>]\n
<Eyes: Choice | Which Eye type to use> \n[<OPTIONAL>]\n
<Deg: Number (0-360) | The angle the eyes face> \n[<OPTIONAL>]\n
<Center: Choice | If the eyes are in the center> \n[<OPTIONAL>]\n
<Color: Choice | If the Tee is colored or not> \n[<OPTIONAL>]\n
<Body HSL: 3 Numbers (0-255) | Color for the body> \n[<OPTIONAL>]\n
<Feet HSL: 3 Numbers (0-255) | Color for the feet> \n[<OPTIONAL>]\n

[<ISSUES: None that are known>]
```""")

        elif command.value == "Random":
            em.add_field(name="\u200b", value="```html\n[<USE: Renders a random tee with random settings>]\n[<ISSUES: None that are known>]```")

        elif command.value == "Points":
            em.add_field(name="\u200b", value="```html\n[<USE: Gives a Points stats Image>]\n\n<Player: Name | Profile to check> [<REQUIRED>]\n<Theme: Choice | Color Theme> [<OPTIONAL>]\n\n[<ISSUES: Points Graph offset if user has too few points>]```")

        elif command.value == "Map Info":
            em.add_field(name="\u200b", value="""
```html\n
[<USE: Gives a Map stats Image>]
[<NOTE: All params are optional, but some are required in certain conditions>]

<Map: Name | Map to get stats from.> \n[<REQURED IF TYPE IS NOT UNFINISHED/RANDOM>]\n
<Player: Name | Player to get stats from.> \n[<REQUIRED IF TYPE IS UNFINISHED>]\n
<Category: Choice | Category to pull map from> \n[<OPTIONAL>]\n
<Type: Choice | Pull RANDOM or UNFINISHED map> \n[<OPTIONAL>]\n
<Sort: Choice | Pull UNFINISHED map based off SORT> \n[<OPTIONAL>]

[<ISSUES: Text in Team ranks are not centered if downscaled>]
```""")

        await interaction.response.send_message(embed=em, ephemeral=True)
    
async def setup(client): # Adding the class as a cog
    await client.add_cog(HelpCommand(client))