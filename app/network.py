import os
import traceback
from ipaddress import ip_address, IPv6Address, IPv4Address

import requests
from steam import SteamQuery


def get_players():
    """
    Returns a tuple with the current number of players connected
    to the server as well as the max players supported respectively
    """
    try:
        server = _server_connection()
        server_state = _lint_steamquery_output(server.query_server_info())
        current_players = server_state["players"]
        max_players = server_state["max_players"]
        return current_players, max_players

    except Exception:
        print("Could not get server info")
        traceback.print_exc()
        return


def get_players_details() -> list:
    """
    Returns a list with all current player objects containing
    names, scores and durations on the server
    """
    try:
        server = _server_connection()
        player_info = _lint_steamquery_output(server.query_player_info())
        return player_info

    except Exception:
        print("Could not get player info")
        traceback.print_exc()
        return

# Gets the external IP address where the server is running
# this assumes that the outbound IP after NAT and inbound IP
# before NAT are the same IP address.
#
# Unknown how this will behave in IPv6 environments, but the
# assumption is that it will work just the same as no NAT is
# used in IPv6 and the external IPv6 address will be the
# global address of the machine


def get_external_ip() -> str:
    """
    Gets the current external IP of where the app is running.
    This uses ifconfig.me and assumes it is not blocked or down.
    """
    try:
        response = requests.get('https://ifconfig.me/ip', timeout=5)
        return str(response.content.decode())

    except Exception:
        print("External IP could not be found, ifconfig.me may be down or blocked")
        traceback.print_exc()
        return

# Validates if the IP address given is valid


def _valid_ip_address(IP: int) -> int:
    """
    Checks if the IP address passed is a Valid IPv4 or IPv6 address
    """
    try:
        if type(ip_address(IP)) is IPv4Address:
            return True
        elif type(ip_address(IP)) is IPv6Address:
            return True

    except ValueError:
        raise

# Validates if the given port is in valid range


def _valid_port(port: int) -> int:
    """
    Checks if a given port is in the valid list of ranges for UDP ports
    """
    try:
        port = int(port)
        if port > 0 and port <= 65535:
            return True
        else:
            raise ValueError(f'PORT {port} is not in valid range 1-65535')

    except Exception:
        raise

# Creates and returns server connection object


def _server_connection() -> object:
    """
    Creates a steam query server connection object and passes it back.
    """
    arma_port = os.environ["PORT"]
    try:
        # Import server IP from env var for debugging if
        # it is not defined, get the current external IP
        # if it is, import and validate the IP from env
        if "SERVER_IP" not in os.environ:
            server_ip = get_external_ip()
            if not _valid_ip_address(server_ip):
                raise
        else:
            server_ip = os.environ["SERVER_IP"]
            if not _valid_ip_address(server_ip):
                raise

        # Steam Query port for Arma is the base server port +1
        # Ex: base server port is 2302, so query port is 2303
        if _valid_port(arma_port):
            server_port = int(arma_port) + 1
        else:
            raise ValueError("PORT environment variable is invalid")

        server = SteamQuery(server_ip, server_port, 15)
        return server

    except Exception:
        print("Unable to connect to server")
        traceback.print_exc()
        return


def _lint_steamquery_output(query):
    """
    Checks if SteamQuery output should have been an exception
    and if so raises one, kill me
    """
    # SteamQuery lib returns errors as strings, so need to
    # check if "error" key is present to detect exceptions
    # when errored, it is always passed back as a dict
    #
    # If the query is a list, then it is a valid response
    # in any case
    if isinstance(query, list):
        return query
    else:
        try:
            if "error" in query.keys():
                raise ConnectionError(str(query))
            else:
                return query
        except Exception:
            traceback.print_exc()
