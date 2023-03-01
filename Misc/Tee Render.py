# Image imports
from PIL import Image, ImageOps
from io import BytesIO
import math
import functools

# Discord Imports
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())
tree = app_commands

def Render(asset, eye_type, deg, iscenter, color, body_hsl, foot_hsl): # Render the tee from asset image

    asset_bytes = BytesIO(asset) # Turn bytes object into BytesIO object
    asset_bytes.seek(0)
    asset = Image.open(asset_bytes) # Open it from byte form into PIL image

    im_w, im_h = asset.size
    m = im_w / 512 # Multiplies based on image size, 512x256 being base value

    if im_w != im_h*2: # Only accept 2:1 ratios
        raise Exception("Image Dimensions Aren't 2:1")
    
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
        [pos * m for pos in [384, 192, 448, 256]], # Dead Eyes
        [pos * m for pos in [448, 192, 512, 256]] # Surprised Eyes
    ]

    # Seperate Every Asset
    body = asset.crop(box=positions[0])
    body_shadow = asset.crop(box=positions[1])
    hand = asset.crop(box=positions[2])
    hand_shadow = asset.crop(box=positions[3])
    feet = asset.crop(box=positions[4])
    feet_shadow = asset.crop(box=positions[5])
    eye = asset.crop(box=positions[eye_type + 6])

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
            if 0 <= rgb_h < 1: r, g, b = c, x, 0
            if 1 <= rgb_h < 2: r, g, b = x, c, 0
            if 2 <= rgb_h < 3: r, g, b = 0, c, x
            if 3 <= rgb_h < 4: r, g, b = 0, x, c
            if 4 <= rgb_h < 5: r, g, b = x, 0, c
            if 5 <= rgb_h < 7: r, g, b = c, 0, x

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
    def MoveAngle(xy, sep, deg, off_x=0, off_y=0, subtract_x=False, subtract_y=False, iscenter=False):
        x, y = xy
        x /= 1.20
        y /= 1.20
        if not iscenter:
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
    skin = eye = Position(skin, eye, MoveAngle(xy=center(tr_width, tr_height, eye_width, eye_height, off_x=2, subtract_x=True), sep=16, deg=deg, iscenter=iscenter))
    skin = eyem = Position(skin, eyem, MoveAngle(xy=center(tr_width, tr_height, eye_width, eye_height, off_x=2, subtract_x=True), sep=16, deg=deg, off_x=eye_sep, iscenter=iscenter))
    skin = feet2 = Position(skin, feet2, center(tr_width, tr_height, body_width, body_height, off_x=13, off_y=60))

    with BytesIO() as img_binary: # This is to be able to send the image as a message without having to save it locally
        skin.save(img_binary, 'PNG')
        img_binary.seek(0)
        file = discord.File(fp=img_binary, filename="image.png")

    return(file) # Return to discord command with image

class TeeRender(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @client.tree.command(name="render", description="Render a Tee from an image")
    @tree.choices( # Set up the options
        eyes=[
            Choice(name="Normal", value=0),
            Choice(name="Angry", value=1),
            Choice(name="Freeze", value=2),
            Choice(name="Happy", value=3),
            Choice(name="Dead", value=4),
            Choice(name="Surprised", value=5)
        ],

        color=[
            Choice(name="True", value="True"),
            Choice(name="False", value="False")
        ],
        
        center=[
            Choice(name="True", value="True"),
            Choice(name="False", value="False")
        ])
    async def tee(self, interaction: discord.Interaction, image: discord.Attachment, eyes: Choice[int]=0, deg: int=90, center: Choice[str]="", color: Choice[str]="", body_hsl: str="0, 0, 0", feet_hsl: str="0, 0, 0"):
        await interaction.response.defer() # Give time for image to generate
        asset = await image.read()
        iscenter = False
        iscolor = False
        if "," not in body_hsl or "," not in feet_hsl:
            raise Exception("HSL Values must be seperated with ,")
        else:
            body_hsl = body_hsl.replace(" ", "") # Strip Spaces
            feet_hsl = feet_hsl.replace(" ", "")
            body_hsl = body_hsl.split(",") # Seperate numbers
            feet_hsl = feet_hsl.split(",")
            body_hsl = int(body_hsl[0]), int(body_hsl[1]), int(body_hsl[2]) # Turn string into int, pack into tuple
            feet_hsl = int(feet_hsl[0]), int(feet_hsl[1]), int(feet_hsl[2])

        if hasattr(center, "value"):
            if center.value == "True":
                iscenter = True
        
        if hasattr(color, "value"):
            if color.value == "True":
                iscolor = True

        if hasattr(eyes, "value"):
            eyes = eyes.value
        
        if not iscenter: # Check if degrees are valid
            if deg < 0 or deg > 360:
                raise Exception("Invalid Number for degrees, Valid Number: 0-360")
        
        if iscolor: # Check if colors are valid
            for part_color in body_hsl:
                if part_color > 255 or part_color < 0:
                    raise Exception("Invalid Number for Body Color, Valid Number: 0-255")

            for part_color in feet_hsl:
                if part_color > 255 or part_color < 0:
                    raise Exception("Invalid Number for Feet Color, Valid Number: 0-255")

        else:
            body_hsl = 0, 0, 0
            feet_hsl = 0, 0, 0

        render_param = functools.partial(Render, asset, eyes, deg, iscenter, iscolor, body_hsl, feet_hsl) # Pack all parameters into a single variable
        async with client:
            file = await client.loop.run_in_executor(None, render_param) # Render Tee (Run in executor to prevent PIL blocking the event loop)

        em = discord.Embed(
            title=f"Tee Render",
            description="Please report any issues with the image")

        em.set_image(url="attachment://image.png")
        await interaction.followup.send(file=file, embed=em)
    
    @tee.error # Error Handling
    async def on_tee_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
            # TODO: Fix so ephemeral actually works
            if "Command 'render' raised an exception: Exception:" in str(error):
                error = str(error).replace("Command 'render' raised an exception: Exception:", "")[1:]
            await interaction.followup.send(f"```arm\nERROR: \"{error}\"\n```", ephemeral=True) # Errors after Interaction response

async def setup(client): # Adding the class as a cog
    await client.add_cog(TeeRender(client))