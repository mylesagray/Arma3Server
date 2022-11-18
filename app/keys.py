from genericpath import isfile
import os
import shutil


def copy(moddir):
    print()
    if os.path.exists(os.path.join(moddir, "keys")):
        for o in os.listdir(os.path.join(moddir, "keys")):
            keyfile = os.path.join(os.path.join(moddir, "keys"), o)
            if not os.path.isdir(keyfile):
                shutil.copy2(keyfile, "/arma3/keys")
    elif os.path.exists(os.path.join(moddir, "key")):
        for o in os.listdir(os.path.join(moddir, "key")):
            keyfile = os.path.join(os.path.join(moddir, "key"), o)
            if not os.path.isdir(keyfile):
                shutil.copy2(keyfile, "/arma3/keys")
    else:
        if os.path.isfile(os.path.join(moddir, "meta.cpp")):
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
        else:
            print(f"### KEYS: Missing key(s): {moddir}")
