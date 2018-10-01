#! /usr/bin/env python
"""Command line tool for interacting with the JASMIN data migration app (JDMA)
for users who are logged into JASMIN and have full JASMIN accounts."""

# Author : Neil R Massey
# Date   : 28/07/2017

import sys
import os
import argparse
import requests
import json
import math

# switch off warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class settings:
    """Settings for the xfc command line tool."""
    # location of the jdma_control server / app
    JDMA_SERVER_URL = "https://jdma-test.ceda.ac.uk/jdma_control"
#    JDMA_SERVER_URL = "https://172.16.149.183/jdma_control"
    JDMA_API_URL = JDMA_SERVER_URL + "/api/v1/"
    # get the user from the environment
    USER = os.environ["USER"] # the USER name
    # version of this software
    VERSION = "0.1"
    VERIFY = False
    user_credentials = {}
    DEBUG = True


unit_list = list(zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB'],
                     [0, 0, 1, 1, 1, 1, 1]))


def sizeof_fmt(num):
    """Human friendly file size"""
    if num > 1:
        exponent = min(int(math.log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:>5.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    elif num == 1:
        return '1 byte'
    else:
        return '0 bytes'

def output_json(json):
    # output json to the command line in a format that can be read by jq
    json_string = str(json)
    json_string2 = json_string.replace("'", '"').replace('u"', '"')
    print(json_string2)

class bcolors:
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    INVERT = '\033[7m'
    ENDC = '\033[0m'


def user_not_initialized_message():
    sys.stdout.write((
        "{} ** ERROR ** - User {} not initialised yet. {}Run {}jdma.py "
        "init {}first.\n"
    ).format(bcolors.RED, settings.USER, bcolors.ENDC, bcolors.YELLOW,
             bcolors.ENDC))


def print_response_error(response):
    ("""Print a concise summary of the error, rather than a whole output of
       html
    """)
    display=False
    response_str = response.content.decode('utf-8')
    for il in response_str.split("\n"):
        if il == "Traceback:":
            display=True
        if display:
            print(il)
            if il == "</div>":
                display=False


def do_help(args):
    """help <command> : get help for a command"""
    if len(args.arg):
        method = globals().get("do_" + args.arg)
        if method != None:
            print(bcolors.YELLOW + method.__doc__ + bcolors.ENDC)
        else:
            print((
                "{}help: {} invalid choice of command.{}"
            ).format(bcolors.YELLOW, args.arg, bcolors.ENDC))
    else:
        print((
            "{}help: supply command to seek help on.{}"
        ).format(bcolors.YELLOW, bcolors.ENDC))
        # get a list of the commands
        cmds = []
        for function in globals():
            if function[0:3] == "do_" and function != "do_help":
                cmds.append(function[3:])
        cmds.sort()
        print("Available commands are:")
        for cmd in cmds:
            print ("\t" + cmd)


def error_message(response, message, output_json):
    # get the reason why it failed
    user = settings.USER
    error = ""
    try:
        json_response = response.json()
        if 'error' in json_response:
            error = json_response['error']
        if 'name' in json_response:
            user = json_response['name']
        if output_json == True:
            output_json(json_response)
            return
    except:
        try:
            error = str(response.status_code)
        except:
            error = ""
    out_message = "{}** ERROR ** - {} {}"
    if error != "":
        out_message += " : {}{}\n"
    else:
        out_message += "{}{}\n"
    sys.stdout.write((out_message
    ).format(bcolors.RED, message, user, error, bcolors.ENDC))
    if settings.DEBUG and response is not None:
        print_response_error(response)


def do_init(args):
    ("""init <email address> : Initialise the JASMIN Data Migration App for """
     """your JASMIN login.""")
    ### Send the HTTP request (POST) to initialise a user.###
    # get the email from the args
    email = args.arg
    if args.email:
        email = args.email
    url = settings.JDMA_API_URL + "user"
    data = {"name" : settings.USER}
    if email != "":
        data["email"] = email
    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)
    # check the response code
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        sys.stdout.write((
              "{}** SUCCESS ** - user initiliazed with{}:\n"
              "    Username : {}\n"
              "    Email    : {}\n"
        ).format(bcolors.GREEN, bcolors.ENDC, data["name"], data["email"]))
    else:
        error_message(response, "cannot initialise user", args.json)


def do_email(args):
    ("""email <email address> : Set / update your email address for """
     """notifications.""")
    ### Send the HTTP request (PUT) to update the email address of the user by
    ### sending a PUT request.###
    # get the email from the args
    email = args.arg
    if args.email:
        email = args.email
    url = settings.JDMA_API_URL + "user?name=" + settings.USER
    data = {"name" : settings.USER}
    data["email"] = email
    response = requests.put(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        sys.stdout.write((
            "{}** SUCCESS ** - user email updated to: {}{}\n"
        ).format(bcolors.GREEN, data["email"], bcolors.ENDC))
    else:
        error_message(response, "cannot update email for user", args.json)


def do_info(args):
    ("""info : get information about you, including email address and """
     """notification setting.""")
    ###Send the HTTP request (GET) to return information about the user###
    url = settings.JDMA_API_URL + "user?name=" + settings.USER
    data = {"name" : settings.USER}
    response = requests.get(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        sys.stdout.write((
            "{}** SUCCESS ** - user info:\n{}"
            "    username: {}\n"
            "    email   : {}\n"
            "    notify  : {}\n"
        ).format(bcolors.GREEN,  bcolors.ENDC, data["name"], data["email"],
                 ["off", "on"][data["notify"]]))
    else:
        error_message(response, "cannot get info for user", args.json)


def do_notify(args):
    ("""notify : Switch on / off email notifications of the completion of """
     """GET | PUT | MIGRATE requests.  Default is on.""")
    ### Send the HTTP request (PUT) to switch on / off notifications for the
    ### user ###
    # first get the status of notifications
    url = settings.JDMA_API_URL + "user?name=" + settings.USER
    response = requests.get(url, verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        notify = data["notify"]
        # update to inverse
        put_data = {"name" : settings.USER,
                    "notify": not notify}
        response = requests.put(url, data=json.dumps(put_data),
                                verify=settings.VERIFY)
        if response.status_code == 200:
            sys.stdout.write((
                "{}** SUCCESS ** - user notifications updated to: {}{}\n"
            ).format(bcolors.GREEN, ["off", "on"][put_data["notify"]],
                     bcolors.ENDC))
        else:
            error_message(response, "cannot update notify for user", args.json)
    else:
        error_message(response, "cannot update notify for user", args.json)


def get_request_type(req_type):
    ("""Get a string from a request type integer.  See """
     """jdma_control.models.MigrationRequest for details""")
    request_types = ["PUT", "GET", "MIGRATE", "DELETE"]
    return request_types[req_type]


def get_request_stage(stage):
    request_stages = {
          0 : 'PUT_START',
          1 : 'PUT_PENDING',
          2 : 'PUT_PACK',
          3 : 'PUTTING',
          4 : 'VERIFY_PENDING',
          5 : 'VERIFY_GETTING',
          6 : 'VERIFYING',
          7 : 'PUT_TIDY',
          8 : 'PUT_COMPLETED',
        100 : 'GET_START',
        101 : 'GET_PENDING',
        102 : 'GETTING',
        103 : 'GET_UNPACK',
        104 : 'GET_RESTORE',
        105 : 'GET_TIDY',
        106 : 'GET_COMPLETED',
        200 : 'DELETE_START',
        201 : 'DELETE_PENDING',
        202 : 'DELETING',
        203 : 'DELETE_TIDY',
        204 : 'DELETE_COMPLETED',
       1000 : 'FAILED'
    }

    return request_stages[stage]


def get_batch_stage(stage):
    batch_stages = {
        0 : 'ON_DISK',
        1 : 'PUTTING',
        2 : 'ON_STORAGE',
        3 : 'FAILED'
    }
    return batch_stages[stage]

def get_permissions_string(p):
    # this is unix permissions
    is_dir = 'd'
    dic = {'7':'rwx', '6' :'rw-', '5' : 'r-x', '4':'r--', '0': '---'}
    perm = oct(p)[-3:]
    return is_dir + ''.join(dic.get(x,x) for x in perm)


def do_request(args):
    ("""request <request_id> : List all requests, or the details of a """
     """particular request with <request_id>.""")
    ###Send the HTTP request (GET) to get the details about a single request.
    # determine whether to list one request or all
    if len(args.arg):
        req_id = int(args.arg)
    else:
        list_requests(args)
        return

    url = settings.JDMA_API_URL + "request?name=" + settings.USER
    if req_id != None:
        url += ";request_id=" + str(req_id)
    # send the request
    response = requests.get(url, verify=settings.VERIFY)
    # process if returned
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        # print the response
        sys.stdout.write(bcolors.MAGENTA)
        sys.stdout.write("Request for user: {}\n".format(data["user"]))
        sys.stdout.write(bcolors.ENDC)
        sys.stdout.write((
            "    Request id   : {}\n"
        ).format(str(data["request_id"])))
        sys.stdout.write((
            "    Request type : {}\n"
        ).format(get_request_type(data["request_type"])))
        sys.stdout.write((
            "    Batch id     : {}\n"
        ).format(str(data["migration_id"])))
        sys.stdout.write("    Workspace    : {}\n".format(data["workspace"]))
        if "migration_label" in data:
            sys.stdout.write((
                "    Batch label  : {}\n"
            ).format(data["migration_label"]))
        if "storage" in data:
            sys.stdout.write("    Ex. storage  : {}\n".format(data["storage"]))
        if "date" in data:
            sys.stdout.write((
                "    Request date : {}\n"
            ).format(data["date"][0:16].replace("T"," ")))
        sys.stdout.write((
            "    Stage        : {}\n"
        ).format(get_request_stage(data["stage"])))
        if "failure_reason" in data:
            sys.stdout.write((
                "    Fail reason  : {}\n"
            ).format(data["failure_reason"]))
    elif response.status_code < 500:
        # get the reason why it failed
        message = "cannot list request {} for user".format(req_id)
        error_message(response, message, args.json)


def list_requests(args):
    ("""Called from do_requests if request_id is None.  Lists all the """
     """requests.""")
    url = settings.JDMA_API_URL + "request?name=" + settings.USER

    response = requests.get(url, verify=settings.VERIFY)
    if response.status_code == 200:
        # get the list of responses from the JSON
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        n_req = len(data["requests"])
        if n_req == 0:
            error_message(None, "no requests found for user", args.json)
        else:
            # print the header
            sys.stdout.write(bcolors.MAGENTA)
            sys.stdout.write((
                "{:>6} {:<8} {:<8} {:<16} {:16} {:<16} {:<17} {:<11}\n"
            ).format("req id", "type", "batch id", "workspace",
                     "batch label", "storage", "date", "stage"))
            sys.stdout.write(bcolors.ENDC)
            for r in data["requests"]:
                sys.stdout.write((
                    "{:>6} {:<8} {:<8} {:<16} {:16} {:<16} {:<17} {:<11}"
                ).format(
                    r["request_id"],
                    get_request_type(r["request_type"]),
                    r["migration_id"],
                    r["workspace"],
                    r["migration_label"][0:16],
                    r["storage"][0:16],
                    r["date"][0:16].replace("T"," "),
                    get_request_stage(r["stage"]))+"\n"
                )
    else:
        error_message(response, "cannot list requests for user", args.json)


def do_batch(args):
    ("""batch <batch_id> : List all batches, or all the details of a """
     """particular batch with <batch_id>.""")
    ### Send the HTTP request (GET) to get the details of a single migration
    ### for the user.
    ### Optionally filter on the workspace.
    # get the workspace from the arguments, or from the config file
    if args.workspace == "default":
        try:
            workspace = settings.user_credentials["default_gws"]
        except:
            workspace = None
    else:
        workspace = args.workspace
    # determine whether we should list one batch or many
    if len(args.arg):
        batch_id = int(args.arg)
    else:
        list_batches(workspace, args)
        return

    # send the HTTP request
    url = settings.JDMA_API_URL + "migration?name=" + settings.USER
    if batch_id != None:
        url += ";migration_id=" + str(batch_id)
    if workspace != None:
        url += ";workspace=" + workspace

    response = requests.get(url, verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        # check if the JSON option was chosen
        if args.json == True:
            print(data)
            return
        sys.stdout.write(bcolors.MAGENTA)
        sys.stdout.write("Batch for user: {}\n".format(data["user"]))
        sys.stdout.write(bcolors.ENDC)
        sys.stdout.write((
            "    Batch id     : {}\n"
        ).format(str(data["migration_id"])))
        sys.stdout.write((
            "    Workspace    : {}\n"
        ).format(data["workspace"]))
        sys.stdout.write((
            "    Batch label  : {}\n"
        ).format(data["label"]))
        if "storage" in data:
            sys.stdout.write((
                "    Ex. storage  : {}\n"
            ).format(data["storage"]))
        if "registered_date" in data:
            sys.stdout.write((
                "    Date         : {}\n"
            ).format(data["registered_date"][0:16].replace("T"," ")))
        if "external_id" in data:
            sys.stdout.write(("    External id  : {}\n"
        ).format(str(data["external_id"])))
        if "filelist" in data and len(data["filelist"]) > 0:
            sys.stdout.write((
                "    Filelist     : {}...\n"
            ).format(data["filelist"][0]))
        sys.stdout.write((
            "    Stage        : {}\n"
        ).format(get_batch_stage(data["stage"])))
        if "failure_reason" in data:
            sys.stdout.write((
                "    Fail reason  : {}\n"
            ).format(data["failure_reason"]))
        return True

    else:
        error_msg = ("cannot list batch {}").format(str(batch_id))
        if workspace != None:
            error_msg += " in workspace " + workspace
        error_msg += " for user"
        error_message(response, error_msg, args.json)
        return False


def list_batches(workspace=None, args=None):
    ("""Called from do_batch when batch_id == None.  Lists all batches=.""")
    ### Send the HTTP request (GET) to get the details of all the user's
    ### migrations.  Optionally filter on the workspace."""

    # send the HTTP request
    url = settings.JDMA_API_URL + "migration?name=" + settings.USER
    if workspace != None:
        url += ";workspace=" + workspace
    response = requests.get(url, verify=settings.VERIFY)

    if response.status_code == 200:
        data = response.json()
        if args is not None and args.json == True:
            output_json(data)
            return
        n_mig = len(data["migrations"])
        if n_mig == 0:
            error_msg = (
                "{}** ERROR ** - No batches found for user {}"
            ).format(bcolors.RED, settings.USER)
            if workspace:
                error_msg += " in workspace " + workspace
            error_msg += bcolors.ENDC + "\n"
            sys.stdout.write(error_msg)
        else:
            # print the header
            sys.stdout.write(bcolors.MAGENTA)
            sys.stdout.write((
                "{:>8} {:<16} {:<16} {:<16} {:<17} {:<11}\n"
            ).format("batch id", "workspace", "batch label",
                     "storage", "date", "stage"))
            sys.stdout.write(bcolors.ENDC)
            for r in data["migrations"]:
                sys.stdout.write((
                    "{:>8} {:<16} {:<16} {:<16} {:<17} {:<11}\n"
                ).format(
                    r["migration_id"],
                    r["workspace"][0:16],
                    r["label"][0:16],
                    r["storage"][0:16],
                    r["registered_date"][0:16].replace("T"," "),
                    get_batch_stage(r["stage"]))
                )
    else:
        error_message(response, "cannot list batches for user", args.json)


def add_credentials(args, data):
    if args.storage:
        # check whether there is a default storage backend and read it from the
        # credentials file if there is
        if args.storage == "default":
            try:
                storage = settings.user_credentials['default_storage']
            except:
                # the default default is elastictape
                storage = "elastictape"
        else:
            storage = args.storage
        # add to JSON data
        data["storage"] = storage
        # read the credentials for this backend from the ~/.jdma.json file and
        # add them to the request if there are no credentials in ~/.jdma.json
        # for this backend then add nothing if the backend is expecting
        # credentials and none are supplied then the server will return an error
        try:
            data["credentials"] = settings.user_credentials['storage'][storage]['required_credentials']
        except:
            # don't add any credentials
            pass


def read_filelist(path):
    filelist = []
    fh = open(path)
    flist = fh.read()
    # split the file and add to the data as "filelist" - add the absolute
    # paths, though
    flist_split = flist.split()
    flist_split = map(str.strip, flist_split)

    filelist = []
    for f in flist_split:
        filelist.append(f)
    fh.close()
    if len(filelist) == 0:
        raise Exception("Filelist {} has no files".format(path))
    return filelist


def migrate_or_put(args, request_type):
    ###Send the HTTP request (POST) to indicate a directory is to be migrated.
    ###
    # get the path, workspace and label (if any) from the args
    assert(request_type == "PUT" or request_type == "MIGRATE")
    url = settings.JDMA_API_URL + "request"
    # set the user and request type data
    data = {"name" : settings.USER,
            "request_type" : request_type}

    # get absolute path of filelist or directory (we don't know what it is yet)
    current_path = os.path.abspath(args.arg)

    # is this a directory?
    if os.path.isdir(current_path):
        data["filelist"] = [current_path]
    # does the filelist exist?
    elif os.path.exists(current_path):
        # read the filelist in and add it to the data
        data["filelist"] = read_filelist(current_path)
        # set the label to (the non absolute path of) the filelist - this may
        # be overriden later if args.label is not None
        data["label"] = args.arg
    # file or directory not found
    else:
        error_msg = "directory or filelist not found: {} for user".format(args.arg)
        error_message(None, error_msg, args.json)
        sys.exit()

    # Add the workspace - if the workspace is the default then try to add
    # the default workspace.  If this fails then don't add the workspace as,
    # in this case the HTTP API will return an error as a workspace is required
    if args.workspace == "default":
        try:
            workspace = settings.user_credentials["default_gws"]
        except:
            workspace = None
    else:
        workspace = args.workspace
    data["workspace"] = workspace

    if args.label:
        data["label"] = args.label

    # add the credentials to the request
    add_credentials(args, data)

    # do the request (POST)
    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        sys.stdout.write((
            "{}** SUCCESS ** - batch ({}) requested:\n{}"
        ).format(bcolors.GREEN, request_type, bcolors.ENDC))
        sys.stdout.write((
            "    Request id   : {}\n"
        ).format(str(data["request_id"])))
        sys.stdout.write((
            "    Request type : {}\n"
        ).format(get_request_type(data["request_type"])))
        sys.stdout.write((
            "    Batch id     : {}\n"
        ).format(str(data["batch_id"])))
        sys.stdout.write((
            "    Workspace    : {}\n"
        ).format(data["workspace"]))
        sys.stdout.write((
            "    Label        : {}\n"
        ).format(data["label"]))
        sys.stdout.write((
            "    Date         : {}\n"
        ).format(data["registered_date"][0:16].replace("T"," ")))
        sys.stdout.write((
            "    Ex. storage  : {}\n"
        ).format(data["storage"]))
        sys.stdout.write((
            "    Stage        : {}\n"
        ).format(get_request_stage(data["stage"])))
        if len(data["filelist"]) > 0:
            flist_display = data["filelist"][0] + "..."
        else:
            flist_display = current_path
            sys.stdout.write((
                "    Filelist     : {}\n"
            ).format(flist_display))
    else:
        # print the error
        error_data = response.json()
        # get the filelist name
        if "filelist" in error_data and len(error_data["filelist"]) > 0:
            filelist = error_data["filelist"][0]
        else:
            filelist = current_path
        error_msg = (
            "cannot {} filelist {}..."
        ).format(request_type, filelist)
        if "workspace" in error_data:
            error_msg += " in workspace " + error_data["workspace"]
        error_msg += " for user"
        error_message(response, error_msg, args.json)


def do_put(args):
    ("""put <path>|<filelist>: Create a batch upload of the current """
     """directory, or directory in <path> or a list of files.\nUse --label= """
     """to give the batch a label.\nUse --storage to specify which external """
     """storage to target for the migration.  Use command storage to """
     """list all the available storage targets.""")
    migrate_or_put(args, "PUT")


def do_migrate(args):
    ("""migrate <path>|<filelist>: Create a batch upload of the current """
     """directory, or directory in <path> or a list of files.\nUse --label= """
     """to give the batch a label.\nUse --storage to specify which external """
     """storage to target for the migration.\nUse command storage to """
     """list all the available storage targets.\nThe data in the directory """
     """or filelist will be deleted after the upload is completed.""")
    migrate_or_put(args, "MIGRATE")

def do_delete(args):
    ("""delete <batch_id> : Delete the batch with <batch_id> from the storage""")
    ### Send the HTTP request (POST) to add a DELETE request to the
    ### MigrationRequests###

    # get the batch id
    if len(args.arg):
        batch_id = int(args.arg)
    else:
        batch_id = None

    if args.force == True:
        force = True
    else:
        force = False
    # don't prompt if force flag set
    if not force:
        # Print a warning message! and the batch info:
        warning_message = "** WARNING ** - this will delete the following batch: \n"
        sys.stdout.write(bcolors.RED + warning_message + bcolors.ENDC)
        if do_batch(args):
            prompt_message = "Do you wish to continue? [y/N] "
            # prompt user to confirm
            sys.stdout.write(bcolors.RED + prompt_message)
            answer = input()
            sys.stdout.write(bcolors.ENDC)
            if answer != "y" and answer != "Y":
                return # do nothing

    # use the same POST URL as GET and PUT
    url = settings.JDMA_API_URL + "request"
    # set the user and request type data
    data = {"name" : settings.USER,
            "request_type" : "DELETE"}
    if batch_id:
        data["migration_id"] = batch_id

    # add the credentials to the request
    add_credentials(args, data)

    # do the request (POST)
    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return

        sys.stdout.write((
            "{}** SUCCESS ** - removal (DELETE) requested:{}\n"
        ).format(bcolors.GREEN, bcolors.ENDC))
        sys.stdout.write((
            "    Request id   : {}\n"
        ).format(str(data["request_id"])))
        sys.stdout.write((
            "    Batch id     : {}\n"
        ).format(str(data["batch_id"])))
        sys.stdout.write((
            "    Workspace    : {}\n"
        ).format(data["workspace"]))
        sys.stdout.write((
            "    Label        : {}\n"
        ).format(data["label"]))
        sys.stdout.write((
            "    Date         : {}\n"
        ).format(data["registered_date"][0:16].replace("T"," ")))
        sys.stdout.write((
            "    Request type : {}\n"
        ).format(get_request_type(data["request_type"])))
        sys.stdout.write((
            "    Stage        : {}\n"
        ).format(get_request_stage(data["stage"])))

    else:
        error_msg = "cannot remove (DELETE) batch {} for user".format(batch_id)
        error_message(response, error_msg, args.json)

def do_get(args):
    ("""get <batch_id> : Retrieve a batch upload of a directory or filelist """
     """with the id <request_id>.\nA different target directory to the """
     """original directory can be specified with --target=. """
     """\nget <batch_id> <filelist> : Retrieve a (subset) list of files """
     """from a batch with <batch_id>.\n<filelist> is the name of a file """
     """containing a list of filenames to retrieve.\nThe filenames in the """
     """filelist must be the relative path, as obtained by """
     """--simple files <batch_id>."""
    )
    ### Send the HTTP request (POST) to add a GET request to the
    ### MigrationRequests###
    # get the batch id
    if len(args.arg):
        batch_id = int(args.arg)
    else:
        batch_id = None

    if len(args.opts):
        filelist = args.opts
    else:
        filelist = None
    # get the target directory if any
    if args.target:
        target_dir = os.path.abspath(args.target)
    else:
        target_dir = None

    url = settings.JDMA_API_URL + "request"
    # set the user and request type data
    data = {"name" : settings.USER,
            "request_type" : "GET"}
    # add the migration_id and target_path if either have been given in the
    # command line
    # in this case the HTTP API will return an error as the migration_id and
    # target_path are both required
    if batch_id:
        data["migration_id"] = batch_id
    if target_dir:
        data["target_path"] = target_dir
    if filelist:
        data["filelist"] = read_filelist(filelist)
    # add the credentials to the request
    add_credentials(args, data)

    # do the request (POST)
    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return

        sys.stdout.write((
            "{}** SUCCESS ** - retrieval (GET) requested:{}\n"
        ).format(bcolors.GREEN, bcolors.ENDC))
        sys.stdout.write((
            "    Request id   : {}\n"
        ).format(str(data["request_id"])))
        sys.stdout.write((
            "    Batch id     : {}\n"
        ).format(str(data["batch_id"])))
        sys.stdout.write((
            "    Workspace    : {}\n"
        ).format(data["workspace"]))
        sys.stdout.write((
            "    Label        : {}\n"
        ).format(data["label"]))
        sys.stdout.write((
            "    Date         : {}\n"
        ).format(data["registered_date"][0:16].replace("T"," ")))
        sys.stdout.write((
            "    Request type : {}\n"
        ).format(get_request_type(data["request_type"])))
        sys.stdout.write((
            "    Stage        : {}\n"
        ).format(get_request_stage(data["stage"])))
        sys.stdout.write((
            "    Target       : {}\n"
        ).format(data["target_path"]))
        if (data["filelist"]):
            sys.stdout.write((
                "    Filelist     : {}...\n"
            ).format(data["filelist"][0]))

    else:
        error_data = response.json()
        error_msg = "cannot retrieve (GET) batch"
        if "migration_id" in error_data:
            error_msg += " with id " + str(error_data["migration_id"])
        error_msg += " for user"
        error_message(response, error_msg, args.json)


def do_storage(args):
    ("""storage : list the storage targets that batches can be written to.""")
    url = settings.JDMA_API_URL + "list_backends"
    response = requests.get(url, verify=settings.VERIFY)
    storage = {}
    if response.status_code == 200:
        # parse the JSON that comes back
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        for r in range(0, len(data)):
            k = list(data)
            storage[k[r]] = data[k[r]]

    else:
        error_msg = "cannot list storage"
        error_message(response, error_msg, args.json)
        return

    if storage != {}:
        sys.stdout.write(bcolors.MAGENTA)
        sys.stdout.write("{:>4} {:<24} {:16}\n".format("", "Name", "Short ID"))
        sys.stdout.write(bcolors.ENDC)
        r = 0
        for k in storage:
            sys.stdout.write("{:>4} {:<24} {:16}\n".format(r, storage[k], k))
            r+=1
        sys.stdout.write(bcolors.ENDC)


def do_files(args):
    ("""files <batch_id> : List the original paths of files in a batch.\n"""
     """Use --simple option to produce a simply formatted list which can be """
     """used in conjunction with the get command to get a subset of the batch.""")
    ###Send the HTTP request (GET) to list the files in a Migration###
    # get the batch id if any
    if len(args.arg):
        batch_id = int(args.arg)
    else:
        batch_id = None

    if args.workspace == "default":
        try:
            workspace = settings.user_credentials["default_gws"]
        except:
            workspace = None
    else:
        workspace = args.workspace

    if args.limit:
        limit = args.limit
    else:
        limit = 0

    url = settings.JDMA_API_URL + "file?name=" + settings.USER
    if batch_id:
        url += ";migration_id=" + str(batch_id)
    if workspace:
        url += ";workspace=" + workspace

    # add the limit (the number of files output)
    url += ";limit=" + str(limit)
    # add whether to list the digest or not
    if args.digest == True:
        url += ";digest=1"
    # do the request (POST)
    response = requests.get(url, verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        n_mig = len(data["migrations"])
        if n_mig == 0:
            error_msg = (
                "{}** ERROR ** - No files found for user {}"
            ).format(bcolors.RED, settings.USER)
            if batch_id:
                error_msg += " for batch " + str(batch_id)
            if workspace:
                error_msg += " in workspace " + workspace
            error_msg += bcolors.ENDC + "\n"
            sys.stdout.write(error_msg)
        else:
            if args.simple != True:
                # print the header
                sys.stdout.write(bcolors.MAGENTA)
                sys.stdout.write((
                    "{:>5} {:<12} {:<12} {:<12} {:<18} {:<64} {:>8}"
                ).format("b.id", "workspace", "batch label",
                         "storage", "archive", "file", "size"))
                if args.digest == True:
                    sys.stdout.write((" {:<64}").format("digest"))
                sys.stdout.write("\n"+bcolors.ENDC)
            for r in data["migrations"]:
                # print the migration details and the first archive details
                n_a = len(r["archives"])
                if n_a == 0:
                    continue
                c_a = 0
                for a in r["archives"]:
                    n_f = len(a["files"])
                    c_f = 0
                    for f in a["files"]:
                        if args.simple == True:
                            sys.stdout.write("{}\n".format(f["path"]))
                            continue
                        fname = f["path"][-64:]
                        size = sizeof_fmt(f["size"])[0:8]
                        # fancy underlining?
                        if c_f == n_f-1 and c_a == n_a-1:
                            sys.stdout.write(bcolors.UNDERLINE)
                        if n_f > 1 and c_f == n_f-1:
                            ULA = bcolors.UNDERLINE
                        else:
                            ULA = ""
                        # determine what to print out
                        if c_a == 0 and c_f == 0:
                            M = r["migration_id"]
                            W = r["workspace"][0:12]
                            L = r["label"][0:12]
                            S = r["storage"][0:12]
                        else:
                            M = ""
                            W = ""
                            L = ""
                            S = ""
                        if c_f == 0:
                            A = a["archive_id"][0:20]
                        else:
                            A = ""

                        sys.stdout.write((
                            "{:>5} {:<12} {:<12} {:<12}" + ULA + " {:<18} {:<64} {:>8}"
                        ).format(M, W, L, S, A,
                                 fname,
                                 size))
                        if args.digest == True:
                            digest = f["digest"]
                            sys.stdout.write((" {:<64}").format(digest))
                        sys.stdout.write(bcolors.ENDC+"\n")
                        c_f += 1
                    c_a += 1

    else:
        error_msg = "cannot list files"
        error_message(response, error_msg, args.json)


def do_archives(args):
    ("""archives <batch_id> : List the original paths of archives in a batch."""
    )
    ###Send the HTTP request (GET) to list the archives in a Migration###
    # get the batch id if any
    if len(args.arg):
        batch_id = int(args.arg)
    else:
        batch_id = None

    if args.workspace == "default":
        try:
            workspace = settings.user_credentials["default_gws"]
        except:
            workspace = None
    else:
        workspace = args.workspace

    if args.limit:
        limit = args.limit
    else:
        limit = 0

    url = settings.JDMA_API_URL + "archive?name=" + settings.USER
    if batch_id:
        url += ";migration_id=" + str(batch_id)
    if workspace:
        url += ";workspace=" + workspace

    # add the limit (the number of files output)
    url += ";limit=" + str(limit)
    # add whether to list the digest or not
    if args.digest == True:
        url += ";digest=1"
    # do the request (POST)
    response = requests.get(url, verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        n_mig = len(data["migrations"])
        if n_mig == 0:
            error_msg = "no archives found"
            if batch_id:
                error_msg += " for batch " + str(batch_id)
            if workspace:
                error_msg += " in workspace " + workspace
            error_msg += " for user"
            error_message(response, error_msg, args.json)
        else:
            # print the header
            sys.stdout.write(bcolors.MAGENTA)
            sys.stdout.write((
                "{:>5} {:<12} {:<12} {:<12} {:<18} {:>8}"
            ).format("b.id", "workspace", "batch label",
                     "storage", "archive", "size"))
            if args.digest == True:
                sys.stdout.write((" {:<32}").format("digest"))
            sys.stdout.write("\n"+bcolors.ENDC)
            for r in data["migrations"]:
                # print the migration details and the first archive details
                a = r["archives"][0]
                sys.stdout.write((
                    "{:>5} {:<12} {:<12} {:<12} {:<18} {:>8}"
                ).format(r["migration_id"],
                         r["workspace"][0:12],
                         r["label"][0:12],
                         r["storage"][0:12],
                         a["archive_id"][0:20],
                         sizeof_fmt(a["size"])))
                if args.digest == True:
                    sys.stdout.write((" {:<32}").format(a["digest"]))
                sys.stdout.write("\n")
                # underline the last one
                ac = 1
                for a in r["archives"][1:]:
                    if ac == len(r["archives"])-1:
                        sys.stdout.write(bcolors.UNDERLINE)
                    sys.stdout.write((
                        "{:>5} {:<12} {:<12} {:<12} {:<18} {:>8}"
                    ).format("","","", "",
                         a["archive_id"][0:20],
                         sizeof_fmt(a["size"])))
                    if args.digest == True:
                        sys.stdout.write((" {:<32}").format(a["digest"]))
                    sys.stdout.write("\n"+bcolors.ENDC)
                    ac += 1

    else:
        error_msg = "cannot list archives"
        error_message(response, error_msg, args.json)


def do_label(args):
    ("""label <batch_id> : Change the label of the batch with <batch_id>."""
    )
    ###Send the HTTP request (PUT) to change a label of a migration.###
    # get batch id if any
    if len(args.arg):
        batch_id = int(args.arg)
    else:
        batch_id = None

    # get label
    if args.label:
        label = args.label
    else:
        label = None

    url = settings.JDMA_API_URL + "migration/?name=" + settings.USER
    if batch_id != None:
        url += ";migration_id=" + str(batch_id)
    data = {}
    if label:
        data["label"] = label
    response = requests.put(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        if args.json == True:
            output_json(response.json)
            return
        sys.stdout.write((
            "{}** SUCCESS ** - label of batch {} changed to: {}{}\n"
        ).format(bcolors.GREEN, str(batch_id), label, bcolors.ENDC))
    else:
        error_msg = "cannot relabel batch {} for user".format(batch_id)
        error_message(response, error_msg, args.json)


def read_credentials_file():
    ("""Read in the credentials file.  It is JSON formatted"""
    )
    # path is in user directory
    user_home = os.environ["HOME"]

    # add the config file name
    jdma_user_config_filename = user_home + "/" + ".jdma.json"

    # open the file
    try:
        fp = open(jdma_user_config_filename)
        # deserialize from the JSON
        jdma_user_credentials = json.load(fp)
        # close the config file
        fp.close()
    except IOError:
        sys.stdout.write((
            "{}** ERROR ** - User credentials file does not exist "
            "with path: {}{}\n"
        ).format(bcolors.RED, jdma_user_config_filename, bcolors.ENDC))
        sys.exit(1)
    except Exception:
        sys.stdout.write((
            "{}** ERROR ** - Error in credentials file at: {}{}\n"
        ).format(bcolors.RED, jdma_user_config_filename, bcolors.ENDC))
        sys.exit(1)

    return jdma_user_credentials


def main():
    command_help = "Type help <command> to get help on a specific command"
    command_choices = ["init", "email", "info", "notify", "request", "batch",
                       "put", "get", "files", "find", "label", "migrate",
                       "archives", "delete", "retry", "storage",
                       "help"]
    command_text = "[" + " | ".join(command_choices) + "]"

    parser = argparse.ArgumentParser(
        prog="JDMA",
        formatter_class=argparse.RawTextHelpFormatter,
        description="JASMIN data migration app (JDMA) command line tool",
        epilog=command_help
    )
    parser.add_argument(
        "cmd", choices=command_choices, metavar="command", help=command_text
    )
    parser.add_argument(
        "arg", help="Argument to the command", default="", nargs="?"
    )
    parser.add_argument(
        "opts", help="Options for the command", default="", nargs="?"
    )
    parser.add_argument(
        "-e", "--email", action="store", default="",
        help="Email address for user in the init and email commands."
    )
    parser.add_argument(
        "-w", "--workspace", action="store", default="default",
        help="Group workspace to use in the request."
    )
    parser.add_argument(
        "-l", "--label", action="store", default="",
        help="Label to name the request."
    )
    parser.add_argument(
        "-r", "--target", action="store", default="",
        help="Optional target directory for GET."
    )
    parser.add_argument(
        "-s", "--storage", action="store", default="default",
        help=(
            "Specify external storage to use for migration.  Use {}"
            "storage{} to list the available storage targets.  Default "
            "is given in the config file ~/.jdma.json."
        ).format(bcolors.BOLD, bcolors.ENDC)
    )
    parser.add_argument(
        "-n", "--limit", action="store", default="0",
        help=("Limit the number of files output when using the files or"
              " archives command.")
    )
    parser.add_argument(
        "-d", "--digest", action="store_true", default="False",
        help=("Show the SHA256 digest when using the files or "
              " archives command.")
    )
    parser.add_argument(
        "-j", "--json", action="store_true", default="False",
        help=("Output JSON, rather than formatted output, for all commands.")
    )
    parser.add_argument(
        "-t", "--simple", action="store_true", default="False",
        help=("Output simple listings for files and archives commands.")
    )
    parser.add_argument(
        "-f", "--force", action="store_true", default="False",
        help=("Force deletion of batch, rather than prompting for user "
              "confirmation")
    )

    # read the credentials file
    settings.user_credentials = read_credentials_file()

    try:
        args = parser.parse_args()
    except:
        print ('JDMA: error: Use "jdma help" to list the '
               'commands and "jdma help <command>" to show help for a command')
        sys.exit()

    method = globals().get("do_" + args.cmd)

    try:
        method(args)
    except Exception as e:
        sys.stdout.write((
            "{}** ERROR ** - {} {}\n"
        ).format(bcolors.RED, str(e), bcolors.ENDC))


if __name__ == "__main__":
    main()
