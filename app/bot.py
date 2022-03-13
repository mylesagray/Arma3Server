import os
import discord
import update
import json

def env_defined(key):
    return key in os.environ and len(os.environ[key]) > 0


DISCORD_CHANNEL = []

# env variables are defaults, if no config exists it'll be created
try:
    DISCORD_SERVER = os.environ["DISCORD_SERVER"]
    DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
except:
    print("Missing config values")
    exit()

DISCORD_CONFIG = "/arma3/configs/discord.cfg"

def load_settings():
    try:
        f = open(DISCORD_CONFIG,'r')
        settings = json.load(f)
        f.close()
    except:
        return 0
    return settings


settings = load_settings()
if not settings:
    try:
        settings = {"DISCORD_SERVER":DISCORD_SERVER,"DISCORD_TOKEN":DISCORD_TOKEN}
        with open(DISCORD_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except:
        print(DISCORD_CONFIG+" not accessible")

if (settings["DISCORD_SERVER"]):
    DISCORD_SERVER = settings["DISCORD_SERVER"]
if (settings["DISCORD_TOKEN"]):
    DISCORD_TOKEN = settings["DISCORD_TOKEN"]


client = discord.Client()

@client.event
async def on_message(message):
    if message.author == "kharms#1207": #this is a bit dumb, but # in config files gets interpreted as comment
        return
    if message.content == '!settings add channel':
        channel = str(message.channel.id)
        if (channel in DISCORD_CHANNEL):
            await message.channel.send("Already set to this channel")
        else:
            # TODO Add channel to discord.cfg
            DISCORD_CHANNEL.append(str(channel))
            os.system("export DISCORD_CHANNEL=\""+str(DISCORD_CHANNEL)+"\"")
            await message.channel.send("Added "+channel+" to DISCORD_CHANNEL.\nMake sure to add this ID to your .env if you haven't already.")
    
    if message.content == '!get version':
        await message.channel.send(update.get_version())
    if message.content == '!get install_state':
        await message.channel.send(update.get_install_state())
    if message.content == '!get settings':
        await message.channel.send(load_settings())
client.run(DISCORD_TOKEN)
