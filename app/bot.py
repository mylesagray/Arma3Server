from email import message
import os
import discord
import update
import json
import datetime
from discord.ext import commands

def env_defined(key):
    return key in os.environ and len(os.environ[key]) > 0


DISCORD_CHANNEL = []
# env variables are defaults, if no config file exists it'll be created.
# If no env is set, stop the bot
try:
    DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
except:
    print("Missing token")
    exit()


DISCORD_CONFIG = "/arma3/configs/discord.cfg"

# tries to load an existing DISCORD_CONFIG, creates one on initial startup. 
# Fails if the path isn't writeable
def load_settings():
    try:
        f = open(DISCORD_CONFIG,'r')
        settings = json.load(f)
        f.close()
    except:
        try:
            settings = {"DISCORD_TOKEN":DISCORD_TOKEN}
            with open(DISCORD_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except:
            print(DISCORD_CONFIG+" not accessible")
            exit()
    return settings

settings = load_settings()

if (settings["DISCORD_TOKEN"]):
    DISCORD_TOKEN = settings["DISCORD_TOKEN"]

# straight forward, saves the settings json to DISCORD_CONFIG
def save_settings(jsonString):
    try:
        with open(DISCORD_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(jsonString, f, ensure_ascii=False, indent=4)
    except:
        return 0
    return 1

desc = '''Arma3 server status bot:
!setup - Adds a message to this channel that will be updated by !update //TODO: implement cron feature
!delete - Removes the message created by !setup
!status - Sends a self deleting status message with all available server info
!update - Updates the pinned message from !setup
!mods - Sends a self deleting message with the currently used mod-list as html file
!ping - Alive check'''

bot = commands.Bot(command_prefix='!', description=desc)

# mostly for debugging purposes
@bot.command(name="get")
async def _get(ctx, arg):
    response = desc
    if (arg == "version"):
        response = update.get_version()
    if (arg == "status"):
        response = update.get_install_state()
    await ctx.send(response)

# Adds a message to the channel that it was executed in, pins it and stores the id for !update
@bot.command(name="setup")
async def _setup(ctx, *arg):
    response = ""
    # if no server has been set up, create the root element and add this server to it
    # discord calls servers guilds
    server = str(ctx.guild)
    channel = ctx.channel.id
    # check if the server is already known, check if the channel is, if not add one or both
    if "DISCORD_SERVER" not in settings:
        settings["DISCORD_SERVER"] = {}
    if server not in settings["DISCORD_SERVER"]:
        settings["DISCORD_SERVER"][server] = {"name":server, "channels":[channel], "msgids":[]}
        response = "Channel added"
    else:
        if channel not in settings["DISCORD_SERVER"][server]["channels"]:
            settings["DISCORD_SERVER"][server]["channels"].append(channel)
            response = "Channel added"
        else:
            response = "Channel already monitored"
            await ctx.send(response, delete_after=15)
            return
    # Gather message id for editing purposes
    res = await ctx.send(response)
    if res.id not in settings["DISCORD_SERVER"][server]["msgids"]:
        settings["DISCORD_SERVER"][server]["msgids"].append(res.id)
        ctx.channel.pin(res)
    res = save_settings(settings)
    if not res:
        response = "Saving the settings failed, call an adult"
        ctx.send(response)
    if res:
        _update()

# Removes the channel this was called in from the list of channels to !update
@bot.command(name="delete")
async def _delete(ctx, *arg):
    response = "Channel not monitored"
    server = str(ctx.guild)
    channel = ctx.channel.id
    if server in settings["DISCORD_SERVER"]:
        if channel in settings["DISCORD_SERVER"][server]["channels"]:
            try:
                idx = settings["DISCORD_SERVER"][server]["channels"].index(channel)
                settings["DISCORD_SERVER"][server]["channels"].remove(channel)
                msg = await bot.get_channel(channel).fetch_message(settings["DISCORD_SERVER"][server]["msgids"][idx])
                del(settings["DISCORD_SERVER"][server]["msgids"][idx])
                response = "Channel removed"
                await msg.delete()
            except Exception as e:
                print(e)
    res = save_settings(settings)
    if not res:
        response = "Saving the settings failed, call an adult"
    await ctx.send(response)

# updates the pinned messages created via !setup
@bot.command(name="update")
async def _update(ctx, *args):
    response = ""
    # No servers configured = no need to process further
    if "DISCORD_SERVER" not in settings:
        return
    await ctx.message.delete()
    cnt = 0
    embed = messageConstructor()
    for server in settings["DISCORD_SERVER"]:
        cnt = 0
        for channel in settings["DISCORD_SERVER"][server]["channels"]:
            chan = bot.get_channel(channel)
            message = await chan.fetch_message(settings["DISCORD_SERVER"][server]["msgids"][cnt])
            await message.edit(content="",embed=embed)
            cnt += 1

# Sends a self deleting status message with all available server info
@bot.command(name="status")
async def _status(ctx, *args):
    await ctx.message.delete()
    embed = messageConstructor()
    await ctx.send(content="(delete in 60sec)", embed=embed, delete_after=60)
    
# Alive check
@bot.command(name="ping")
async def _ping(ctx, *args):
    await ctx.send("pong 🏓")

# Sends a self deleting message with the currently used mod-list as html file
@bot.command(name="mods")
async def _mods(ctx, *args):
    await ctx.message.delete()
    if os.environ["MODS_PRESET"] != "":
        try:
            modfile = open(os.environ["MODS_PRESET"],"rb")
            fileupload = discord.File(fp=modfile,filename="mod-list.html")
            modfile.close()
            await ctx.send(content="(delete in 60sec)", file=fileupload, delete_after=60)
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong reading the file, call an adult")
    else:
        await ctx.send("No mod file defined, maybe you're running non-workshop mods?")

# Constructs an embed for !update and !status
def messageConstructor():
    status = update.get_install_state()
    version = update.get_version()
    server_name, server_password = update.get_server_details()
    embed = discord.Embed(type="rich",colour=discord.Colour.blurple())
    embed.title = "ArmA Server Status"
    embed.description = "The currently active ArmA server details are below"
    embed.set_thumbnail(url="https://arma3.com/assets/img/logos/arma3.png")
    embed.add_field(name="💻Server Name:", value=server_name)
    embed.add_field(name="🔑Password:", value=server_password)
    embed.add_field(name="📃Status:", value=status, inline=True)
    embed.add_field(name="💥Version:", value=version, inline=True)
    embed.timestamp = datetime.datetime.utcnow()
    return embed

bot.run(DISCORD_TOKEN)

