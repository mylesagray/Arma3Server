import os
import re
import subprocess
import signal
from time import sleep
from datetime import datetime

import local
import workshop


task_manager = []
server_params = {
    "mod": [],
    "serverMod": [],
}
headless_params = {
    "client": "",
    "mod": [],
}

# Build directory names
USER_HOME_DIR = os.environ["HOMEDIR"]
STEAM_USER_DIR = os.path.join( USER_HOME_DIR, 'Steam/userdata' )
STEAM_INSTALL_DIR = os.environ["STEAM_APPDIR"]
STEAMCMD_DIR = os.environ["STEAMCMDDIR"]
STEAMCMD = os.path.join(STEAMCMD_DIR, "steamcmd.sh")
KEYS_DIR = os.path.join(STEAM_INSTALL_DIR,"keys")

# Map constants from env for better readability
USERNAME = os.environ["USER"]
USERID = int(os.environ["PUID"])
GROUPID = int(os.environ["PGID"])
STEAM_USER = os.environ["STEAM_USER"]
STEAM_PASSWORD = os.environ["STEAM_PASSWORD"]
ARMA_BINARY = os.environ["ARMA_BINARY"]
ARMA_PORT = int(os.environ["PORT"])
ARMA_PROFILE = os.environ["ARMA_PROFILE"]
ARMA_BASIC_CONFIG = os.environ["BASIC_CONFIG"]
ARMA_CONFIG = os.environ["ARMA_CONFIG"]
STEAM_APPID = os.environ["STEAM_APPID"]
STEAM_BRANCH = os.getenv("STEAM_BRANCH")
STEAM_BRANCH_PASSWORD = os.getenv("STEAM_BRANCH_PASSWORD")
ARMA_MOD_PRESET = os.getenv("MODS_PRESET")
ARMA_LIMITFPS = int(os.environ['ARMA_LIMITFPS'])
ARMA_WORLD = os.environ['ARMA_WORLD']
ARMA_PARAMS = os.environ['ARMA_PARAMS']
ARMA_CDLC = os.getenv("ARMA_CDLC")
ARMA_LOCAL_MODS = os.getenv("MODS_LOCAL")
ARMA_SERVER_LOCAL_MODS = os.getenv("SERVER_MODS_LOCAL")
ARMA_HEADLESS_CLIENTS = int(os.getenv("HEADLESS_CLIENTS"))
ARMA_SERVER_MODS_PRESET = os.getenv("SERVER_MODS_PRESET")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ARMA_CONFIG_FILE = f"{STEAM_INSTALL_DIR}/configs/{ARMA_CONFIG}"


# check if there's a userdata folder other than anonymous, if it exists there is login data,
# if not this script will NOT try to log in further until you log in manually
# this is required for proper 2FA and also to never store your password in ENV
def checkUSER():
    try:
        return subprocess.check_output([ 'ls', STEAM_USER_DIR ]).rstrip().decode("utf8").split("\n")[0]
    except subprocess.CalledProcessError:
        print("### STEAM: Initial steam setup", flush=True)
        steam_cmd = [STEAMCMD]
        steam_cmd.extend(["+login", "anonymous"])
        steam_cmd.extend(["+quit"])
        exit_code = 127
        while exit_code != 0:
            exit_code = subprocess.call(steam_cmd)
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
        exit()


def compile_launch_options(params_data):
    cmditems = []
    for key, data in params_data.items():
        if isinstance(data, list):
            cmditems.append(f"-{key}=\"{';'.join(data)}\"")
        elif isinstance(data, int):
            # int does not require quotation
            cmditems.append(f"-{key}={data}")
        elif len(data) == 0:
            # just the option
            cmditems.append(f"-{key}")
        elif data[0:1] == "\"" and data[-1:] == "\"":
            # value is already encapsulated
            cmditems.append(f"-{key}={data}")
        else:
            cmditems.append(f"-{key}=\"{data}\"")

    return " ".join(cmditems)


print("### SYSTEM: Setup user and group", flush=True)
# Set group id
try:
    group_id_cmd = [ "groupmod", "-g", str(GROUPID), USERNAME ]
    subprocess.call(group_id_cmd)
except Exception as exception:
    print(f"###\nERROR: Setting group ID failed: {exception}\n###", flush=True)

