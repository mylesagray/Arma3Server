import os
import shutil


def copy(moddir):
    processed_keys = 0

    # Try to find human readable name

    try:
        with open(os.path.join(moddir, "meta.cpp"), "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith("name"):
                    modname = line[line.index("\"")+1:]
                    modname = modname[0:modname.index("\"")]
    except:
        modname = moddir

    # print(f"### KEYS: Modname = {modname}")

    for addon_path, addon_subdirs, addon_files in os.walk(moddir):
        for fname in addon_files:
            if fname.lower().endswith('.bikey'):
                processed_keys = processed_keys + 1
                shutil.copy2(os.path.join(addon_path, fname), "/arma3/keys")
    
    if not processed_keys:
        try:
            if modname:
                print(f"### KEYS: Missing key(s): {modname}")
            else:
                print(f"### KEYS: Missing key(s): {moddir}")
        except:
            print(f"### KEYS: Missing key(s)_: {moddir}")
    # else:
    #     print(f"### KEYS: {modname}: {processed_keys} Key/s copied.")
