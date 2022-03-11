from encodings import utf_8
import os
import re
import subprocess
import requests
import json
from datetime import datetime, date, timedelta


WEBHOOK_JSON = json.loads("""
{
  "username": "ALARMA",
  "avatar_url": "https://s.minuq.net/bb.jpg",
  "content": "ARMA3 Server status",
  "embeds": [
    {
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
        }
      ]
    }
  ]
}
""")


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
    r = requests.post(WEBHOOK_URL, json=WEBHOOK_JSON)
    print(r.text)


res = re.search("install state: (.+?),\n", get_install_state())
if res:
    res = res.group(1)

currentTime = datetime.now().strftime("%H:%M:%S")


update_webhook()