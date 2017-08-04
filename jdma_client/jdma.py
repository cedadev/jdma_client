#! /usr/bin/env python
"""Command line tool for interacting with the JASMIN data migration app (JDMA) for users who are
logged into JASMIN and have full JASMIN accounts."""

# Author : Neil R Massey
# Date   : 28/07/2017

import sys, os
import argparse
import requests
import json

# switch off warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class settings:
    """Settings for the xfc command line tool."""
    JDMA_SERVER_URL = "http://0.0.0.0:8001/jdma_control"  # location of the jdma_control server / app
    JDMA_API_URL = JDMA_SERVER_URL + "/api/v1/"
#    USER = os.environ["USER"] # the USER name
    USER = "vagrant"
    VERSION = "0.1" # version of this software
    VERIFY = False


unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB'], [0, 0, 1, 1, 1, 1, 1])
def sizeof_fmt(num):
    """Human friendly file size"""
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:>5.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    elif num == 1:
        return '1 byte'
    else:
        return '0 bytes'


class bcolors:
    MAGENTA   = '\033[95m'
    BLUE      = '\033[94m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    RED       = '\033[91m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    INVERT    = '\033[7m'
    ENDC      = '\033[0m'


def do_init(email=""):
    """Send the HTTP request (POST) to initialize a user."""
    url = settings.JDMA_API_URL + "user"
    data = {"name" : settings.USER}
    if email != "":
        data["email"] = email

    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)
    # check the response code
    if response.status_code == 200:
        data = response.json()
        sys.stdout.write( bcolors.GREEN +\
              "** SUCCESS ** - user initiliazed with:\n" + bcolors.ENDC +\
              "    username: " + data["name"] + "\n" +\
              "    email: " + data["email"] + "\n")
    else:
        # get the reason why it failed
        error = response.json()['error']
        user = response.json()['name']
        sys.stdout.write(bcolors.RED+\
              "** ERROR ** - cannot initialize user " + user + " : " + error + bcolors.ENDC + "\n")


