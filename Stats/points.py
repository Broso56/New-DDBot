# Image Imports
from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime
from io import BytesIO
import aiohttp
import functools

# Discord Imports
import discord
from discord.ui import Button, View, Select
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
import asyncio

global bot_dir
bot_dir = "C:/Users/broso/Desktop/Coding/Python Projects/New DDBot"
intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())
tree = app_commands

async def Scrape(player_name):
    url = f'https://ddnet.tw/players/?json2={player_name}'
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            data = await r.json()  
    return(data)

def GenImage(data, color, player_name): # Generate the Points Stats Image

    # Get Colors
    colors = {
    "Blue" : [(13, 220, 241), "Into The Night"],
    "Purple" : [(144, 87, 192), "Lotus"],
    "Red" : [(241, 13, 101), "Lockdown"],
    "Orange" : [(228, 113, 46), "Willow"],
    "Teal" : [(7, 98, 107), "Not Naufrage 4"]}
    color_rgb = colors[color][0]

    # Load Images
    background = Image.open(f"{bot_dir}/Images/Profile Backgrounds/{colors[color][1]}.png")
    base = Image.open(f"C:/Users/broso/Desktop/Coding/Python Projects/New DDBot/Images/Profile Graphics/{color}/Profile Base.png")
    graph_outline = Image.open(f"C:/Users/broso/Desktop/Coding/Python Projects/New DDBot/Images/Profile Graphics/{color}/Graph Outline.png")
    graph_fill = Image.open(f"C:/Users/broso/Desktop/Coding/Python Projects/New DDBot/Images/Profile Graphics/{color}/Graph Fill.png")

    # Get Image Size
    bg_width, bg_height = background.size
    base_width, base_height = base.size

    # Get Font Data
    fonts_directory = "C:/Users/Broso/AppData/Local/Microsoft/Windows/Fonts" # Font Locations
    montserrat_regular = f"{fonts_directory}/Montserrat-Regular.ttf" # Montserrat-Regular Font

    # Load Font and set size
    def fontsize(font, size):
        font = ImageFont.truetype(font, size)
        return(font)

    # Center image onto another image
    def center(bg_width=0, bg_height=0, fg_width=0, fg_height=0, axis='both', sub_x=0, sub_y=0, off_x=0, off_y=0, subtract_x=False, subtract_y=False):
        # If Statement: Give option to center along only a single axis | Offset center by specific amount
        x = (((bg_width - fg_width) / 2)) if axis == 'horizontal' or axis == 'both' else sub_x
        if not subtract_x: x += off_x
        elif subtract_x: x -= off_x

        y = ((bg_height - fg_height) / 2) if axis == 'vertical' or axis == 'both' else sub_y
        if not subtract_y: y += off_y
        elif subtract_y: y -= off_y

        return(int(x), int(y))

    # Shorten Numbers (1000 -> 1K)
    def humanize_points(points: int) -> str: # Taken from official ddnet bot

        if points < 1000:
            return str(points)
        else:
            points = round(points / 1000, 1)
            if points % 1 == 0:
                points = int(points)

            return f'{points}K'

    # Merge BG and Base images together
    profile = background.copy()
    profile.paste(base, center(bg_width, bg_height, base_width, base_height), base)

    # Write Text
    profile_text = ImageDraw.Draw(profile)

    def WriteText(data, bg, player_name):
        bg_width = bg.width

        # Seperate Data
        str_points = str(data['points']['points']) if 'points' in data else "0"
        str_points_rank = str(data['points']['rank']) if 'points' in data else "0"

        str_points_lastmonth = str(data['points_last_month']['points']) if 'points' in data['points_last_month'] else "0"
        str_points_lastmonth_rank = str(data['points_last_month']['rank']) if 'points' in data['points_last_month'] else "0"

        str_points_lastweek = str(data['points_last_week']['points']) if 'points' in data['points_last_week'] else "0"
        str_points_lastweek_rank = str(data['points_last_week']['rank']) if 'points' in data['points_last_week'] else "0"

        str_teamrank_points = str(data['team_rank']['points']) if 'points' in data['team_rank'] else "0"
        str_teamrank_rank = str(data['team_rank']['rank']) if 'points' in data['team_rank'] else "0"

        str_rank_points = str(data['rank']['points']) if 'points' in data['rank'] else "0"
        str_rank_rank = str(data['rank']['rank']) if 'points' in data['rank'] else "0"


        # Write Text
        # Top Text
        # Why did I not make this a function
        profile_text.text( # Player Name
            center( # Coords
                bg_width=bg_width,
                fg_width=profile_text.textlength(player_name, fontsize(montserrat_regular, 49)), # Get width of text
                axis='horizontal',
                sub_y=20,
                off_x=1,
                subtract_x=True), 
            player_name, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 49)) # Font and Text Size
        profile_text.text( # "Point Stats"
            center( # Coords
                bg_width=bg_width,
                fg_width=profile_text.textlength("Point Stats", fontsize(montserrat_regular, 30)), # Get width of text
                axis='horizontal',
                sub_y=75),
            "Point Stats", # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 30)) # Font and Text Size

        # Total Points and Rank
        # Like come on
        x = 89
        y = 130
        main_text = "Points"
        points_text = str_points
        type_text = "Rank"
        rank_text = str_points_rank
        profile_text.text( # "Points"
            (x, y),
            main_text,
            (255, 255, 255),
            fontsize(montserrat_regular, 25))
        profile_text.text( # Total Points
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(points_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x + 108,
                off_y = y),
            points_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size
        profile_text.text( # "Rank"
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(type_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x,
                off_y = y + 39),
            type_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size
        profile_text.text( # Points Rank
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(rank_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x + 108,
                off_y = y + 39),
            rank_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size

        # Points Last Month and Rank
        # It would have made everything easy
        y += 110
        extra_text = "(Monthly)"
        points_text = str_points_lastmonth
        type_text = "Rank"
        rank_text = str_points_lastmonth_rank
        profile_text.text( # "Points"
            (x, y),
            main_text,
            (255, 255, 255),
            fontsize(montserrat_regular, 25))
        profile_text.text( # "(Monthly)"
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(extra_text, fontsize(montserrat_regular, 15)), # Get width of text
                off_x = x,
                off_y = y + 26),
            extra_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 15)) # Font and Text Size
        profile_text.text( # Points Last Month
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(points_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x + 108,
                off_y = y),
            points_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size
        profile_text.text( # "Rank"
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(type_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x,
                off_y = y + 39),
            type_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size
        profile_text.text( # Points Rank
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(rank_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x + 108,
                off_y = y + 39),
            rank_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size

        # Points Last Week and Rank
        # Instead of spamming
        y += 110
        extra_text = "(Weekly)"
        points_text = str_points_lastweek
        type_text = "Rank"
        rank_text = str_points_lastweek_rank
        profile_text.text( # "Points"
            (x, y),
            main_text,
            (255, 255, 255),
            fontsize(montserrat_regular, 25))
        profile_text.text( # "(Weekly)"
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(extra_text, fontsize(montserrat_regular, 15)), # Get width of text
                off_x = x,
                off_y = y + 26),
            extra_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 15)) # Font and Text Size
        profile_text.text( # Points Last Week
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(points_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x + 108,
                off_y = y),
            points_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size
        profile_text.text( # "Rank"
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(type_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x,
                off_y = y + 39),
            type_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size
        profile_text.text( # Points Rank
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(rank_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x + 108,
                off_y = y + 39),
            rank_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size

        # Rank Points and Rank
        # A million lines of code
        x = 725
        y = 187
        extra_text = "(Rank)"
        points_text = str_rank_points
        type_text = "Rank"
        rank_text = str_rank_rank
        profile_text.text( # "Points"
            (x, y),
            main_text,
            (255, 255, 255),
            fontsize(montserrat_regular, 25))
        profile_text.text( # "(Rank)"
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(extra_text, fontsize(montserrat_regular, 15)), # Get width of text
                off_x = x,
                off_y = y + 26),
            extra_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 15)) # Font and Text Size
        profile_text.text( # Rank Points
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(points_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x + 108,
                off_y = y),
            points_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size
        profile_text.text( # "Rank"
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(type_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x,
                off_y = y + 39),
            type_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size
        profile_text.text( # Points Rank
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(rank_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x + 108,
                off_y = y + 39),
            rank_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size

        # Team Rank Points and Rank
        # For basic text
        y += 104
        extra_text = "(Team Rank)"
        points_text = str_teamrank_points
        type_text = "Rank"
        rank_text = str_teamrank_rank
        profile_text.text( # "Points"
            (x, y),
            main_text,
            (255, 255, 255),
            fontsize(montserrat_regular, 25))
        profile_text.text( # "(Rank)"
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(extra_text, fontsize(montserrat_regular, 15)), # Get width of text
                off_x = x,
                off_y = y + 26),
            extra_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 15)) # Font and Text Size
        profile_text.text( # Rank Points
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(points_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x + 108,
                off_y = y),
            points_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size
        profile_text.text( # "Rank"
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(type_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x,
                off_y = y + 39),
            type_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size
        profile_text.text( # Points Rank
            center( # Coords
                bg_width=profile_text.textlength(main_text, fontsize(montserrat_regular, 25)),
                fg_width=profile_text.textlength(rank_text, fontsize(montserrat_regular, 25)), # Get width of text
                off_x = x + 108,
                off_y = y + 39),
            rank_text, # Text
            (255, 255, 255), # Color
            fontsize(montserrat_regular, 25)) # Font and Text Size

    # Draw Points Graph
    def DrawGraph(data):
        points = []
        time_finish = []
        for category in data['types']: # Loop through all categories
            category = data['types'][category]
            for map in category['maps']: # Loop through all maps in all categories
                maps = category['maps']
                if 'rank' in maps[map]: # Check if player has finished the map
                    points.append(maps[map]['points'])
                    time_finish.append(maps[map]['first_finish'])

        def NewRange(old_value, old_range, new_range): # Convert a range into a new range (e.g 1,000 - 10,000 to 0 - 1)
            old_min, old_max = old_range
            new_min, new_max = new_range
            old_range = old_max - old_min
            new_range = new_max - new_min
            new_value = (((old_value - old_min) * new_range) / old_range) + new_min
            return(new_value)


        points = [points for _, points in sorted(zip(time_finish, points))] # Reorder points list based on timestamp value (least to greatest)
        time_finish = sorted(time_finish) # Reorder time_finish list

        i = 0

        current_date = int(datetime.now().timestamp())
        time_max = current_date
        time_min = int(time_finish[0])
        time_range = []

        points_total = sum(points)
        points_max = points_total
        points_min = 0
        points_range = []
        points_value = 0

        ss_mult = 3 # Supersampling multiplier
        line_width = 3 * ss_mult
        graph_size = (bg_width * ss_mult, bg_height * ss_mult)
        graph_width, graph_height = graph_size

        x_mult = 280 * ss_mult
        x_add = 360 * ss_mult
        y_mult = int((172 - (line_width / ss_mult)) * ss_mult)
        y_add = 361 * ss_mult
        for _ in time_finish: # Points and Time_Finish lists are lined up, so only need one for loop
            time_value = time_finish[i]
            points_value -= points[i]

            time_range.append(int(NewRange(time_value, (time_min, time_max), (0, 1)) * x_mult + x_add)) # Multiply by width of graph box, add by X Coordinate, Multiply by 3 for supersampling
            points_range.append(int(NewRange(points_value, (points_min, points_max), (0, 1)) * y_mult + y_add)) # Multiply same as above, but subtract by line width/3 from multiplier
            i += 1

        coords = list(zip(time_range, points_range)) # Create a list of tuples, where points is the Y Coordinate and the time is the X Coordinate
        coords.append((640 * ss_mult, int(NewRange(points_value - points[i-1], (points_min, points_max), (0, 1)) * y_mult + y_add)))

        graph = Image.new("RGBA", graph_size)

        graph_line = ImageDraw.Draw(graph)
        graph_line.line(coords, fill=color_rgb, width=line_width)

        graph = graph.resize((bg_width, bg_height), resample=Image.ANTIALIAS)

        # Add text to graph box
        first_finish_date = datetime.fromtimestamp(int(time_finish[0])).year - 2000 # Get just the 2 numbers from the year, eg 23 for 2023
        current_year = datetime.now().year - 2000

        year_add = 31536000
        start_year = 1325376000 # Jan 1st 2012
        year_stamps = { # 2013-2029
            2013 : start_year + year_add,
            2014 : start_year + (year_add * 2),
            2015 : start_year + (year_add * 3),
            2016 : start_year + (year_add * 4),
            2017 : start_year + (year_add * 5),
            2018 : start_year + (year_add * 6),
            2019 : start_year + (year_add * 7),
            2020 : start_year + (year_add * 8),
            2021 : start_year + (year_add * 9),
            2022 : start_year + (year_add * 10),
            2023 : start_year + (year_add * 11),
            2024 : start_year + (year_add * 12),
            2025 : start_year + (year_add * 13),
            2026 : start_year + (year_add * 15),
            2027 : start_year + (year_add * 16),
            2028 : start_year + (year_add * 17),
            2029 : start_year + (year_add * 18),
        }
        year_list = [first_finish_date + 2000]
        finish_year = int(time_finish[0]) 

        x_mult /= ss_mult
        x_add /= ss_mult
        x = 321 # Points Grid
        y_mult /= ss_mult
        y_add /= ss_mult
        y_sub = 10
        y = 371 # Time Grid

        while finish_year < datetime.now().timestamp(): # Calculate what years are in between first finish and current date

            finish_year += year_add # Increment by one year

            year_list.append(datetime.fromtimestamp(int(finish_year)).year)


        time_grid = Image.new("RGBA", (1000, 500))
        alpha = 25
        for year in year_list:
            if year_stamps[year] >= time_min and year_stamps[year] + 2678400 <= time_max: # Dont Show the last year unless its 1 month after the start of the year
                profile_text.text( # Year Text
                    (int(NewRange(year_stamps[year], (time_min, time_max), (0, 1)) * x_mult + x_add), y), # Coords
                    f"'{str(year)[2:4]}", # Text
                    (255, 255, 255), # Color
                    fontsize(montserrat_regular, 15)) # Font and Text Size

            if year_stamps[year] >= time_min and year_stamps[year] <= time_max:
                time_grid_line = ImageDraw.Draw(time_grid)
                time_grid_x = int(NewRange(year_stamps[year], (time_min, time_max), (0, 1)) * x_mult + x_add)
                time_grid_coords = [(time_grid_x, 361), (time_grid_x, 190)] 
                time_grid_line.line(time_grid_coords, fill=(255, 255, 255, alpha), width=2)

        thresholds = { # Points Threshold
            15000: 5000,
            10000: 2500,
            5000:  2000,
            3000:  1000,
            1000:  500,
            0:     250,
        }

        steps = next(s for t, s in thresholds.items() if points_total > t)
        points_step = 0
        i = 0
        points_grid = Image.new("RGBA", (1000, 500))

        while i <= points_total:
            profile_text.text(
                center( # Coords
                    bg_width=profile_text.textlength("00.0K", fontsize(montserrat_regular, 12)),
                    fg_width=profile_text.textlength(humanize_points(abs(points_step)), fontsize(montserrat_regular, 12)), # Get width of text
                    off_x = x,
                    off_y = int(NewRange(points_step, (points_min, points_max), (0, 1)) * y_mult + y_add - y_sub)),
                humanize_points(abs(points_step)),
                (255, 255, 255),
                fontsize(montserrat_regular, 12),
            )
            points_grid_line = ImageDraw.Draw(points_grid)
            points_grid_y = int(NewRange(points_step, (points_min, points_max), (0, 1)) * y_mult + y_add)
            points_grid_coords = [(360, points_grid_y), (639, points_grid_y)] 
            points_grid_line.line(points_grid_coords, fill=(255, 255, 255, alpha + 50), width=2)

            i += steps
            points_step -= steps

        profile_text.text( # Total Points
            center( # Coords
                bg_width=profile_text.textlength("00.0K", fontsize(montserrat_regular, 12)),
                fg_width=profile_text.textlength(humanize_points(points_total), fontsize(montserrat_regular, 12)), # Get width of text
                off_x = x + 323,
                off_y = int(NewRange(points_total, (points_min, points_max), (0, 1)) * y_mult + y_add - 345)),
            humanize_points(points_total),
            (255, 255, 255),
            fontsize(montserrat_regular, 12),
        )

        return(time_grid, points_grid, graph)
    
    # Call Functions
    WriteText(data, background, player_name)
    graph_data = DrawGraph(data)

    # Seperate Data
    time_grid = graph_data[0]
    points_grid = graph_data[1]
    graph = graph_data[2]

    # Merge all images into final image
    profile.paste(graph_fill, center(bg_width, bg_height, base_width, base_height), graph_fill)
    profile.paste(time_grid, center(bg_width, bg_height, base_width, base_height), time_grid)
    profile.paste(points_grid, center(bg_width, bg_height, base_width, base_height), points_grid)
    profile.paste(graph, center(bg_width, bg_height, base_width, base_height, off_x=1, off_y=2), graph) # Line Graph gets rendered over box fill and grid but under the box outline
    profile.paste(graph_outline, center(bg_width, bg_height, base_width, base_height), graph_outline)

    with BytesIO() as img_binary: # This is to be able to send the image as a message without having to save it locally
        profile.save(img_binary, 'PNG')
        img_binary.seek(0)
        file = discord.File(fp=img_binary, filename="image.png")

    return(file)


class UserPoints(commands.Cog): # Cog initiation
    def __init__(self, client):
        self.client = client
        
    @client.tree.command(name="points", description='Generate a points stats image')
    @tree.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    @tree.choices(
        theme=[
            Choice(name="Blue", value="Blue"),
            Choice(name="Purple", value="Purple"),
            Choice(name="Red", value="Red"),
            Choice(name="Orange", value="Orange"),
            Choice(name="Teal", value="Teal")
            ])
    async def points(self, interaction: discord.Interaction, player: str, theme: Choice[str]):
        
        await interaction.response.defer()
        player_name = player
        data = await Scrape(player_name)

        if data == {}:
            raise Exception("Player Doesn't Exist")
            return

        else:
            gen_image_params = functools.partial(GenImage, data, theme.value, player_name)
            async with client:
                file = await client.loop.run_in_executor(None, gen_image_params) # Generate the points Image, run in executor to prevent PIL from blocking
            await interaction.followup.send(file=file)
        
    
    @points.error # Error Handling
    async def on_points_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"```arm\nERROR: \"{error}\"\n```", ephemeral=True) # Errors before Interaction response
        else: # TODO: Fix so ephemeral actually works
            if "Command 'points' raised an exception: Exception:" in str(error):
                error = str(error).replace("Command 'points' raised an exception: Exception:", "")[1:]
            await interaction.followup.send(f"```arm\nERROR: \"{error}\"\n```", ephemeral=True) # Errors after Interaction response

async def setup(client): # Adding the class as a cog
    await client.add_cog(UserPoints(client))
