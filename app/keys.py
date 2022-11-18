import os
import shutil


def copy(moddir):
    print()
    processed_keys = 0
    for addon_path, addon_subdirs, addon_files in os.walk(moddir):
        for fname in addon_files:
            if fname.lower().endswith('.bikey'):
                processed_keys
                shutil.copy2(os.path.join(addon_path, fname), "/arma3/keys")
    
    if not processed_keys:
        try:
            modname = None
            with open(os.path.join(moddir, "meta.cpp"), "r") as file:
                for line in file:
                    if line.startswith("name"):
                        modname = line[line.index("\"")-1:-1]
            if modname:
                print(f"### KEYS: Missing key(s): {modname}")
            else:
                print(f"### KEYS: Missing key(s): {moddir}")
        except:
            print(f"### KEYS: Missing key(s)_: {moddir}")