# Set user id
try:
    user_id_cmd =  [ "usermod", "-u", str(USERID), "-g", str(GROUPID), USERNAME ]
    subprocess.call(user_id_cmd)
except Exception as exception:
    print(f"###\nERROR: Setting user ID failed: {exception}\n###", flush=True)

# Update file permissions
print("### SYSTEM: Set file permissions", flush=True)

permission_targets = [
    os.sep.join(STEAM_INSTALL_DIR,"mpmissions")
]

for target in permission_targets:
    try:
        permission_cmd = [ "chmod", "-R", "777", target ]
        subprocess.call(permission_cmd)
    except Exception as exception:
        print(f"###\nERROR: Setting file permissions for '{target}': {exception}\n###", flush=True)

# Update file ownership
print("### SYSTEM: Set file ownership", flush=True)

permission_targets = [
    USER_HOME_DIR,
    STEAMCMD_DIR,
    STEAM_INSTALL_DIR,
    "/tmp/dumps",
    "/app",
]

for target in permission_targets:
    try:
        permission_cmd = [ "chown", "-R", f"{USERID}:{GROUPID}", target ]
        subprocess.call(permission_cmd)
    except Exception as exception:
        print(f"###\nERROR: Setting file ownership for '{target}': {exception}\n###", flush=True)

# Drop root privileges
print("### SYSTEM: Dropping root privileges", flush=True)
os.setgid(int(USERID))
os.setuid(int(GROUPID))

# Cleanup keys directory
if os.path.exists(KEYS_DIR):
    print("### SYSTEM: Deleting signing keys", flush=True)
    for item in os.listdir(KEYS_DIR):
        if os.path.isfile(os.path.join(KEYS_DIR,item)):
            if item.lower() not in ['a3.bikey','a3c.bikey','csla.bikey','gm.bikey','vn.bikey','ws.bikey']:
                os.remove(os.path.join(KEYS_DIR,item))

#######################
## Pre-Checks / Overrides
#######################
if ARMA_CDLC:
    server_params["mod"].extend(ARMA_CDLC.split(";"))
    headless_params["mod"].extend(ARMA_CDLC.split(";"))
    print(f"### ARMA: Creator DLC(s): {ARMA_CDLC}", flush=True)
    if STEAM_BRANCH.lower() != "creatordlc":
        print(f"###\nWARNING: Changing STEAM_BRANCH from \"{STEAM_BRANCH}\" to \"creatordlc\" since ARMA_CDLC is set.\n###", flush=True)
        STEAM_BRANCH = "creatordlc"

########################
## STEAM
########################

steamuser = checkUSER()
if steamuser == "anonymous":
    print("You need to manually log in, the setup will continue once it detecs a valid login", flush=True)
    if STEAM_PASSWORD:
        print("docker exec -it -u "+USERNAME+" <container> /bin/bash " +
            STEAMCMD + " +login "+STEAM_USER + 
            " "+STEAM_PASSWORD+" +quit", flush=True)
    else:
        print("docker exec -it -u "+USERNAME+" <container> /bin/bash " +
            STEAMCMD + " +login "+STEAM_USER+" +quit", flush=True)

while steamuser == "anonymous":
    sleep(10)
    steamuser = checkUSER()

print("### STEAM: Login data found, commencing with startup", flush=True)

# Install ArmA
steam_cmd = [STEAMCMD]
steam_cmd.extend(["+force_install_dir", STEAM_INSTALL_DIR])
# steam_cmd.extend(["+login", "anonymous"])
steam_cmd.extend(["+login", STEAM_USER])
if STEAM_PASSWORD:
    steam_cmd.extend([STEAM_PASSWORD])
steam_cmd.extend(["+app_update", STEAM_APPID])
if STEAM_BRANCH:
    steam_cmd.extend(["-beta", STEAM_BRANCH])
if STEAM_BRANCH_PASSWORD:
    steam_cmd.extend(["-betapassword", STEAM_BRANCH_PASSWORD])
steam_cmd.extend(["validate", "+quit"])

exit_code = 127
while exit_code != 0:
    exit_code = subprocess.call(steam_cmd)
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

#######################
## ArmA 3 Mods
#######################
print()

