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
#    JDMA_SERVER_URL = "http://0.0.0.0:8001/jdma_control"  # location of the jdma_control server / app
    JDMA_SERVER_URL = "https://192.168.51.26/jdma_control"
    JDMA_API_URL = JDMA_SERVER_URL + "/api/v1/"
#    USER = os.environ["USER"] # the USER name
    USER = "rmillar"
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


def print_stack_trace(response_content):
    # extract the stacktrace from a Django response when the HTTP status code is 500
    lines = response_content.split("\n")
    print_line = False
    for line in lines:
        if line == "Traceback:":
            print_line = True
        elif "</textarea>" in line:
            print_line = False
        if print_line:
            print line


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
              "    Username : " + data["name"] + "\n" +\
              "    Email    : " + data["email"] + "\n")
    elif response.status_code != 500:
        # get the reason why it failed
        error = response.json()['error']
        user = response.json()['name']
        sys.stdout.write(bcolors.RED+\
              "** ERROR ** - cannot initialize user " + user + " : " + error + bcolors.ENDC + "\n")
    else:
        sys.stdout.write(bcolors.RED+\
              "** ERROR ** - cannot initialize user " + user + " : 500 " + bcolors.ENDC + "\n")
        print_stack_trace(response.content)


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
    request_types = ["PUT", "GET"]
    return request_types[req_type]


def get_request_stage(stage):
    request_stages = ["ON_DISK",            # 0  - Migration starts here
                      "PUT_PENDING",        # 1
                      "PUTTING",            # 2
                      "VERIFY_PENDING",     # 3
                      "VERIFY_GETTING",     # 4
                      "VERIFYING",          # 5
                      "ON_TAPE",            # 6
                      "FAILED",             # 7
                      "",                   # 8
                      "",                   # 9
                      "ON_TAPE",            # 10 - MigrationRequest starts here
                      "GET_PENDING",        # 11
                      "GETTING",            # 12
                      "ON_DISK",            # 13
                      "FAILED"]             # 14

    return request_stages[stage]


def get_permission(permission):
    # this is user permissions - private, group workspace or all
    permission_choices = ["PRIVATE",
                          "GROUP",
                          "ALL"]
    return permission_choices[permission]


def get_permissions_string(p):
    # this is unix permissions
    is_dir = 'd'
    dic = {'7':'rwx', '6' :'rw-', '5' : 'r-x', '4':'r--', '0': '---'}
    perm = oct(p)[-3:]
    return is_dir + ''.join(dic.get(x,x) for x in perm)


def do_request(req_id):
    """Send the HTTP request (GET) to get the details about a single request."""
    url = settings.JDMA_API_URL + "request?name=" + settings.USER
    if req_id != None:
        url += ";request_id=" + str(req_id)
    # send the request
    response = requests.get(url, verify=settings.VERIFY)
    # process if returned
    if response.status_code == 200:
        data = response.json()
        # print the response
        sys.stdout.write(bcolors.MAGENTA)
        sys.stdout.write("Request for user: " + data["user"] + "\n")
        sys.stdout.write(bcolors.ENDC)
        sys.stdout.write("    Request id   : " + str(data["request_id"])+"\n")
        sys.stdout.write("    Batch id     : " + str(data["migration_id"])+"\n")
        sys.stdout.write("    Workspace    : " + data["workspace"]+"\n")
        if "migration_label" in data:
            sys.stdout.write("    Batch label  : " + data["migration_label"]+"\n")
        if "date" in data:
            sys.stdout.write("    Request date : " + data["date"][0:16].replace("T"," ")+"\n")
        sys.stdout.write("    Request type : " + get_request_type(data["request_type"])+"\n")
        sys.stdout.write("    Stage        : " + get_request_stage(data["stage"])+"\n")
    elif response.status_code != 500:
        # get the reason why it failed
        data = response.json()
        error_msg = "** ERROR ** - cannot list request " + str(data["request_id"]) + " for user " + data["name"]
        error_msg += " : " + data["error"] + "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_stack_trace(response.content)


