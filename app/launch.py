import os
import re
import subprocess
import signal
from time import sleep
import local
import workshop

def mod_param(name, mods):
    return ' -{}="{}" '.format(name, ";".join(mods))

def env_defined(key):
    return key in os.environ and len(os.environ[key]) > 0

CONFIG_FILE = os.environ["ARMA_CONFIG"]
BASIC_CONFIG_FILE = os.environ["BASIC_CONFIG"]

## Build login command

CONTAINER_ID = subprocess.check_output(["cat","/proc/1/cpuset"]).decode("utf-8")[8:20]
# since macOS docker is weird and /proc/1/cpuset is empty
if len(CONTAINER_ID) < 4:
    CONTAINER_ID = "<container>"
KEYS = "/arma3/keys"

if not os.path.isdir(KEYS):
    if os.path.exists(KEYS):
        os.remove(KEYS)
    os.makedirs(KEYS)

# check if there's a userdata folder other than anonymous, if it exists there  is login data,
# if not this script will NOT try to log in further until you log in manually
# this is required for proper 2FA and also to never store your password in ENV

def checkUSER():
    try:
        STEAMUSER = subprocess.check_output(['ls', os.environ["HOMEDIR"] + '/Steam/userdata/']).decode("utf-8").rstrip()
        return STEAMUSER
    except subprocess.CalledProcessError:
        subprocess.call(["echo", "Initial steam setup"])
        steamcmd = [os.environ["STEAMCMDDIR"] + "/steamcmd.sh"]
        steamcmd.extend(["+login", "anonymous"])
        steamcmd.extend(["+quit"])
        subprocess.call(steamcmd)
        exit()

STEAMUSER = checkUSER()
if STEAMUSER == "anonymous":
    subprocess.call(["echo","You need to manually log in, the setup will continue once it detecs a valid login"])
    subprocess.call(["echo","docker exec -it "+CONTAINER_ID+" /bin/bash " + os.environ["STEAMCMDDIR"] + "/steamcmd.sh +login "+os.environ["STEAM_USER"]+" +quit"])

while (STEAMUSER == "anonymous"):
    sleep(10)
    STEAMUSER = checkUSER()

subprocess.call(["echo", "Login data found, commencing with startup"])

## Install Arma

steamcmd = [os.environ["STEAMCMDDIR"] + "/steamcmd.sh"]
steamcmd.extend(["+force_install_dir", "/arma3"])
steamcmd.extend(["+login", os.environ["STEAM_USER"]])
steamcmd.extend(["+app_update", os.environ["STEAM_APPID"]])
if env_defined("STEAM_BRANCH"):
    steamcmd.extend(["-beta", os.environ["STEAM_BRANCH"]])
if env_defined("STEAM_BRANCH_PASSWORD"):
    steamcmd.extend(["-betapassword", os.environ["STEAM_BRANCH_PASSWORD"]])
steamcmd.extend(["validate", "+quit"])
subprocess.call(steamcmd)

## Mods

mods = []

if os.environ["MODS_PRESET"] != "":
    mods.extend(workshop.preset(os.environ["MODS_PRESET"]))

if os.environ["MODS_LOCAL"] == "true" and os.path.exists("mods"):
    mods.extend(local.mods("mods"))

## Build launchopts

launchopts = " -limitFPS={} -world={} {} {}".format(
    os.environ["ARMA_LIMITFPS"],
    os.environ["ARMA_WORLD"],
    os.environ["ARMA_PARAMS"],
    mod_param("mod", mods),
)

# Check if using Creator DLC

if os.environ["ARMA_CDLC"] != "":
    for cdlc in os.environ["ARMA_CDLC"].split(";"):
        launchopts += " -mod={}".format(cdlc)

# Check if using headless clients and create configs if so

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
        launchopts += ' -config="/tmp/arma3.cfg"'

    client_launchopts = launchopts
    client_launchopts += " -client -connect=127.0.0.1"
    if "password" in config_values:
        client_launchopts += " -password={}".format(config_values["password"])

    for i in range(0, clients):
        hc_launchopts = client_launchopts + ' -name="{}-hc-{}"'.format(
            os.environ["ARMA_PROFILE"], i
        )
        print("LAUNCHING ARMA CLIENT {} WITH".format(i), hc_launchopts)
        subprocess.Popen(hc_launchopts, shell=True)
else:
    launchopts += ' -config="/arma3/configs/{}"'.format(CONFIG_FILE)

# Add ports and profiles config to launchopts

launchopts += ' -port={} -name="{}" -profiles="/arma3/configs/profiles"'.format(
    os.environ["PORT"], os.environ["ARMA_PROFILE"]
)

# Load servermods if exists

if os.path.exists("servermods"):
    launchopts += mod_param("serverMod", local.mods("servermods"))

# Launch ArmA Server
print("LAUNCHING ARMA SERVER WITH", launchopts, flush=True)
botprocess = subprocess.Popen(["python3", "/app/bot.py"])
armaprocess = subprocess.Popen([os.environ["ARMA_BINARY"], launchopts])
try:
    armaprocess.wait()
except KeyboardInterrupt:
    subprocess.call(["echo", "Shutting down"])
    armaprocess.terminate()
    raise