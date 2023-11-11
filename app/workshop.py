import os
import re
import subprocess
import urllib.request
import keys
from time import sleep
from itertools import islice


WORKSHOP = "steamapps/workshop/content/107410/"
# WORKSHOP = "mod/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"  # noqa: E501


# def update_directory_names(dirs,old_dir,new_dir):
#   for index in range(0,len(dirs)-1):
#     # if dirs[index].startswith(old_dir):
#     dirs[index] = dirs[index].replace(old_dir,new_dir)

#   return dirs

def modFilesLower(startdir):
    print(f"\n### WORKSHOP: Checking to rename files...")

    addon_dirs = []

    # Files pass
    for addon_path, _, addon_files in os.walk(startdir):
        for fname in addon_files:

            fname_lower = fname.lower()
            # if name needs to be "converted"
            if fname != fname_lower:
                # test if lower case file already exists
                print(f"\n### WORKSHOP: Rename: {fname} -> {fname_lower}")

                # Steam seems to be smart enough to write in the lowercase file, if exists
                
                # try the rename
                try:
                    os.rename(os.sep.join([addon_path,fname]), os.sep.join([addon_path,fname_lower]))
                except Exception as e:
                    print(f"\n### WORKSHOP: ERROR: Renaming file failed: {e}")

    # Directories pass
    addon_path_list = []

    for addon_path, _, addon_files in os.walk(startdir):
        addon_path_list.append(addon_path)

    # Reverse to traverse from deepest directory backwards
    addon_path_list.reverse()
    for addon_path in addon_path_list:
        addon_path_array = addon_path.split(os.sep)
        addon_path_array_lower = addon_path_array.copy()
        addon_path_array_lower[-1] = addon_path_array_lower[-1].lower()

        if addon_path_array[-1] != addon_path_array_lower[-1]:
            # try the rename
            try:
                print(f"\n### WORKSHOP: Rename Dir: {os.sep.join(addon_path_array)} -> {os.sep.join(addon_path_array_lower)}")
                os.rename(os.sep.join(addon_path_array), os.sep.join(addon_path_array_lower))
            except Exception as e:
                print(f"\n### WORKSHOP: ERROR: Renaming failed: {e}")


def fixMissingModCpp(ids):
    print(f"\n### WORKSHOP: Checking if all mod.cpp present...")

    DIR = os.sep.join([os.environ["STEAM_APPDIR"],WORKSHOP])
    for id in ids:
        # print(f"### DEBUG: checking: {os.path.isfile(os.path.join(DIR,id,'mod.cpp'))}")
        if not os.path.isfile(os.path.join(DIR,id,"mod.cpp")):
            print(f"### WORKSHOP: No mod.cpp found for {id}")
            # print(f"### DEBUG: checking: {os.path.isfile(os.path.join(DIR,id,'meta.cpp'))}")
            if os.path.isfile(os.path.join(DIR,id,"meta.cpp")):
                print(f"### WORKSHOP: Trying to build mod.cpp from meta.cpp for {id}.")
                with open(os.path.join(DIR,id,"mod.cpp"), 'w') as fw:
                    with open(os.path.join(DIR,id,"meta.cpp")) as fr:
                        for line in fr.readlines():
                            if line.startswith("name"):
                                fw.write(line)
                            elif line.startswith("timestamp"):
                                match = re.search(r"(\d+)", line, re.MULTILINE)
                                if match:
                                    fw.write(f"tooltip = \"{match.group(1)}\";\n")
            else:
                print(f"\n### WORKSHOP: ERROR: Unable to build mod.cpp for {id}")


