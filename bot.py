import os
import discord

def env_defined(key):
    return key in os.environ and len(os.environ[key]) > 0

try:
    DISCORD_SERVER = os.environ["DISCORD_SERVER"]
    DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
    BOT_NAME = os.environ["BOT_NAME"]
except:
    print("Your .env is missing tokens and i'm too lazy yet to say which")
    exit()

if env_defined("DISCORD_CHANNEL"):
    DISCORD_CHANNEL = os.environ["DISCORD_CHANNEL"]

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == BOT_NAME:
        return
    if message.content == '!setup':
        channel = str(message.channel.id)
        if (DISCORD_CHANNEL == channel):
            await message.channel.send("Already set to this channel")
        else:
            os.system("export DISCORD_CHANNEL="+channel)
            await message.channel.send("DISCORD_CHANNEL set to "+channel+"\nMake sure to add this ID to your .env if you haven't already.")

client.run(DISCORD_TOKEN)