def do_list_requests():
    """Send the HTTP request (GET) to get the details about all of a user's requests"""
    url = settings.JDMA_API_URL + "request?name=" + settings.USER

    response = requests.get(url, verify=settings.VERIFY)
    if response.status_code == 200:
        # get the list of responses from the JSON
        data = response.json()
        n_req = len(data["requests"])
        if n_req == 0:
            error_msg = "** ERROR ** - No requests found for user " + settings.USER
            error_msg += "\n"
            sys.stdout.write(bcolors.RED + error_msg)
            sys.stdout.write(bcolors.ENDC)
        else:
            # print the header
            sys.stdout.write(bcolors.MAGENTA)
            print "{:>11} {:<6} {:<8} {:<16} {:16} {:<11} {:<16}".format("request id", "type", "batch id", "workspace", "batch label", "stage", "date")
            sys.stdout.write(bcolors.ENDC)
            for r in data["requests"]:
                print "{:>11} {:<6} {:<8} {:<16} {:16} {:<11} {:<16}".format(\
                    r["request_id"],
                    get_request_type(r["request_type"]),
                    r["migration_id"],
                    r["workspace"],
                    r["migration_label"][0:16],
                    get_request_stage(r["stage"]),
                    r["date"][0:16].replace("T"," "))
    elif response.status_code != 500:
        error_data = response.json()
        error_msg = "** ERROR ** - cannot list requests for user " + error_data["name"]
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_stack_trace(response.content)


def do_migration(batch_id, workspace=None):
    """Send the HTTP request (GET) to get the details of a single migration for the user.
    Optionally filter on the workspace."""
    # send the HTTP request
    url = settings.JDMA_API_URL + "migration?name=" + settings.USER
    if batch_id != None:
        url += ";migration_id=" + str(batch_id)
    if workspace != None:
        url += ";workspace=" + workspace

    response = requests.get(url, verify=settings.VERIFY)

    if response.status_code == 200:
        data = response.json()
        sys.stdout.write(bcolors.MAGENTA)
        sys.stdout.write("Batch for user: " + data["user"] + "\n")
        sys.stdout.write(bcolors.ENDC)
        sys.stdout.write("    Batch id     : " + str(data["migration_id"])+"\n")
        sys.stdout.write("    Workspace    : " + data["workspace"]+"\n")
        sys.stdout.write("    Label        : " + data["label"]+"\n")
        if "registered_date" in data:
            sys.stdout.write("    Date         : " + data["registered_date"][0:16].replace("T"," ")+"\n")
        if "permission" in data:
            sys.stdout.write("    Permission   : " + get_permission(data["permission"])+"\n")
        sys.stdout.write("    Stage        : " + get_request_stage(data["stage"])+"\n")
        if "et_id" in data:
            sys.stdout.write("    ET id        : " + str(data["et_id"])+"\n")
        sys.stdout.write("    Directory    : " + data["original_path"]+"\n")
        sys.stdout.write("    Unix uid     : " + data["unix_user_id"]+"\n")
        sys.stdout.write("    Unix gid     : " + data["unix_group_id"]+"\n")
        sys.stdout.write("    Unix filep   : " + get_permissions_string(data["unix_permission"])+"\n")
    elif response.status_code != 500:
        # get the reason why it failed
        data = response.json()
        error_msg = "** ERROR ** - cannot list batch " + str(data["migration_id"]) + " for user " + data["name"]
        if "workspace" in data:
            error_msg += " in workspace " + data["workspace"]
        error_msg += " : " + data["error"] + "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_stack_trace(response.content)


