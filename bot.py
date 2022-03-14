from email import message
import os
import discord
import update
import json
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
!setup - add this channel to update notification list
!delete - removes this channel from update notification list'''

bot = commands.Bot(command_prefix='!', description=desc)

@bot.command(name="get")
async def _get(ctx, arg):
    response = desc
    if (arg == "version"):
        response = update.get_version()
    if (arg == "status"):
        response = update.get_install_state()
    await ctx.send(response)

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
        response = "Channel added, pin this message"
    else:
        if channel not in settings["DISCORD_SERVER"][server]["channels"]:
            settings["DISCORD_SERVER"][server]["channels"].append(channel)
            response = "Channel added, pin this message"
        else:
            response = "Channel already monitored"
            await ctx.send(response)
            return
    # Gather message id for editing purposes
    res = await ctx.send(response)
    if res.id not in settings["DISCORD_SERVER"][server]["msgids"]:
        settings["DISCORD_SERVER"][server]["msgids"].append(res.id)
    res = save_settings(settings)
    if not res:
        response = "Saving the settings failed, call an adult"
        ctx.send(response)


@bot.command(name="delete")
async def _delete(ctx, *arg):
    response = "Channel not monitored"
    server = str(ctx.guild)
    channel = ctx.channel.id
    if server in settings["DISCORD_SERVER"]:
        for chan in settings["DISCORD_SERVER"][server]["channels"]:
            try:
                idx = settings["DISCORD_SERVER"][server]["channels"].index(channel)
                settings["DISCORD_SERVER"][server]["channels"].remove(channel)
                msg = channel.fetch_message(settings["DISCORD_SERVER"][server]["msgids"][idx])
                await msg.delete()
                del settings["DISCORD_SERVER"][server]["msgids"][idx]
                response = "Channel removed"
            except:
                pass
    res = save_settings(settings)
    if not res:
        response = "Saving the settings failed, call an adult"
    await ctx.send(response)


@bot.command(name="update")
async def _update(ctx, *args):
    response = ""
    # No servers configured = no need to process further
    if "DISCORD_SERVER" not in settings:
        return
    cnt = 0
    status = update.get_install_state()
    version = update.get_version()
    embed = discord.Embed(type="rich")
    embed.add_field(name="Server status", value=status, inline=True)
    embed.add_field(name="Server version", value=version, inline=True)
    for server in settings["DISCORD_SERVER"]:
        for channel in settings["DISCORD_SERVER"][server]["channels"]:
            chan = bot.get_channel(channel)
            message = await chan.fetch_message(settings["DISCORD_SERVER"][server]["msgids"][cnt])
            await message.edit(content="Arma3server status",embed=embed)
            cnt += 1

bot.run(DISCORD_TOKEN)