import os
import re
import subprocess
import urllib.request
import keys
from time import sleep


WORKSHOP = "steamapps/workshop/content/107410/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"  # noqa: E501


def mod(ids):
    steamcmd = [os.environ["STEAMCMDDIR"] + "/steamcmd.sh"]
    steamcmd.extend(["+force_install_dir", "/arma3"])
    steamcmd.extend(["+login", os.environ["STEAM_USER"]])
    if os.environ["STEAM_PASSWORD"]:
        steamcmd.extend([os.environ["STEAM_PASSWORD"]])
    for id in ids:
        steamcmd.extend(["+workshop_download_item", "107410", id])
        steamcmd.extend(["validate"])
    steamcmd.extend(["+quit"])

    exit_code = 127
    while exit_code != 0:
        exit_code = subprocess.call(steamcmd)
        print(f"\n### DEBUG: Exit code {exit_code}.", flush=True)
        if exit_code == 5:
            print(f"### STEAM: We are throttled. Sleeping for 30 minutes...", flush=True)
            sleep(300)
            print(f"### STEAM: We are throttled. Sleeping for 25 more minutes...", flush=True)
            sleep(300)
            print(f"### STEAM: We are throttled. Sleeping for 20 more minutes...", flush=True)
            sleep(300)
            print(f"### STEAM: We are throttled. Sleeping for 15 more minutes...", flush=True)
            sleep(300)
            print(f"### STEAM: We are throttled. Sleeping for 10 more minutes...", flush=True)
            sleep(300)
            print(f"### STEAM: We are throttled. Sleeping for 5 more minutes...", flush=True)
            sleep(300)
            

def preset(mod_file):
    if mod_file.startswith("http"):
        req = urllib.request.Request(
            mod_file,
            headers={"User-Agent": USER_AGENT},
        )
        remote = urllib.request.urlopen(req)
        with open("preset.html", "wb") as modpresetfile:
            modpresetfile.write(remote.read())
        mod_file = "preset.html"
    mods = []
    with open(mod_file, 'r', encoding='utf-8') as modpresetfile:
        html = modpresetfile.read()
        regex = r"filedetails\/\?id=(\d+)\""
        matches = re.finditer(regex, html, re.MULTILINE)
        ids = []
        for _, match in enumerate(matches, start=1):
            ids.append(match.group(1))
            moddir = WORKSHOP + match.group(1)
            mods.append(moddir)
            keys.copy(moddir)
        mod(ids)
    return mods