def do_list_migrations(workspace=None):
    """Send the HTTP request (GET) to get the details of all the users migrations.
    Optionally filter on the workspace."""

    # send the HTTP request
    url = settings.JDMA_API_URL + "migration?name=" + settings.USER
    if workspace != None:
        url += ";workspace=" + workspace
    response = requests.get(url, verify=settings.VERIFY)

    if response.status_code == 200:
        data = response.json()
        n_mig = len(data["migrations"])
        if n_mig == 0:
            error_msg = "** ERROR ** - No batches found for user " + settings.USER
            if workspace:
                error_msg += " in workspace " + workspace
            error_msg += "\n"
            sys.stdout.write(bcolors.RED + error_msg)
            sys.stdout.write(bcolors.ENDC)
        else:
            # print the header
            sys.stdout.write(bcolors.MAGENTA)
            print "{:>8} {:<16} {:16} {:<11} {:<16} {:<16}".format("batch id", "workspace", "batch label", "stage", "date", "permission")
            sys.stdout.write(bcolors.ENDC)
            for r in data["migrations"]:
                print "{:>8} {:<16} {:<16} {:11} {:<16} {:<16}".format(\
                    r["migration_id"],
                    r["workspace"][0:16],
                    r["label"][0:16],
                    get_request_stage(r["stage"]),
                    r["registered_date"][0:16].replace("T"," "),
                    get_permission(r["permission"]))
    elif response.status_code != 500:
        error_data = response.json()
        error_msg = "** ERROR ** - cannot list batches for user " + error_data["name"]
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_stack_trace(response.content)


def do_put(path, workspace, label):
    """Send the HTTP request (POST) to indicate a directory is to be migrated."""
    url = settings.JDMA_API_URL + "request"
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
                         "** SUCCESS ** - migration (PUT) requested:\n" + bcolors.ENDC)
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
    elif response.status_code != 500:
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
    else:
        print print_stack_trace(response.content)


def do_get(batch_id, target_dir):
    """Send the HTTP request (POST) to add a GET request to the MigrationRequests"""
    url = settings.JDMA_API_URL + "request"
    # set the user and request type data
    data = {"name" : settings.USER,
            "request_type" : "GET"}
    # add the path and workspace - if the workspace is none then don't add
    # in this case the HTTP API will return an error as a workspace is required
    if batch_id:
        data["migration_id"] = batch_id
    if target_dir:
        data["target_path"] = target_dir

    # do the request (POST)
    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        sys.stdout.write(bcolors.GREEN+\
                         "** SUCCESS ** - retrieval (GET) requested:\n"+bcolors.ENDC)
        sys.stdout.write("    Request id   : " + str(data["request_id"])+"\n")
        sys.stdout.write("    Batch id     : " + str(data["batch_id"])+"\n")
        sys.stdout.write("    Workspace    : " + data["workspace"]+"\n")
        sys.stdout.write("    Label        : " + data["label"]+"\n")
        sys.stdout.write("    Date         : " + data["registered_date"][0:16].replace("T"," ")+"\n")
        sys.stdout.write("    Request type : " + get_request_type(data["request_type"])+"\n")
        sys.stdout.write("    Stage        : " + get_request_stage(data["stage"])+"\n")
        sys.stdout.write("    Target       : " + data["target_path"]+"\n")

    elif response.status_code != 500:
        error_data = response.json()
        error_msg = "** ERROR ** - cannot retrieve (GET) migration"
        if error_data["migration_id"]:
            error_msg += " with batch id: " + str(error_data["migration_id"])
        if error_data["error"]:
            error_msg += ": " + str(error_data["error"])
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_stack_trace(response.content)