def do_email(email=""):
    """Send the HTTP request (PUT) to update the email address of the user by sending a PUT request."""
    url = settings.JDMA_API_URL + "user?name=" + settings.USER
    data = {"name" : settings.USER}
    data["email"] = email
    response = requests.put(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        sys.stdout.write(bcolors.GREEN+\
              "** SUCCESS ** - user email updated to: " + data["email"] + bcolors.ENDC + "\n")
    else:
        # get the reason why it failed
        error = response.json()['error']
        user = response.json()['name']
        sys.stdout.write(bcolors.RED+\
              "** ERROR ** - cannot update email for user " + user+ " : " + error + bcolors.ENDC + "\n")


def do_info():
    """Send the HTTP request (GET) to return information about the user."""
    url = settings.JDMA_API_URL + "user?name=" + settings.USER
    data = {"name" : settings.USER}
    response = requests.get(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        sys.stdout.write(bcolors.GREEN+ \
                         "** SUCCESS ** - user info:\n" + bcolors.ENDC + \
                         "    username: " + data["name"] + "\n" + \
                         "    email   : " + data["email"] + "\n" + \
                         "    notify  : " + ["off", "on"][data["notify"]] +"\n")
    else:
        # get the reason why it failed
        error = response.json()['error']
        user = response.json()['name']
        sys.stdout.write(bcolors.RED+\
              "** ERROR ** - cannot get info for user " + user + " : " + error + bcolors.ENDC + "\n")


def do_notify():
    """Send the HTTP request (PUT) to switch on / off notifications for the user."""
    # first get the status of notifications
    url = settings.JDMA_API_URL + "user?name=" + settings.USER
    response = requests.get(url, verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        notify = data["notify"]
        # update to inverse
        put_data = {"name" : settings.USER,
                    "notify": not notify}
        response = requests.put(url, data=json.dumps(put_data), verify=settings.VERIFY)
        if response.status_code == 200:
            sys.stdout.write(bcolors.GREEN+\
                  "** SUCCESS ** - user notifications updated to: " + ["off", "on"][put_data["notify"]] + bcolors.ENDC +"\n")
        else:
            # get the reason why it failed
            error = response.json()['error']
            user = response.json()['name']
            sys.stdout.write(bcolors.RED+\
                  "** ERROR ** - cannot update notify for user " + user + " : " + error + bcolors.ENDC + "\n")

    else:
        # get the reason why it failed
        error = response.json()['error']
        user = response.json()['name']
        sys.stdout.write(bcolors.RED+\
              "** ERROR ** - cannot update notify for user " + user + " : " + error + bcolors.ENDC + "\n")


def get_request_type(req_type):
    """Get a string from a request type integer.  See jdma_control.models.MigrationRequest for details"""
    request_types = ["PUT", "GET", "VERIFY"]
    return request_types[req_type]


def get_request_stage(stage):
    request_stages = ["ON_DISK", "PUT_PENDING", "PUT", "ON_TAPE", "GET_PENDING", "GET", "FAILED"]
    return request_stages[stage]

def get_permissions_string(p):
    is_dir = 'd'
    dic = {'7':'rwx', '6' :'rw-', '5' : 'r-x', '4':'r--', '0': '---'}
    perm = str(p)[-3:]
    return is_dir + ''.join(dic.get(x,x) for x in perm)


def do_request(req_id, workspace):
    """Send the HTTP request (GET) to get the details about a single request."""
    url = settings.JDMA_API_URL + "migration?name=" + settings.USER
    if req_id != None:
        url += ";request_id=" + str(req_id)
    if workspace != None:
        url += ";workspace=" + workspace
    # send the request
    response = requests.get(url, verify=settings.VERIFY)
    # process if returned
    if response.status_code == 200:
        data = response.json()
        # print the response
        sys.stdout.write(bcolors.MAGENTA)
        sys.stdout.write("Migration request for user: " + data["user"] + "\n")
        sys.stdout.write(bcolors.ENDC)
        sys.stdout.write("    Request id   : " + str(data["request_id"])+"\n")
        sys.stdout.write("    Workspace    : " + data["workspace"]+"\n")
        if "label" in data:
            sys.stdout.write("    Label        : " + data["label"]+"\n")
        if "registered_date" in data:
            sys.stdout.write("    Date         : " + data["registered_date"][0:16].replace("T"," ")+"\n")
        sys.stdout.write("    Request type : " + get_request_type(data["request_type"])+"\n")
        sys.stdout.write("    Stage        : " + get_request_stage(data["stage"])+"\n")
        if "et_id" in data:
            sys.stdout.write("    ET id        : " + str(data["et_id"]) + "\n")
        sys.stdout.write("    Directory    : " + data["original_path"]+"\n")
        if "unix_user_id" in data:
            sys.stdout.write("    Unix uid     : " + data["unix_user_id"]+"\n")
        if "unix_group_id" in data:
            sys.stdout.write("    Unix gid     : " + data["unix_group_id"]+"\n")
        if "unix_permission" in data:
            sys.stdout.write("    Unix filep   : " + get_permissions_string(data["unix_permission"])+"\n")
    else:
        # get the reason why it failed
        data = response.json()
        error_msg = "** ERROR ** - cannot list request " + str(data["request_id"]) + " for user " + data["name"]
        if "workspace" in data:
            error_msg += " in workspace " + data["workspace"]
        error_msg += " : " + data["error"] + "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)


def do_list_requests(workspace):
    """Send the HTTP request (GET) to get the details about all of a user's requests,
       filtering on the workspace."""
    url = settings.JDMA_API_URL + "migration?name=" + settings.USER
    if workspace != None:
        url += ";workspace=" + workspace

    response = requests.get(url, verify=settings.VERIFY)
    if response.status_code == 200:
        # get the list of responses from the JSON
        data = response.json()
        n_req = len(data["requests"])
        if n_req == 0:
            error_msg = "** ERROR ** - No requests found for user " + settings.USER
            if workspace != None:
                error_msg += " in workspace " + workspace
            error_msg += "\n"
            sys.stdout.write(bcolors.RED + error_msg)
            sys.stdout.write(bcolors.ENDC)
        else:
            # print the header
            sys.stdout.write(bcolors.MAGENTA)
            print "{:>4} {:<16} {:<16} {:<6} {:<11} {:<16}".format("id", "workspace", "label", "type", "stage", "date")
            sys.stdout.write(bcolors.ENDC)
            for r in data["requests"]:
                print "{:>4} {:<16} {:<16} {:<6} {:<11} {:<16}".format(\
                    r["request_id"],
                    r["workspace"][0:16],
                    r["label"][0:16],
                    get_request_type(r["request_type"]),
                    get_request_stage(r["stage"]),
                    r["registered_date"][0:16].replace("T"," "))
    else:
        error_data = response.json()
        error_msg = "** ERROR ** - cannot list requests for user " + error_data["name"]
        if "workspace" in error_data:
            error_msg += " in workspace " + error_data["workspace"]
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)


def do_put(path, workspace, label):
    """Send the HTTP request (POST) to indicate a directory is to be migrated."""
    url = settings.JDMA_API_URL + "migration"
    # set the user and request type data
    data = {"name" : settings.USER,
            "request_type" : "PUT"}
    # add the path and workspace - if the workspace is none then don't add
    # in this case the HTTP API will return an error as a workspace is required
    if path:
        data["original_path"] = path
    if workspace:
        data["workspace"] = workspace
    if label:
        data["label"] = label

    # do the request (POST)
    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        sys.stdout.write(bcolors.GREEN+ \
                         "** SUCCESS ** - migration requested:\n" + bcolors.ENDC)
        sys.stdout.write("    Request id   : " + str(data["request_id"])+"\n")
        sys.stdout.write("    Workspace    : " + data["workspace"]+"\n")
        sys.stdout.write("    Label        : " + data["label"]+"\n")
        sys.stdout.write("    Date         : " + data["registered_date"][0:16].replace("T"," ")+"\n")
        sys.stdout.write("    Request type : " + get_request_type(data["request_type"])+"\n")
        sys.stdout.write("    Stage        : " + get_request_stage(data["stage"])+"\n")
        sys.stdout.write("    Directory    : " + data["original_path"]+"\n")
        sys.stdout.write("    Unix uid     : " + data["unix_user_id"]+"\n")
        sys.stdout.write("    Unix gid     : " + data["unix_group_id"]+"\n")
        sys.stdout.write("    Unix filep   : " + get_permissions_string(data["unix_permission"])+"\n")
    else:
        # print the error
        error_data = response.json()
        error_msg = "** ERROR ** - cannot PUT directory"
        if path:
            error_msg += " " + path
        error_msg += " for user " + settings.USER
        if workspace:
            error_msg += " in workspace " + workspace
        if error_data["error"]:
            error_msg += " : " + error_data["error"]
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)


def do_label(req_id, label):
    """Send the HTTP request (PUT) to change a label of a request."""
    url = settings.JDMA_API_URL + "migration?name=" + settings.USER
    if req_id != None:
        url += ";request_id=" + str(req_id)
    data = {}
    if label:
        data["label"] = label
    response = requests.put(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        pass
    else:
        # print the error
        error_data = response.json()
        error_msg = "** ERROR ** - cannot relabel request " + str(req_id)
        error_msg += " : " + error_data["error"]
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)


def main():
    # help string for the command parsing
    command_help = "Available commands are : \n" +\
                   "init  <email address>   : Initialize the transfer cache for your JASMIN login\n"+ \
                   "email <email address>   : Set / update email address\n" + \
                   "info                    : Get the user info\n"+\
                   "notify                  : Switch on / off email notifications of scheduled deletions (default is on)\n"+\
                   "request <request id>    : List all requests, or a particular request\n"+\
                   "put     <path>          : Migrate current directory or directory in <path>, with optional --label=\n"+\
                   "label   <request id>    : Change the label of a request"

    parser = argparse.ArgumentParser(prog="JDMA", formatter_class=argparse.RawTextHelpFormatter,
                                     description="JASMIN data migration app (JDMA) command line tool")
    parser.add_argument("cmd", choices=["init", "email", "info", "notify", "request", "put", "label"],
                        help=command_help, metavar="command")
    parser.add_argument("arg", help="Argument to the command", default="", nargs="?")
    parser.add_argument("--email", action="store", default="", help="Email address for user in the init and email commands.")
    parser.add_argument("--workspace", action="store", default="", help="Group workspace to use in the request.")
    parser.add_argument("--label", action="store", default="", help="Label to name the request.")

    args = parser.parse_args()

    # get the email address
    if args.cmd in ["init", "email"]:
        email = args.arg
        if args.email:
            email = args.email

    # get the workspace
    if args.workspace:
        workspace = args.workspace
    else:
        workspace = None

    # get the label if any
    if args.label:
        label = args.label
    else:
        label = None

    # switch on the commands
    if args.cmd == "init":
        do_init(email)
    elif args.cmd == "email":
        do_email(email)
    elif args.cmd == "info":
        do_info()
    elif args.cmd == "notify":
        do_notify()
    elif args.cmd == "request":
        if len(args.arg):
            do_request(int(args.arg), workspace)
        else:
            do_list_requests(workspace)
    elif args.cmd == "put":
        if len(args.arg):
            path = args.arg
        else:
            path = os.getcwd()
        do_put(path, workspace, label)
    elif args.cmd == "label":
        if len(args.arg):
            request_id = int(args.arg)
        else:
            request_id = None
        do_label(request_id, label)

if __name__ == "__main__":
    main()
