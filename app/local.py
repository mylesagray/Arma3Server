import os

import keys


def mods(directory) -> list:
    """
    Returns a list of mods enumerated from a given directory
    """
    modlist = []

    # Find mod folders
    for mod in os.listdir(directory):
        moddir = os.path.join(directory, mod)
        if os.path.isdir(moddir):
            modlist.append(moddir)
            keys.copy(moddir)

    return modlist