def do_label(batch_id, label):
    """Send the HTTP request (PUT) to change a label of a migration."""
    url = settings.JDMA_API_URL + "migration?name=" + settings.USER
    if batch_id != None:
        url += ";migration_id=" + str(batch_id)
    data = {}
    if label:
        data["label"] = label
    response = requests.put(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        sys.stdout.write(bcolors.GREEN+ \
                         "** SUCCESS ** - label changed to: " + bcolors.ENDC + label + "\n")
    elif response.status_code != 500:
        # print the error
        error_data = response.json()
        error_msg = "** ERROR ** - cannot relabel batch " + str(batch_id)
        error_msg += " : " + error_data["error"]
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_stack_trace(response.content)


def do_permission(batch_id, permission):
    """Send the HTTP request (PUT) to change the permission of a batch."""
    url = settings.JDMA_API_URL + "migration?name=" + settings.USER
    if batch_id != None:
        url += ";migration_id=" + str(batch_id)
    data = {}
    if permission:
        data["permission"] = permission
    response = requests.put(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        sys.stdout.write(bcolors.GREEN+ \
                         "** SUCCESS ** - permission changed to: " + bcolors.ENDC + permission + "\n")
    elif response.status_code != 500:
        # print the error
        error_data = response.json()
        error_msg = "** ERROR ** - cannot change permission of batch " + str(batch_id)
        error_msg += " : " + error_data["error"]
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_stack_trace(response.content)


def main():
    # help string for the command parsing
    command_help = "Available commands are : \n" +\
                   "init    <email address>  : Initialize the migration app for your JASMIN login\n"+ \
                   "email   <email address>  : Set / update email address\n" + \
                   "info                     : Get the user info\n"+\
                   "notify                   : Switch on / off email notifications of scheduled deletions (default is on)\n"+\
                   "request <request_id>     : List all requests, or a particular request\n"+\
                   "batch   <batch_id>       : List all batches, or a particular batch\n"+\
                   "put     <path>           : Create a batch upload of the current directory or directory in <path>,\n"+\
                   "                           with optional --label=\n"+\
                   "get     <batch_id>       : Retrieve a batch upload of a directory with the id <request_id>\n" +\
                   "                           Target directory can be specified with --target= \n" +\
                   "label   <batch_id>       : Change the label of a batch \n" +\
                   "permission <batch_id> <p>: Change the read permission for the batch, p=PRIVATE|GROUP|ALL"

    parser = argparse.ArgumentParser(prog="JDMA", formatter_class=argparse.RawTextHelpFormatter,
                                     description="JASMIN data migration app (JDMA) command line tool")
    parser.add_argument("cmd", choices=["init", "email", "info", "notify", "request", "batch", "put", "get", "label", "permission"],
                        help=command_help, metavar="command")
    parser.add_argument("arg", help="Argument to the command", default="", nargs="?")
    parser.add_argument("-e", "--email", action="store", default="", help="Email address for user in the init and email commands.")
    parser.add_argument("-p", "--permission", action="store", default="PRIVATE", help="Permission PRIVATE|GROUP|ALL.")
    parser.add_argument("-w", "--workspace", action="store", default="", help="Group workspace to use in the request.")
    parser.add_argument("-l", "--label", action="store", default="", help="Label to name the request.")
    parser.add_argument("-r", "--target", action="store", default="", help="Optional target directory for GET.")

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

    # get the target directory if any
    if args.target:
        target_dir = args.target
    else:
        target_dir = None

    # get the permission if any
    if args.permission:
        permission = args.permission
    else:
        permission = None

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
            do_request(int(args.arg))
        else:
            do_list_requests()
    elif args.cmd == "batch":
        if len(args.arg):
            do_migration(int(args.arg), workspace)
        else:
            do_list_migrations(workspace)
    elif args.cmd == "put":
        if len(args.arg):
            path = args.arg
        else:
            path = os.getcwd()
        do_put(path, workspace, label)
    elif args.cmd == "get":
        if len(args.arg):
            request_id = int(args.arg)
        else:
            request_id = None
        do_get(request_id, target_dir)
    elif args.cmd == "label":
        if len(args.arg):
            request_id = int(args.arg)
        else:
            request_id = None
        do_label(request_id, label)
    elif args.cmd == "permission":
        if len(args.arg):
            request_id = int(args.arg)
        else:
            request_id = None
        do_permission(request_id, permission)

if __name__ == "__main__":
    main()