# Preset Mods
if ARMA_MOD_PRESET:
    loaded_preset = workshop.preset(ARMA_MOD_PRESET)
    server_params["mod"].extend(loaded_preset)
    headless_params["mod"].extend(loaded_preset)

if ARMA_SERVER_MODS_PRESET:
    server_params["serverMod"].extend(workshop.preset(ARMA_SERVER_MODS_PRESET))

# Local Mods
if ARMA_LOCAL_MODS and os.path.exists("mods"):
    server_params["mod"].extend(local.mods("mods"))
    headless_params["mod"].extend(local.mods("mods"))

if ARMA_SERVER_LOCAL_MODS and os.path.exists("servermods"):
    server_params["serverMod"].extend(local.mods("servermods"))

# TODO: This doesn't seem to work
print("### SYSTEM: Renaming mod files to lower case", flush=True)
subprocess.call(["/bin/bash", "/app/mods.sh"])

#######################
## ArmA 3 Headless
#######################
if ARMA_HEADLESS_CLIENTS:
    print(f"### ARMA: Setting up headless clients: {ARMA_HEADLESS_CLIENTS}", flush=True)
    # Read server config to dict
    with open(ARMA_CONFIG_FILE, 'r', encoding='utf-8') as server_config:
        data = server_config.read()
        REGEX = r"(.+?)(?:\s+)?=(?:\s+)?(.+?)(?:$|\/|;)"
        config_values = {}

        matches = re.finditer(REGEX, data, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            config_values[match.group(1).lower()] = match.group(2)

    # Prepare headless params
    headless_params["connect"] = f"127.0.0.1:{ARMA_PORT}"
    headless_params["config"] = ARMA_CONFIG_FILE
    headless_params["world"] = ARMA_WORLD

    if "password" in config_values:
        headless_params["password"] = config_values['password']

    for i in range(1, ARMA_HEADLESS_CLIENTS+1):
        tmp_params = headless_params
        tmp_params["name"] = f"{ARMA_PROFILE}-hc-{i}"
        print(f"### ARMA: Launching ArmA Client {i} with: {ARMA_BINARY} {compile_launch_options(tmp_params)}", flush=True)
        task_manager.append(
            subprocess.Popen(os.path.join(STEAM_INSTALL_DIR, ARMA_BINARY) + " " +compile_launch_options(tmp_params), shell=True)
            )


#######################
## ArmA 3 Server
#######################
server_params["config"] = ARMA_CONFIG_FILE
server_params["world"] = ARMA_WORLD
server_params["limitFPS"] = ARMA_LIMITFPS
server_params["port"] = ARMA_PORT
server_params["name"] = ARMA_PROFILE
server_params["profiles"] = f"{STEAM_INSTALL_DIR}/configs/profiles"
server_params["cfg"] = f"{STEAM_INSTALL_DIR}/configs/{ARMA_BASIC_CONFIG}"

# Launch ArmA Server
if DISCORD_TOKEN:
    print("### DISCORD: Launching Discord bot", flush=True)
    botprocess = subprocess.Popen(["python3", "/app/bot.py"])
    
print(f"### ARMA: Launching ArmA Server with: {ARMA_BINARY} {compile_launch_options(server_params)} {ARMA_PARAMS}", flush=True)
timestamp = datetime.now().strftime("%Y%m%d-%H%M")
logfile = open(f"{STEAM_INSTALL_DIR}/logs/server-{ARMA_PROFILE}-{timestamp}.log", 'w', encoding='utf-8')
armaprocess = subprocess.Popen(
    [
        os.path.join(STEAM_INSTALL_DIR, ARMA_BINARY),
        compile_launch_options(server_params) + " " + ARMA_PARAMS,
    ],
    stdout=logfile,
    stderr=logfile
)

try:
    armaprocess.wait()
    logfile.close()
except KeyboardInterrupt:
    print("### SYSTEM: Shutting down...", flush=True)
    for target in task_manager:
        print(f" - {target.pid}", flush=True)
    for target in task_manager:
        print(f"    SIGINT client {target.pid}", flush=True)
        target.send_signal(signal.SIGINT)
        target.wait(timeout=30)
    print(f"    SIGINT server {armaprocess.pid}", flush=True)
    armaprocess.send_signal(signal.SIGINT)
    armaprocess.wait(timeout=30)
    raise
