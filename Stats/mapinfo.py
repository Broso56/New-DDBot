from PIL import Image, ImageDraw, ImageFont, ImageFilter
import datetime
from io import BytesIO
import aiohttp
import functools
import random as rd
import string

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

async def Scrape(player=None, map=None, img_url=None):
    if player is not None: # Get Player Data
        url = f'https://ddnet.tw/players/?json2={player}'
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                player_data = await r.json()  
        return(player_data)
    
    if map is not None: # Get Map Data
        url = f'https://ddnet.tw/maps/?json={map}'
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                map_data = await r.json()
        return(map_data)
    
    if img_url is not None: # Get Map Image
        async with aiohttp.ClientSession() as cs:
            async with cs.get(img_url) as r:
                img = await r.read()
        return(img)
                
async def GetData(player=None, map=None, random=False, category="All", unfinished=False, sort_most=False):
    categories = [
    "Novice", "Moderate", "Brutal", "Insane", # Core types
    "Dummy", "Oldschool", "Solo", "Race", "Fun", # Misc types
    "DDmaX.Easy", "DDmaX.Next", "DDmaX.Pro", "DDmaX.Nut"] # DDmaX types

    if unfinished:
        if player is None:
            raise Exception("Invalid Player")
        
        player_data = await Scrape(player=player)
        if player_data != {}:
            unf_list = []
            fin_count = []
            for current_category in categories: # For every category
                if category == "All" or category == current_category:
                    category = current_category
                else:
                    continue

                for m in player_data["types"][category]["maps"]: # For every map in every category
                    m_data = player_data["types"][category]["maps"][m]
                    if "rank" not in m_data: # Check if unfinished
                        unf_list.append(m) # Add Unfinished map to list
                        fin_count.append(m_data["total_finishes"]) # Add Finish Count
            
            if unf_list == []: # Return if player has all maps finished
                raise Exception("No Unfinished")

            if sort_most: # Most Finished
                unf_map = [unf_map for _, unf_map in sorted(zip(fin_count, unf_list), reverse=True)] # Find most finished map that the player doesnt have
                unf_map = unf_map[0]
                print(f"MAPS:{unf_map}")
                map_data = await Scrape(map=unf_map)
            
            else: # Random
                map = rd.choice(unf_list) # Pick Random unfinished map
                map_data = await Scrape(map=map)

    elif random:
        if category == "All":
            category = rd.choice(categories)

        print(category)
        player_data = await Scrape(player="Broso56") # Scrape from my profile for a random map (Doesn't matter what profile)
        map_list = []
        for m in player_data["types"][category]["maps"]:
            map_list.append(m)

        map = rd.choice(map_list) # Pick a random map
        map_data = await Scrape(map=map)
    
    elif map is not None:
        map_data = await Scrape(map=map)
    
    else:
        raise Exception("Invalid Map")
    
    return map_data

