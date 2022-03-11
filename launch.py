import os
import re
import subprocess

import local
import workshop


def mod_param(name, mods):
    return ' -{}="{}" '.format(name, ";".join(mods))


def env_defined(key):
    return key in os.environ and len(os.environ[key]) > 0


CONFIG_FILE = os.environ["ARMA_CONFIG"]
BASIC_CONFIG_FILE = os.environ["BASIC_CONFIG"]
KEYS = "/arma3/keys"

if not os.path.isdir(KEYS):
    if os.path.exists(KEYS):
        os.remove(KEYS)
    os.makedirs(KEYS)

# check if there's a ssfn(\d) file, if it exists there  is login data,
# if not this script will NOT try to log in further until you log in manually
# this is required for proper 2FA and also to never store your password in ENV

def checkSSFN():
    try:
        SSFN = subprocess.check_output(['ls','/root/Steam/']).decode("utf-8")
        return SSFN
    except subprocess.CalledProcessError:
        subprocess.call(["echo", "Initial steam setup"])
        steamcmd = ["/steamcmd/steamcmd.sh"]
        steamcmd.extend(["+login", "anonymous"])
        steamcmd.extend(["+quit"])
        subprocess.call(steamcmd)
        exit()

SSFN = checkSSFN()

while ("ssfn" not in SSFN):
    subprocess.call(["echo","You need to manually log in, the setup will continue once it detecs a valid login"])
    subprocess.call(["echo","docker exec -it <container_name> /bin/bash /steamcmd/steamcmd.sh +login +quit"])
    subprocess.call(["sleep","10"])
    SSFN = checkSSFN()

subprocess.call(["echo", "Login data found, commencing with startup"])

# Install Arma

steamcmd = ["/steamcmd/steamcmd.sh"]
steamcmd.extend(["+force_install_dir", "/arma3"])
steamcmd.extend(["+login", os.environ["STEAM_USER"]])
steamcmd.extend(["+app_update", "233780"])
if env_defined("STEAM_BRANCH"):
    steamcmd.extend(["-beta", os.environ["STEAM_BRANCH"]])
if env_defined("STEAM_BRANCH_PASSWORD"):
    steamcmd.extend(["-betapassword", os.environ["STEAM_BRANCH_PASSWORD"]])
steamcmd.extend(["validate", "+quit"])
subprocess.call(steamcmd)

# Mods

mods = []

if os.environ["MODS_PRESET"] != "":
    mods.extend(workshop.preset(os.environ["MODS_PRESET"]))

if os.environ["MODS_LOCAL"] == "true" and os.path.exists("mods"):
    mods.extend(local.mods("mods"))

launch = "{} -limitFPS={} -world={} {} {}".format(
    os.environ["ARMA_BINARY"],
    os.environ["ARMA_LIMITFPS"],
    os.environ["ARMA_WORLD"],
    os.environ["ARMA_PARAMS"],
    mod_param("mod", mods),
)

if os.environ["ARMA_CDLC"] != "":
    for cdlc in os.environ["ARMA_CDLC"].split(";"):
        launch += " -mod={}".format(cdlc)

clients = int(os.environ["HEADLESS_CLIENTS"])
print("Headless Clients:", clients)

if clients != 0:
    with open("/arma3/configs/{}".format(CONFIG_FILE)) as config:
        data = config.read()
        regex = r"(.+?)(?:\s+)?=(?:\s+)?(.+?)(?:$|\/|;)"

        config_values = {}

        matches = re.finditer(regex, data, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            config_values[match.group(1).lower()] = match.group(2)

        if "headlessclients[]" not in config_values:
            data += '\nheadlessclients[] = {"127.0.0.1"};\n'
        if "localclient[]" not in config_values:
            data += '\nlocalclient[] = {"127.0.0.1"};\n'

        with open("/tmp/arma3.cfg", "w") as tmp_config:
            tmp_config.write(data)
        launch += ' -config="/tmp/arma3.cfg"'

    client_launch = launch
    client_launch += " -client -connect=127.0.0.1"
    if "password" in config_values:
        client_launch += " -password={}".format(config_values["password"])

    for i in range(0, clients):
        hc_launch = client_launch + ' -name="{}-hc-{}"'.format(
            os.environ["ARMA_PROFILE"], i
        )
        print("LAUNCHING ARMA CLIENT {} WITH".format(i), hc_launch)
        subprocess.Popen(hc_launch, shell=True)

else:
    launch += ' -config="/arma3/configs/{}"'.format(CONFIG_FILE)

launch += ' -port={} -name="{}" -profiles="/arma3/configs/profiles"'.format(
    os.environ["PORT"], os.environ["ARMA_PROFILE"]
)

if os.path.exists("servermods"):
    launch += mod_param("serverMod", local.mods("servermods"))

print("LAUNCHING ARMA SERVER WITH", launch, flush=True)
os.system(launch)
