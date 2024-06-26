import os
import re
import subprocess
from datetime import datetime, date, timedelta

LOG_FILE = "/arma3/startup.log"
CONFIG_FILE = os.environ["ARMA_CONFIG"]


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


def get_server_details():
    server_name = "undefined"
    server_password = "undefined"
    with open(f'/arma3/configs/{CONFIG_FILE}', 'r', encoding='utf-8') as config:
        data = config.read()
        regex = r"(.+?)(?:\s+)?=(?:\s+)?(.+?)(?:$|\/|;)"

        config_values = {}

        matches = re.finditer(regex, data, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            config_values[match.group(1).lower()] = match.group(2)

        if "hostname" in config_values:
            server_name = config_values["hostname"]
            if server_name.startswith('"') and server_name.endswith('"'):
                server_name = server_name[1:-1]

        if "password" in config_values:
            server_password = config_values["password"]
            if server_password.startswith('"') and server_password.endswith('"'):
                server_password = server_password[1:-1]

    return server_name, server_password