def DrawMap(map_data, img):

    # Get Font Data
    fonts_directory = "C:/Users/Broso/AppData/Local/Microsoft/Windows/Fonts" # Font Locations
    montserrat_regular = f"{fonts_directory}/Montserrat-Regular.ttf" # Montserrat-Regular Font
    montserrat_bold = f"{fonts_directory}/Montserrat-Bold.ttf" # Montserrat-Bold Font
    dejavu_sans = f"{fonts_directory}/DejaVuSans.ttf" # DejaVu Sans Font (Backup for chars montserrat cant display)

    # Find most common color
    def get_dominant_color(pil_img, palette_size=16):
        # Resize image to speed up processing
        img = pil_img.copy()
        img.thumbnail((100, 100))

        # Reduce colors (uses k-means internally)
        paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)

        # Find the color that occurs most often
        palette = paletted.getpalette()
        color_counts = sorted(paletted.getcolors(), reverse=True)
        palette_index = color_counts[0][1]
        dominant_color = palette[palette_index*3:palette_index*3+3]

        return dominant_color

    def center(bg_size, fg_size, off_x=0, off_y=0, axis="all"): # Center Image onto another image
        bg_width, bg_height = bg_size
        fg_width, fg_height = fg_size

        if axis == "horizontal" or axis == "all":
            x = (bg_width - fg_width) / 2
            x += off_x
            if axis == "horizontal":
                return(int(x))

        if axis == "vertical" or axis == "all":
            y = (bg_height - fg_height) / 2
            y += off_y
            if axis == "vertical":
                return(int(y))

        return(int(x), int(y))

    def RGBtoHSL(rgb):
        r, g, b = rgb
        # Convert to 0-1 range
        r /= 255
        g /= 255
        b /= 255

        # Find the min and max values of RGB
        cmin = min([r, g, b])
        cmax = max([r, g, b])

        # Calculate Luminance by adding min/max and divide by 2
        l = (cmin + cmax) / 2

        # Check if there is no saturation
        if cmin == cmax: # If saturation is 0:
            h = 0
            s = 0

        else: # Calculate Hue & Saturation
            # Saturation:
            if l <= 0.5:
                s = (cmax-cmin)/(cmax+cmin)
            else:
                s = (cmax-cmin)/(2-cmax-cmin)
            # Hue:
            if cmax == r: h = (g-b)/(cmax-cmin)
            if cmax == g: h = 2+(b-r)/(cmax-cmin)
            if cmax == b: h = 4+(r-g)/(cmax-cmin)
            # Convert Hue to degrees
            h *= 60
            if h < 0: h += 360 # If negative add 360

            # Convert Saturation and Luminance to 0-100 range
            s *= 100
            l *= 100

        return(int(h), int(s), int(l))

    # Based off of the HSL to RGB Formula at:
    # https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB
    def HSLtoRGB(hsl):
        h, s, l = hsl
        # Convert Saturation and Luminance to 0-1 scale
        s /= 100
        l /= 100

        # Find Chroma
        c = (1 - abs(2*l-1)) * s

        # Find points along bottom 3 faces of RGB Cube
        h /= 60
        x = c * (1 - abs(h%2-1))

        # Choose formula
        if 0 <= h < 1: r, g, b = c, x, 0
        if 1 <= h < 2: r, g, b = x, c, 0
        if 2 <= h < 3: r, g, b = 0, c, x
        if 3 <= h < 4: r, g, b = 0, x, c
        if 4 <= h < 5: r, g, b = x, 0, c
        if 5 <= h < 7: r, g, b = c, 0, x

        # Add Luminance
        m = l - (c/2)
        r += m
        g += m
        b += m

        return(int(r*255), int(g*255), int(b*255))

    def DrawLine(coords=((0, 0), (100, 0)), fill="white", width=1, supersampling=True):
        size = (1200, 500)
        if supersampling:
            # Multiply everything by supersampling multipler
            ss_mult = 3
            new_coords = []
            for coord in coords:
                new_coords.append(tuple([pos * ss_mult for pos in coord]))

            new_coords = tuple(new_coords)
            size = (1200*ss_mult, 500*ss_mult)
            width *= ss_mult

        line = Image.new("RGBA", (size), (0, 0, 0, 0))
        line_draw = ImageDraw.Draw(line)
        line_draw.line(coords, fill=fill, width=width)
        if supersampling:
            line = line.resize((1200, 500), resample=Image.LANCZOS)

        return(line)

    def DrawRectangle(rect_size, outline=(0, 0, 0, 0), fill=(0, 0, 0, 0), width=1, radius=0, supersampling=True):
        ss_mult = 3
        rect_width, rect_height = rect_size

        if supersampling: # Multiply parameters for supersampling
            rect_width *= ss_mult
            rect_height *= ss_mult
            width *= ss_mult
            radius *= ss_mult

        # Make new image, initialize Draw
        rect = Image.new("RGBA", (rect_width, rect_height), (0, 0, 0, 0))
        rect_draw = ImageDraw.Draw(rect)

        if radius > 0: # Rounded Rectangle
            rect_draw.rounded_rectangle((0, 0, rect_width, rect_height), outline=outline, fill=fill, width=width, radius=radius)
        else: # Normal Rectangle
            rect_draw.rectangle((0, 0, rect_width, rect_height), outline=outline, fill=fill, width=width)

        if supersampling: # Resize to normal size if supersampling is on
            rect = rect.resize(rect_size, resample=Image.LANCZOS)

        return(rect)

    def DrawText(img, text="Text", size=25, pos=(0, 0), font=montserrat_regular, fill="white", max_length=0, dynamic=False, center=False):
        # TODO: Fix text centering if downscaled
        for s in text:
            if s not in string.printable: font = dejavu_sans; break # DejaVu-Sans supports special unicode characters

        length = img.textlength(text, ImageFont.truetype(font, size))
        if dynamic:
            x = pos[0]
            y = pos[1]
            while length > max_length:
                size -= 1
                y += 1
                length = img.textlength(text, ImageFont.truetype(font, size))
            pos = (x, y)

        if center:
            x = pos[0]
            y = pos[1]
            x -= int(length/2)
            pos = (x, y)

        img.text(pos, text=text, fill=fill, font=ImageFont.truetype(font, size))
        return img

    def ParseTime(sec):
        time = str(datetime.timedelta(seconds = sec))
        if sec < 3600: time = time[2:]
        if sec < 60: time = time[1:]
        if '.' in time: time = time[:len(time)-4]
        else: time += ".00"
        return(str(time))

    def MaxLength(ranks, threshold, font, size):
        i = 0
        time_lengths = []
        for rank in ranks:
            # Limit to 5 ranks, 10 if solo
            if i >= threshold:
                break
            time = ParseTime(rank["time"])

            # Add length of text to list
            time_lengths.append(map_text_draw.textlength(f"{time} ", ImageFont.truetype(font, size)))
            i += 1
        return(max(time_lengths))

    # Open Image
    img_bytes = BytesIO(img)
    img_bytes.seek(0)
    map_bg = Image.open(img_bytes) # Background
    map_bg = map_bg.convert("RGB")
    map_img = map_bg.copy() # Center Image

    # Get & Adjust Colors
    color = get_dominant_color(map_bg) # Get Average color
    h, s, l = RGBtoHSL(color) # Increase saturation and Luminance
    if s > 20 and l > 20:
        s += (20 / (s / 25))
        l += (30 / (l / 25))
    else:
        s += 20
        l += 30
    color = list(HSLtoRGB((h, s, l)))
    color.append(255) # Add alpha channel
    color = tuple(color)
    fcolor = (7, 34, 40, 175)
    fcolor2 = (2, 29, 35, 175)

    # Upscale to target width with same ratio; Crop to the final image size
    map_bg = map_bg.resize((1200, 750))
    map_bg = map_bg.filter(ImageFilter.GaussianBlur(6))
    map_bg = map_bg.crop((0, 125, map_bg.width, map_bg.height - 125))

    ss_mult = 3 # Supersampling multiplier

    # Draw Rectangles
    rect1 = DrawRectangle((1138, 446), outline="black", width=10, radius=60) # Black Rectangle
    rect2 = DrawRectangle((1128, 436), outline=color, fill=fcolor, width=5, radius=57) # Map Color Rectangle
    rect3 = DrawRectangle((360, 400), outline=color, fill=fcolor2, width=3, radius=50) # Leaderboard Rectangle
    rect4 = DrawRectangle((360, 400), outline=color, fill=fcolor2, width=3, radius=50) # Map Info Rectangle
    rect5 = DrawRectangle((308, 170), outline="black", width=6, radius=0) # Center Inner-Border Rectangle
    rect6 = DrawRectangle((312, 174), outline=color, width=4, radius=0) # Center Outer-Border Rectangle

    # Adjust Center Image
    map_img.resize((328, 205))
    crop_width = (map_img.width - rect5.width) / 2
    crop_height = (map_img.height - rect5.height) / 2
    map_img = map_img.crop((crop_width, crop_height, map_img.width-crop_width, map_img.height-crop_height))

    center_x = map_bg.width/2
    center_y = map_bg.height/2

    # Draw Text
    map_text = Image.new("RGBA", (1200, 500), (0, 0, 0, 0))
    map_text_draw = ImageDraw.Draw(map_text)

    # Make Star String
    difficulty = map_data["difficulty"]
    i = 0
    stars = ""
    while i < 5:
        if i < difficulty:
            stars += "★"
        else:
            stars += "☆"
        i += 1

    points = str(map_data["points"])
    # Middle Info
    DrawText(map_text_draw, text=map_data["name"], size=50, pos=(center_x, 35), font=montserrat_bold, max_length=340, dynamic=True, center=True)
    DrawText(map_text_draw, text=map_data["mapper"], size=35, pos=(center_x, 105), font=montserrat_regular, max_length=340, dynamic=True, center=True)
    DrawText(map_text_draw, text=map_data["type"], size=40, pos=(center_x, 340), font=montserrat_bold, max_length=340, dynamic=True, center=True)
    DrawText(map_text_draw, text=f"({points} points)", size=30, pos=(center_x, 420), font=montserrat_regular, center=True)
    DrawText(map_text_draw, text=stars, size=30, pos=(center_x, 390), font=dejavu_sans, center=True)

    # Initialize values
    x = 75
    y = 100
    i = 0

    # Change leaderboard if its a Solo map:
    if map_data["team_ranks"] == []: isteam = False
    else: isteam = True
    y_jump = 25 if isteam else 30
    threshold = 5 if isteam else 10

    # TOP 5 / 10
    DrawText(map_text_draw, text=f"Top {threshold}", size=35, pos=(191 if isteam else 181, 56), font=montserrat_bold)

    # Get Max length of all top times
    time_length = MaxLength(map_data["ranks"], threshold, montserrat_bold, 25)

    for rank in map_data["ranks"]:
        # Limit to 5 ranks, 10 if solo
        if i >= threshold:
            break

        # Grab Data
        placement = rank["rank"]
        player = rank["player"]
        time = ParseTime(rank["time"])

        # Choose Font
        font = montserrat_regular
        for s in player:
            if s not in string.printable: font = dejavu_sans; break # Dejavu-Sans supports special unicode characters

        # Get Length
        placement_length = map_text_draw.textlength("#0 " if isteam else "#00 ", ImageFont.truetype(montserrat_regular, 25))
        threshold_length = rect3.width - placement_length - time_length - 25 # Cutoff for Player 1


        # Write
        DrawText(map_text_draw, text=f"#{placement}", pos=(x, y))
        x += placement_length
        DrawText(map_text_draw, text=time, pos=(x, y), fill=color, font=montserrat_bold)
        x += time_length
        DrawText(map_text_draw, text=player, pos=(x, y), max_length=threshold_length, dynamic=True)

        x = 75
        y += y_jump
        i += 1

    # TOP 5 TEAM
    if isteam: # If there are team ranks
        DrawText(map_text_draw, text="Top 5 Team", size=35, pos=(143, 56+rect3.height/2), font=montserrat_bold)
        # Initialize values
        x = 75
        y = 103 + rect3.height/2
        i = 0
        size = 20

        # Get Max length of all top times
        time_length = MaxLength(map_data["team_ranks"], threshold, montserrat_bold, size)

        for rank in map_data["team_ranks"]:
            # Limit to 5 ranks
            if i >= threshold:
                break

            # Grab Data
            placement = rank["rank"]
            player1 = rank["players"][0]
            player2 = rank["players"][1]
            players = f"{player1} | {player2}"
            time = ParseTime(rank["time"])

            # Get Length
            placement_length = map_text_draw.textlength(f"#0 ", ImageFont.truetype(montserrat_regular, 25))
            threshold_length = rect3.width - placement_length - time_length - 25

            # Write
            DrawText(map_text_draw, text=f"#{placement}", pos=(x, y-3), size=25)
            x += placement_length
            DrawText(map_text_draw, text=time, pos=(x, y), fill=color, font=montserrat_bold, size=size)
            x += time_length
            DrawText(map_text_draw, text=players, pos=(x, y), max_length=threshold_length, dynamic=True, size=size)

            x = 75
            y += y_jump
            i += 1

    # Map Info
    if "release" in map_data:
        timestamp = map_data["release"]
        months = {
            1 : "Jan",
            2 : "Feb",
            3 : "Mar",
            4 : "Apr",
            5 : "May",
            6 : "Jun",
            7 : "Jul",
            8 : "Aug",
            9 : "Sep",
            10 : "Oct",
            11 : "Nov",
            12 : "Dec"
        }
        time = datetime.datetime.fromtimestamp(timestamp)
        year = time.year
        month = months[time.month]
        day = time.day
        timedate = f"{month} {day} {year}"
    else:
        timedate = "Unknown"
    x = 795
    y = 75
    size=29
    DrawText(map_text_draw, "Released", size=size, pos=(x, y))
    length = map_text_draw.textlength("Released ", font=ImageFont.truetype(montserrat_regular, size))
    DrawText(map_text_draw, timedate, size=size, pos=(x+length, y), font=montserrat_bold, fill=color)

    # Map Length
    width = map_data["width"]
    height = map_data["height"]
    total_size = width * height

    size_thresholds = { # Very, Very Rough estimates
        1000000 : "VERY LONG", # ~2h+ (Springlobe 3, for example (4-6h))
        750000 : "LONG",  # ~ 1-2h
        250000 : "MEDIUM", # ~ 30-45m
        50000 : "SHORT", # ~ 10-20m
        0 : "VERY SHORT" # ~ 0-10m
    }
    map_length = next(s for t, s in size_thresholds.items() if total_size > t)


    # Median Time
    sec = map_data["median_time"]
    time = str(datetime.timedelta(seconds = sec))
    if sec < 3600: time = time[2:]
    if sec < 60: time = time[1:]
    if '.' in time: time = time[:len(time)-7]
    map_median = str(time)

    # Finish Stats
    map_finishes = map_data["finishes"]
    map_finishers = map_data["finishers"]
    map_replayrate = map_finishes / map_finishers
    map_bigteam = map_data["biggest_team"]
    stats = [ # Combine into loop to iterate over when drawing text
        [map_length, "Length"],
        [str(map_finishes), "Finishes"],
        [str(map_finishers), "Finishers"],
        [f"{str(map_replayrate)[0:3]}x", "Replay Rate"],
        [map_median, "Median"],
        [width, "Width"],
        [height, "Height"],
        [f"{map_bigteam}P", "Biggest Team"]]

    y_jump = 38
    y += y_jump
    for stat in stats:
        length = map_text_draw.textlength(f"{stat[0]} ", font=ImageFont.truetype(montserrat_bold, size))
        DrawText(map_text_draw, text=str(stat[0]), size=size, pos=(x, y), fill=color, font=montserrat_bold)
        DrawText(map_text_draw, text=str(stat[1]), size=size, pos=(x+length, y))
        y += y_jump
    # Draw Lines
    line1 = DrawLine(((center_x-100, 100), (center_x+100, 100)), width=3, supersampling=False)
    line2 = DrawLine(((center_x-100, 390), (center_x+100, 390)), width=3, supersampling=False)
    line3 = DrawLine(((85, 250), (400, 250)), width=3, supersampling=False)

    # Layer All Images
    map_bg.paste(rect1, center((map_bg.width, map_bg.height), (rect1.width, rect1.height)), rect1)
    map_bg.paste(rect2, center((map_bg.width, map_bg.height), (rect2.width, rect2.height)), rect2)
    map_bg.paste(rect3, center((map_bg.width, map_bg.height), (rect3.width, rect3.height), off_x=-abs(rect3.width - 5)), rect3)
    map_bg.paste(rect4, center((map_bg.width, map_bg.height), (rect4.width, rect4.height), off_x=rect4.width - 4), rect4)
    map_bg.paste(map_img, center((map_bg.width, map_bg.height), (map_img.width, map_img.height)))
    map_bg.paste(rect5, center((map_bg.width, map_bg.height), (rect5.width, rect5.height)), rect5)
    map_bg.paste(rect6, center((map_bg.width, map_bg.height), (rect6.width, rect6.height)), rect6)
    map_bg.paste(line1, (0, 0), line1)
    map_bg.paste(line2, (0, 0), line2)
    if isteam: map_bg.paste(line3, (0, 0), line3) # Only show line if there are team ranks
    map_bg.paste(map_text, (0, 0), map_text)

    with BytesIO() as img_binary: # This is to be able to send the image as a message without having to save it locally
        map_bg.save(img_binary, 'PNG')
        img_binary.seek(0)
        file = discord.File(fp=img_binary, filename="image.png")

    return(file)


