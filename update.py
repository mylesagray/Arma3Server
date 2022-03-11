import os
import re
import subprocess
import requests
from datetime import datetime, date, timedelta


WEBHOOK_JSON = """
{
  "username": "ALARMA",
  "avatar_url": "https://i.imgur.com/4M34hi2.png",
  "content": "ARMA3 Server status",
  "embeds": [
    {
    #   "author": {
    #     "name": "Birdie♫",
    #     "url": "https://www.reddit.com/r/cats/",
    #     "icon_url": "https://i.imgur.com/R66g1Pe.jpg"
    #   },
    #   "title": "Title",
    #   "url": "https://google.com/",
    #   "description": "Text message. You can use Markdown here. *Italic* **bold** __underline__ ~~strikeout~~ [hyperlink](https://google.com) `code`",
    #   "color": 15258703,
      "fields": [
        {
          "name": "Server status",
          "value": "online/offline",
          "inline": true
        },
        {
          "name": "Server version",
          "value": "Yup",
          "inline": true
        },
        # {
        #   "name": "Update scheduled if necessary",
        #   "value": "Updatetime"
        # },
    #     {
    #       "name": "Thanks!",
    #       "value": "You're welcome :wink:"
    #     }
      ],
    #   "thumbnail": {
    #     "url": "https://upload.wikimedia.org/wikipedia/commons/3/38/4-Nature-Wallpapers-2014-1_ukaavUI.jpg"
    #   },
    #   "image": {
    #     "url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/A_picture_from_China_every_day_108.jpg"
    #   },
    #   "footer": {
    #     "text": "Woah! So cool! :smirk:",
    #     "icon_url": "https://i.imgur.com/fKL31aD.jpg"
    #   }
    }
  ]
}"""


def env_defined(key):
    return key in os.environ and len(os.environ[key]) > 0


if env_defined("WEBHOOK_ID"):
    WEBHOOK_ID = os.environ["WEBHOOK_ID"]

if env_defined("WEBHOOK_URL"):
    WEBHOOK_URL = os.environ["WEBHOOK_URL"]
else:
    print("This script requires a configured WEBHOOK_URL")
    exit()

# get install state
# valid returns: "uninstalled", "Fully Installed", "no idea since there's no documentation"

def get_install_state():
    steamcmd = ["/steamcmd/steamcmd.sh"]
    steamcmd.extend(["+@ShutdownOnFailedCommand", "1"])
    steamcmd.extend(["+@NoPromptForPassword", "1"])
    steamcmd.extend(["+force_install_dir", "/arma3"])
    steamcmd.extend(["+login", "anonymous"])
    steamcmd.extend(["+app_info_update", "1"])
    steamcmd.extend(["+app_status", "233780"])
    if env_defined("STEAM_BRANCH"):
        steamcmd.extend(["-beta", os.environ["STEAM_BRANCH"]])
    if env_defined("STEAM_BRANCH_PASSWORD"):
        steamcmd.extend(["-betapassword", os.environ["STEAM_BRANCH_PASSWORD"]])
    steamcmd.extend(["+quit"])
    install_state = subprocess.check_output(steamcmd).decode("utf-8")
    return install_state

# gets text, updates the webhook with whatever is needed

def update_webhook():
    r = requests.post(WEBHOOK_URL, data=WEBHOOK_JSON)
    print(r.text)




res = re.search("install state: (.+?),\n", get_install_state())
if res:
    res = res.group(1)

currentTime = datetime.now().strftime("%H:%M:%S")


update_webhook()