def fixMissingMetaCppId(ids):
    print(f"\n### WORKSHOP: Checking if meta.cpp correct...")

    DIR = os.sep.join([os.environ["STEAM_APPDIR"],WORKSHOP])
    for id in ids:
        newMetaCpp = ""
        if os.path.isfile(os.path.join(DIR,id,"meta.cpp")):
            with open(os.path.join(DIR,id,"meta.cpp")) as fr:
                for line in fr.readlines():
                    if line.startswith("publishedid"):
                        match = re.search(r"(\d+)", line, re.MULTILINE)
                        if match:
                            if match.group(1) == "0":
                                # we need to fix
                                print(f"### WORKSHOP: Fixing meta.cpp for {id}.")
                                newMetaCpp = f"{newMetaCpp}publishedid = {id};\n"
                            else:
                                # already good
                                newMetaCpp = newMetaCpp+line
                        else:
                            # didn't match
                            print(f"### Debug: {line}")
                            newMetaCpp = newMetaCpp+line
                    else:
                        # not publishedid line
                        newMetaCpp = newMetaCpp+line

            # Write new file
            with open(os.path.join(DIR,id,"meta.cpp"),'w') as fw:
                fw.write(newMetaCpp)

def chunks(data, SIZE=15):
    for i in range(0, len(data), SIZE):
        yield data[i:i + SIZE]


def download_mods(ids):
    if len(ids) > 0:
        CHUNK_SIZE = 15
        total = len(ids)

        # We need to split up downloads over multiple passes since steam runs out of memory otherwise (32bit goodes, yay)
        for ids_chunk in chunks(ids, CHUNK_SIZE):
            # total = total+len(ids_chunk)
            print(f"\n### WORKSHOP: Queing {len(ids_chunk)} mods from {total} remaining for download: {ids_chunk}.", flush=True)
            steamcmd = [os.environ["STEAMCMDDIR"] + "/steamcmd.sh"]
            steamcmd.extend(["+force_install_dir", os.environ["STEAM_APPDIR"]])
            steamcmd.extend(["+login", os.environ["STEAM_USER"]])
            if os.environ["STEAM_PASSWORD"]:
                steamcmd.extend([os.environ["STEAM_PASSWORD"]])
            for id in ids_chunk:
                steamcmd.extend(["+workshop_download_item", "107410", id])
                steamcmd.extend(["validate"])
            steamcmd.extend(["+quit"])

            total = total-CHUNK_SIZE

            exit_code = 127
            while exit_code != 0:
                exit_code = subprocess.call(steamcmd)
                # print(f"\n### DEBUG: Exit code {exit_code}.", flush=True)
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

        # All downloads finished - Rename files to lower case
        modFilesLower(os.sep.join([os.environ["STEAM_APPDIR"],WORKSHOP]))
        # All downloads finished - Fix broken Mod-Infos
        fixMissingModCpp(ids)
        fixMissingMetaCppId(ids)


def preset(mod_file, optional_mod=False, server_mod=False):
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
        # for each Steam-Mod-ID from HTML/file
        for _, match in enumerate(matches, start=1):
            ids.append(match.group(1))
            moddir = WORKSHOP + match.group(1)

            if optional_mod:
                print(f"\n### WORKSHOP: Optional mod: {match.group(1)}.", flush=True)
                mods.append(moddir) # Required to download the mod to be able to copy the signing keys
                # keys.copy(moddir) # Wrong place - not downloaded yet
            elif server_mod:
                print(f"\n### WORKSHOP: Server mod: {match.group(1)} - SKIPPING KEY.", flush=True)
                mods.append(moddir)
                # Do not copy the keys. So clients will not be asked to load the server mod
            else:
                # Required mod for server and client
                # print(f"\n### WORKSHOP: Adding mod to load: {match.group(1)}.", flush=True)
                mods.append(moddir)
                # keys.copy(moddir) # Wrong place - not downloaded yet

        if(ids):
            download_mods(ids)

        # mod or optional mod
        if not server_mod:
            for mod_dir in mods:
                keys.copy(mod_dir)

    # TODO: Delete presets.html

    if optional_mod:
        # Optional mods don't need to be loaded (clientside)
        return []
    else:
        return mods