class MapInfo(commands.Cog): # Cog initiation
    def __init__(self, client):
        self.client = client
    
    @client.tree.command(name="map", description="Generate a Map stats image")
    @tree.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    @tree.choices(
        sort=[
            Choice(name="None", value="None"),
            Choice(name="Most finished", value="Most Finished"),
            Choice(name="Random", value="Random")],

        type=[
            Choice(name="Search", value="Search"),
            Choice(name="Unfinished", value="Unfinished"),
            Choice(name="Random", value="Random")],
        
        category=[
            Choice(name="All", value="All"),
            Choice(name="Novice", value="Novice"),
            Choice(name="Moderate", value="Moderate"),
            Choice(name="Brutal", value="Brutal"),
            Choice(name="Insane", value="Insane"),
            Choice(name="Dummy", value="Dummy"),
            Choice(name="Oldschool", value="Oldschool"),
            Choice(name="Solo", value="Solo"),
            Choice(name="Race", value="Race"),
            Choice(name="DDmaX.Easy", value="DDmaX.Easy"),
            Choice(name="DDmaX.Next", value="DDmaX.Next"),
            Choice(name="DDmaX.Pro", value="DDmaX.Pro"),
            Choice(name="DDmaX.Nut", value="DDmaX.Nut"),
            Choice(name="Fun", value="Fun")])

    async def map(self, interaction: discord.Interaction, map: str="", player: str="", category: Choice[str]="",  type: Choice[str]="", sort: Choice[str]=""):
        await interaction.response.defer()
        
        random = False
        unfinished = False
        sort_most = False
        set_category = "All"
        if map == "": map = None
        if player == "": player = None
        
        if hasattr(type, "value"):
            if type.value == "Random": random = True
            elif type.value == "Unfinished": unfinished = True

        if hasattr(sort, "value"):
            if sort.value == "Most Finished": sort_most = True
        
        if hasattr(category, "value"):
            set_category = category.value

        if map is None and not random and not unfinished:
            raise Exception("[Map] or [Random] parameters need a value")
        
        if player is None and unfinished:
            raise Exception("[Player] Needs a value if picking unfinished map.")
        
        map_data = await GetData(player, map, random, set_category, unfinished, sort_most)
        img = await Scrape(img_url = map_data["thumbnail"])
        drawmap_params = functools.partial(DrawMap, map_data, img)
        async with client:
            file = await client.loop.run_in_executor(None, drawmap_params) # Generate the map Image, run in executor to prevent PIL from blocking
        
        
        await interaction.followup.send(file=file, ephemeral=False)
    
    @map.error # Error Handling
    async def on_map_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"```arm\nERROR: \"{error}\"\n```", ephemeral=True) # Errors before Interaction response
        else:
            if "Command 'map' raised an exception: Exception:" in str(error):
                error = str(error).replace("Command 'map' raised an exception: Exception:", "")[1:]
            await interaction.followup.send(f"```arm\nERROR: \"{error}\"\n```", ephemeral=True) # Errors after Interaction response
        


async def setup(client): # Adding the class as a cog
    await client.add_cog(MapInfo(client))
