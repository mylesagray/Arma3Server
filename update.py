from encodings import utf_8
import os
import re
import subprocess
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
LOG_FILE="/arma3/startup.log"

def env_defined(key):
    return key in os.environ and len(os.environ[key]) > 0


# get install state
# valid returns: "uninstalled", "Fully Installed", "Update Required,Update Started," "no idea since there's no documentation"

def get_install_state():
  install_state = "undefined"
  steamcmd = [os.environ["STEAMCMDDIR"] + "/steamcmd.sh"]
  steamcmd.extend(["+@ShutdownOnFailedCommand", "1"])
  steamcmd.extend(["+@NoPromptForPassword", "1"])
  steamcmd.extend(["+force_install_dir", "/arma3"])
  steamcmd.extend(["+login", "anonymous"])
  steamcmd.extend(["+app_info_update", "1"])
  steamcmd.extend(["+app_status", os.environ["STEAM_APPID"]])
  if env_defined("STEAM_BRANCH"):
    steamcmd.extend(["-beta", os.environ["STEAM_BRANCH"]])
  if env_defined("STEAM_BRANCH_PASSWORD"):
    steamcmd.extend(["-betapassword", os.environ["STEAM_BRANCH_PASSWORD"]])
  steamcmd.extend(["+quit"])
  res = subprocess.check_output(steamcmd).decode("utf-8")
  res = re.search("install state: (.+?),\n", res)
  if res:
    install_state = res.group(1)
  return install_state

def get_version():
  version = "undefined"
  res = subprocess.check_output(["more", LOG_FILE]).decode("utf-8")
  res = re.search("Arma 3 Console version (.+?) x64(.+?)", res)
  if res:
    version = res.group(1)
  return version
