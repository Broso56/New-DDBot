# Image imports
from PIL import Image, ImageOps
from io import BytesIO
import math
import random
import os

# Discord Imports
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from discord.app_commands import Choice

global bot_dir
bot_dir = "C:/Users/broso/Desktop/Coding/Python Projects/New DDBot"
intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())
tree = app_commands

def Render(): # Render the tee from asset image

    # Random values
    deg = random.choice(range(0, 360)) # Random Eye Angle
    eye_type = random.choice(["Normal", "Angry", "Freeze", "Happy", "Surprised"]) # Random Eyes, excluded "Dead" eyes because most skins dont have them
    eye_types = {
        "Normal" : 0,
        "Angry" : 1,
        "Freeze" : 2,
        "Happy" : 3,
        "Surprised" : 4
}

    color = random.choice([True, False])
    if color:
        body_hsl = [random.choice(range(0, 255)), random.choice(range(0, 255)), random.choice(range(0, 255))] # Random H, S, L values
        foot_hsl = [random.choice(range(0, 255)), random.choice(range(0, 255)), random.choice(range(0, 255))] # Random H, S, L values
    else:
        body_hsl = [0, 0, 0]
        foot_hsl = [0, 0, 0]

    
    img_random = random.choice(os.listdir(f"{bot_dir}/Images/Tee Skins")) # Random Skin
    asset = Image.open(f"{bot_dir}/Images/Tee Skins/{img_random}") # Open Random Skin

    im_w, _ = asset.size
    m = im_w / 512 # Multiplies based on image size, 512x256 being base value

    # Positions for each asset
    positions = [
        [pos * m for pos in [0, 0, 192, 192]], # Body
        [pos * m for pos in [192, 0, 384, 192]], # Body Shadow
        [pos * m for pos in [384, 0, 448, 64]], # Hand
        [pos * m for pos in [448, 0, 512, 64]], # Hand Shadow
        [pos * m for pos in [384, 64, 512, 128]], # Feet
        [pos * m for pos in [384, 128, 512, 192]], # Feet Shadow

        [pos * m for pos in [128, 192, 192, 256]], # Normal Eyes
        [pos * m for pos in [192, 192, 256, 256]], # Angry Eyes
        [pos * m for pos in [256, 192, 320, 256]], # Freeze Eyes
        [pos * m for pos in [320, 192, 384, 256]], # Happy Eyes
        [pos * m for pos in [448, 192, 512, 256]] # Surprised Eyes
    ]

    # Seperate Every Asset
    body = asset.crop(box=positions[0])
    body_shadow = asset.crop(box=positions[1])
    hand = asset.crop(box=positions[2])
    hand_shadow = asset.crop(box=positions[3])
    feet = asset.crop(box=positions[4])
    feet_shadow = asset.crop(box=positions[5])
    eye = asset.crop(box=positions[eye_types[eye_type] + 6])

    # Downscale Body & Eyes
    body_width, body_height = body.size
    body_width = int(body_width * 0.66)
    body_height = int(body_height * 0.66)

    body = body.resize((body_width, body_height))
    body_shadow = body_shadow.resize((body_width, body_height))

    eye_width, eye_height = eye.size
    eye_width = int(eye_width * 0.8)
    eye_height = int(eye_height * 0.8)

    eye = eye.resize((eye_width, eye_height))

    # Coloring Function
    def Color(parts, body_hsl, foot_hsl):
        
        body, body_shadow, hand, hand_shadow, feet, feet_shadow, eye = parts
        # Convert In-Game colors to HSL
        def TeeToHSL(tee_hsl):
            tee_h, tee_s, tee_l = tee_hsl
            h = tee_h / 255
            s = tee_s / 255
            l = (0.5 + (0.5 * (tee_l / 255)))
            return(h, s, l)
        
        # Based off of the HSL to RGB Formula at:
        # https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB
        def HSLtoRGB(hsl):
            h, s, l = hsl

            rgb_h = h * 6
            c = (1 - abs(2 * l - 1)) * s
            x = c * (1 - abs(rgb_h % 2 - 1))

            # R, G, B = Any order of C, X, 0
            if 0 <= rgb_h and rgb_h < 1: r, g, b = c, x, 0
            if 1 <= rgb_h and rgb_h < 2: r, g, b = x, c, 0
            if 2 <= rgb_h and rgb_h < 3: r, g, b = 0, c, x
            if 3 <= rgb_h and rgb_h < 4: r, g, b = 0, x, c
            if 4 <= rgb_h and rgb_h < 5: r, g, b = x, 0, c
            if 5 <= rgb_h and rgb_h < 7: r, g, b = c, 0, x

            rgb_m = (l - c / 2)
            r, g, b = r + rgb_m, g + rgb_m, b + rgb_m

            return(r, g, b)
        
        body_rgb = HSLtoRGB(TeeToHSL(body_hsl)) # Convert In-Game to HSL, then to RGB
        foot_rgb = HSLtoRGB(TeeToHSL(foot_hsl)) # Convert In-Game to HSL, then to RGB

        def ColorPart(part, rgb, grayscale=False):
            r, g, b = rgb

            # pixels[i] = Red | pixels[i + 1] = Green | pixels[i + 2] = Blue | pixels[i + 3] = Alpha | Every 4 iterations = 1 pixel
            part_data = list(part.getdata()) # Merge all lists/tuples into one list (PIL has tuples for every pixel with RGBA values, rather than just all in a single list)
            pixels = []
            i = 0
            for i in part_data:
                for x in i:
                    pixels.append(x)

            i = 0
            while i < len(pixels): # Grayscale the image
                gray = int((pixels[i] + pixels[i+1] + pixels[i+2]) / 3)
                pixels[i] = gray
                pixels[i+1] = gray
                pixels[i+2] = gray
                i += 4

            if grayscale:
                f = []; i = 1
                while i <= 256: f.append(0); i+=1

                OrgWeight = 0
                NewWeight = 192

                # Find Most Common Frequence
                i = 0
                while i < len(pixels):
                    if pixels[i+3] > 128:
                        f[pixels[i]] += 1
                    i+=4

                i = 1
                while i < 256:
                    if f[OrgWeight] < f[i]:
                        OrgWeight = i
                    i += 1

                # Reorder
                InvOrgWeight = 255 - OrgWeight
                InvNewWeight = 255 - NewWeight

                i = 0
                while i < len(pixels):
                    v = pixels[i]

                    if v <= OrgWeight and OrgWeight == 0:
                        v = 0

                    elif v <= OrgWeight:
                        v = v / OrgWeight * NewWeight

                    elif InvOrgWeight == 0:
                        v = NewWeight

                    else:
                        v = ((v - OrgWeight) / InvOrgWeight) * InvNewWeight + NewWeight

                    pixels[i] = v
                    pixels[i+1] = v
                    pixels[i+2] = v
                    i += 4

            i = 0
            while i < len(pixels): # Set Colors
                pixels[i] = int(pixels[i] * r)
                pixels[i+1] = int(pixels[i+1] * g)
                pixels[i+2] = int(pixels[i+2] * b)
                i += 4

            new_part_data = []
            i = 0
            while i < len(pixels):
                new_part_data.append((pixels[i], pixels[i+1], pixels[i+2], pixels[i+3])) # Split up values back into multiple lists (PIL requires RGBA values to be bundled into lists for each pixel)
                i += 4
            part = part.putdata(new_part_data) # Apply Colors
            return(part)

        # Color Every Part
        ColorPart(body, body_rgb, grayscale=True)
        ColorPart(body_shadow, body_rgb)
        ColorPart(hand, body_rgb)
        ColorPart(hand_shadow, body_rgb)
        ColorPart(feet, foot_rgb)
        ColorPart(feet_shadow, foot_rgb)
        ColorPart(eye, body_rgb)
        return

    # Color the skin if requested
    if color:
        Color((body, body_shadow, hand, hand_shadow, feet, feet_shadow, eye), body_hsl, foot_hsl)

    # Copy & Mirror Parts
    eyem = ImageOps.mirror(eye)
    feet2 = feet.copy()
    feet_shadow2 = feet_shadow.copy()

    transparent = Image.open(r"C:\Users\broso\Downloads\transparent.png") # Open this to use as a base for alpha compositing
    tr_width, tr_height = transparent.size
    tr_width *= m
    tr_height *= m
    transparent = transparent.resize((int(tr_width), int(tr_height))) # Resize Image relative to the asset image

    crop_amount = 32 # Crop on all edges since there is a lot of empty space left (Might remove if it breaks certain skins)
    p1 = crop_amount * m
    p2 = tr_height - (crop_amount * m)
    transparent = transparent.crop(box=(p1, p1, p2, p2))

    tr_width = transparent.width
    tr_height = transparent.height

    skin = transparent.copy()

    # Position Objects
    def Position(skin, fg, xy):
        x, y = xy
        p_transparent = transparent.copy()
        p_transparent.paste(fg, (int(x * m), int(y * m)), fg)

        skin = Image.alpha_composite(skin, p_transparent)

        return(skin)

    # Center object onto another object
    def center(bg_width=0, bg_height=0, fg_width=0, fg_height=0, off_x=0, off_y=0, subtract_x=False, subtract_y=False):
        bg_width /= m
        bg_height /= m
        fg_width /= m
        fg_height /= m

        x = (bg_width - fg_width) / 2
        if not subtract_x: x += off_x
        if subtract_x: x -= off_x

        y = (bg_height - fg_height) / 2
        if not subtract_y: y += off_y
        if subtract_y: y -= off_y


        return(int(x), int(y))

    # Move object by degrees around a center
    def MoveAngle(xy, sep, deg, off_x=0, off_y=0, subtract_x=False, subtract_y=False):
        x, y = xy
        x /= 1.20
        y /= 1.20

        deg = (deg - 90) * math.pi/180
        y += abs(sep) * (math.sin(deg) / 1.25)
        x += sep * math.cos(deg)

        if not subtract_x: x += off_x
        if subtract_x: x -= off_x

        if not subtract_y: y += off_y
        if subtract_y: y -= off_y

        return(int(x), int(y))


    eye_sep = (eye_width / m) / 3.1

    skin = body_shadow = Position(skin, body_shadow, center(tr_width, tr_height, body_width, body_height))
    skin = feet_shadow = Position(skin, feet_shadow, center(tr_width, tr_height, body_width, body_height, off_x=18, off_y=60, subtract_x=True))
    skin = feet_shadow2 = Position(skin, feet_shadow2, center(tr_width, tr_height, body_width, body_height, off_x=13, off_y=60))
    skin = feet = Position(skin, feet, center(tr_width, tr_height, body_width, body_height, off_x=18, off_y=60, subtract_x=True))
    skin = body = Position(skin, body, center(tr_width, tr_height, body_width, body_height))
    skin = eye = Position(skin, eye, MoveAngle(xy=center(tr_width, tr_height, eye_width, eye_height, off_x=2, subtract_x=True), sep=16, deg=deg))
    skin = eyem = Position(skin, eyem, MoveAngle(xy=center(tr_width, tr_height, eye_width, eye_height, off_x=2, subtract_x=True), sep=16, deg=deg, off_x=eye_sep))
    skin = feet2 = Position(skin, feet2, center(tr_width, tr_height, body_width, body_height, off_x=13, off_y=60))

    with BytesIO() as img_binary: # This is to be able to send the image as a message without having to save it locally
        skin.save(img_binary, 'PNG')
        img_binary.seek(0)
        file = discord.File(fp=img_binary, filename="file.png")
    
    with BytesIO() as img2_binary:
        asset.save(img2_binary, 'PNG')
        img2_binary.seek(0)
        asset_file = discord.File(fp=img2_binary, filename="asset.png")

    return(file, asset_file, body_hsl, foot_hsl) # Return to discord command with image

