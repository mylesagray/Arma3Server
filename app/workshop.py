import os
import re
import subprocess
import urllib.request
import keys

WORKSHOP = "steamapps/workshop/content/107410/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"  # noqa: E501


def mod(ids):
    steamcmd = [os.environ["STEAMCMDDIR"] + "/steamcmd.sh"]
    steamcmd.extend(["+force_install_dir", "/arma3"])
    steamcmd.extend(["+login", os.environ["STEAM_USER"]])
    for id in ids:
        steamcmd.extend(["+workshop_download_item", "107410", id])
        steamcmd.extend(["validate"])
    steamcmd.extend(["+quit"])
    try:
        subprocess.run(steamcmd, check=True)
    except subprocess.CalledProcessError:
        # If this is triggered, steamcmd ran into an issue, most likely a server side timeout
        # Retrying the download with the timeout set in .env, without +quit
        steamcmd.pop(-1)
        if "WORKSHOP_TIMEOUT" in os.environ and len(os.environ["WORKSHOP_TIMEOUT"]) > 0:
            timeout = int(os.environ["WORKSHOP_TIMEOUT"])*60
        else:
            timeout = 600
        subprocess.run(steamcmd, timeout=timeout, check=True)

def preset(mod_file):
    if mod_file.startswith("http"):
        req = urllib.request.Request(
            mod_file,
            headers={"User-Agent": USER_AGENT},
        )
        remote = urllib.request.urlopen(req)
        with open("preset.html", "wb", encoding='utf-8') as modpresetfile:
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
