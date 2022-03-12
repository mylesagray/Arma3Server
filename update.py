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
# valid returns: "uninstalled", "Fully Installed", "no idea since there's no documentation"
#  - release state: released (No License)
#  - install state: Update Required,Update Started,
#  - install dir: "/arma3"
#  - mounted depots:
#  - size on disk: 0 bytes, BuildID 0
#  - update started: Thu Jan  1 00:00:00 1970, staged: 6914/6914 MB 100%, downloaded: 2775/2775 MB 100% - 0 KB/s
#  - update state:  ( No Error )
#  - user config: "UserConfig"
# root@docker-desktop:/arma3# cat startup.log
# 11:19:02 Dedicated host created.
# 11:19:16 BattlEye server updated to version: 217
# 11:19:16 BattlEye Server: Initialized (v1.217)
# 11:19:16 Game Port: 2302, Steam Query Port: 2303
# Arma 3 Console version 2.08.148892 x64 : port 2302
# 11:19:16 Host identity created.


def get_install_state():
  install_state = "undefined"
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