class RandomRender(commands.Cog):
    def __init__(self, client):
        self.client = client

    @client.tree.command(name="random", description="Renders a random tee with random colors/eyes")
    async def tee(self, interaction: discord.Interaction):
        await interaction.response.defer() # Give time for image to generate

        async with client:
            file, asset, body_hsl, foot_hsl = await client.loop.run_in_executor(None, Render) # Render Tee (Run in executor to prevent PIL blocking the event loop)

        body_h, body_s, body_l = body_hsl
        foot_h, foot_s, foot_l = foot_hsl

        imageEmbed = discord.Embed(
            title="Tee Render",
            description="Please report any issues with the image")
        imageEmbed.set_image(url="attachment://file.png")

        infoEmbed = discord.Embed(
            title="Render Info",
            description="Info about the Tee skin")
        infoEmbed.add_field(name="\u200b", value=f"```css\n[Body]\n[H:{body_h}] \n[S:{body_s}] \n[L:{body_l}]\n```") # u200b for invisible name, css codeblock for cyan text
        infoEmbed.add_field(name="\u200b", value=f"```html\n<Feet>\n<H:{foot_h}> \n<S:{foot_s}> \n<L:{foot_l}>\n```") # u200b for invisible name, html codeblock for yellow text
        infoEmbed.set_image(url="attachment://asset.png")

        await interaction.followup.send(files=[file, asset], embeds=[imageEmbed, infoEmbed])


async def setup(client): # Adding the class as a cog
    await client.add_cog(RandomRender(client))