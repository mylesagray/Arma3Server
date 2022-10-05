import os
import subprocess
import json
import datetime

from discord.ext import commands
import update
import discord
import network


def env_defined(key):
    return key in os.environ and len(os.environ[key]) > 0


DISCORD_CHANNEL = []
# env variables are defaults, if no config file exists it'll be created.
# If no env is set, stop the bot
if not env_defined("DISCORD_TOKEN"):
    print("Missing bot token from .env")
    exit()

if env_defined("DISCORD_PREFIX"):
    DISCORD_PREFIX = os.environ["DISCORD_PREFIX"]
else:
    print("No user defined prefix given, defaulting to '!'")
    DISCORD_PREFIX = "!"

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
DISCORD_CONFIG = "/arma3/configs/discord.cfg"

# tries to load an existing DISCORD_CONFIG, creates one on initial startup.
# Fails if the path isn't writeable


def load_settings():
    try:
        f = open(DISCORD_CONFIG, 'r')
        settings = json.load(f)
        f.close()
    except Exception:
        try:
            settings = {
                "DISCORD_TOKEN": DISCORD_TOKEN
            }
            with open(DISCORD_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception:
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
    except Exception:
        return 0
    return 1


desc = f'''Arma3 server status bot:
{DISCORD_PREFIX}setup - Adds a message to this channel that will be updated by {DISCORD_PREFIX}update //TODO: implement cron feature
{DISCORD_PREFIX}delete - Removes the message created by !setup
{DISCORD_PREFIX}status - Sends a self deleting status message with all available server info
{DISCORD_PREFIX}update - Updates the pinned message from !setup
{DISCORD_PREFIX}mods - Sends a self deleting message with the currently used mod-list as html file
{DISCORD_PREFIX}ping - Alive check
{DISCORD_PREFIX}restart - CAUTION: Restarts the server!'''

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=DISCORD_PREFIX,
                   description=desc, intents=intents)


@bot.event
async def on_ready():
    print('Logged on')
    activity = discord.Activity(
        name="ArmA Noobz", type=discord.ActivityType.playing, details="URBW Antistasi - 0/16", state="In Game")
    await bot.change_presence(status=discord.Status.online, activity=activity)


@bot.command(name="restart")
async def _restart(ctx):
    embed = embed_constructor(
        title='<:warning:1024796220222345216>WARNING<:warning:1024796220222345216>',
        text="This command will restart the running arma server without any further questions.\n\
              If you're sure about that, react with <:elmo:1005177400105107507> within the next 5 seconds.")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("<:elmo:1005177400105107507>")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '<:elmo:1005177400105107507>'
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=5.0, check=check)
    except TimeoutError:
        await msg.clear_reactions()
        await ctx.send('Restart aborted')
    else:
        subprocess.call(["/usr/bin/pkill", "-SIGINT", "arma3"])
        await ctx.send('Restarting server now')

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
        settings["DISCORD_SERVER"][server] = {
            "name": server, "channels": [channel], "msgids": []}
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
        await res.pin()
    res = save_settings(settings)
    if not res:
        response = "Saving the settings failed, call an adult"
        await ctx.send(response)
    if res:
        await _update(ctx)

# Removes the channel this was called in from the list of channels to !update


@bot.command(name="delete")
async def _delete(ctx, *arg):
    response = "Channel not monitored"
    server = str(ctx.guild)
    channel = ctx.channel.id
    if server in settings["DISCORD_SERVER"]:
        if channel in settings["DISCORD_SERVER"][server]["channels"]:
            try:
                idx = settings["DISCORD_SERVER"][server]["channels"].index(
                    channel)
                settings["DISCORD_SERVER"][server]["channels"].remove(channel)
                msg = await bot.get_channel(channel).fetch_message(settings["DISCORD_SERVER"][server]["msgids"][idx])
                del (settings["DISCORD_SERVER"][server]["msgids"][idx])
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
            await message.edit(content="", embed=embed)
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
            modfile = open(os.environ["MODS_PRESET"], "rb")
            fileupload = discord.File(fp=modfile, filename="mod-list.html")
            modfile.close()
            await ctx.send(content="(delete in 60sec)", file=fileupload, delete_after=60)
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong reading the file, call an adult")
    else:
        await ctx.send("No mod file defined, maybe you're running non-workshop mods?")


# Updates the bot's presence with current server population


# Constructs an embed for !update and !status


def messageConstructor():
    status = update.get_install_state()
    version = update.get_version()
    server_name, server_password = update.get_server_details()
    server_ip = network.get_external_ip()
    current_players, max_players = network.get_players()
    embed = discord.Embed(type="rich", colour=discord.Colour.blurple())
    embed.title = "ArmA Server Status"
    embed.description = "The currently active ArmA server details are below"
    embed.set_thumbnail(url="https://arma3.com/assets/img/logos/arma3.png")
    embed.add_field(name="💻Server Name:", value=server_name)
    embed.add_field(name="🔑Password:", value=server_password)
    embed.add_field(name="📃Status:", value=status, inline=True)
    embed.add_field(name="💥Version:", value=version, inline=True)
    embed.add_field(name="☁Server IP:", value=server_ip)
    embed.add_field(name="🕹️Players:",
                    value=f'{current_players} / {max_players}')
    embed.timestamp = datetime.datetime.utcnow()
    return embed


def embed_constructor(title: str, text: str) -> discord.Embed:
    embed = discord.Embed(type="rich", colour=discord.Colour.red())
    embed.title = title
    embed.description = text
    return embed


bot.run(DISCORD_TOKEN)
