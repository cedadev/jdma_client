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
    JDMA_SERVER_URL = "http://192.168.51.26/jdma_control"  # location of the test server / vagrant version
    JDMA_API_URL = JDMA_SERVER_URL + "/api/v1/"
#    USER = os.environ["USER"] # the USER name
    USER = "nrmassey"
    VERSION = "0.1" # version of this software
    VERIFY = False
    user_credentials = {}


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


def user_not_initialized_message():
    sys.stdout.write(bcolors.RED+\
                  "** ERROR ** - User " + settings.USER + " not initialised yet." + bcolors.ENDC +\
                  "  Run " + bcolors.YELLOW + "jdma.py init" + bcolors.ENDC + " first.\n")


def print_response_error(response):
    """Print a concise summary of the error, rather than a whole output of html"""
    for il in response.content.split("\n"):
        if "Exception" in il:
            print il


def error_from_response(response):
    try:
        data = response.json()
        if "error" in data:
            sys.stdout.write(bcolors.RED + "** ERROR ** - " + data["error"] + bcolors.ENDC + "\n")
    except:
        sys.stdout.write(bcolors.RED + "** ERROR ** " + str(response.status_code) + bcolors.ENDC + "\n")


def do_help(args):
    """help <command> : get help for a command"""
    if len(args.arg):
        method = globals().get("do_" + args.arg)
        if method != None:
            print(bcolors.YELLOW + method.__doc__ + bcolors.ENDC)
        else:
            print(bcolors.YELLOW + "help: " + args.arg + " invalid choice of command." + bcolors.ENDC)
    else:
        print(bcolors.YELLOW + "help: supply command to seek help on." + bcolors.ENDC)

def do_init(args):
    """init <email address> : Initialise the JASMIN Data Migration App for your JASMIN login."""
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
        sys.stdout.write( bcolors.GREEN +\
              "** SUCCESS ** - user initiliazed with:\n" + bcolors.ENDC +\
              "    Username : " + data["name"] + "\n" +\
              "    Email    : " + data["email"] + "\n")
    elif response.status_code < 500:
        # get the reason why it failed
        error = response.json()['error']
        user = response.json()['name']
        sys.stdout.write(bcolors.RED+\
              "** ERROR ** - cannot initialise user " + user + " : " + error + bcolors.ENDC + "\n")
    else:
        sys.stdout.write(bcolors.RED+\
              "** ERROR ** - cannot initialise user " + user + " : 500 " + bcolors.ENDC + "\n")
        print_response_error(response)


def do_email(args):
    """email <email address> : Set / update your email address for notifications."""
    ###Send the HTTP request (PUT) to update the email address of the user by sending a PUT request.###
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
        sys.stdout.write(bcolors.GREEN+\
              "** SUCCESS ** - user email updated to: " + data["email"] + bcolors.ENDC + "\n")
    elif response.status_code < 500:
        # get the reason why it failed
        error = response.json()['error']
        user = response.json()['name']
        sys.stdout.write(bcolors.RED+\
              "** ERROR ** - cannot update email for user " + user+ " : " + error + bcolors.ENDC + "\n")
    else:
        print_response_error(response)


def do_info(args):
    """info : get information about you, including email address and notification setting."""
    ###Send the HTTP request (GET) to return information about the user###
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
    elif response.status_code < 500:
        # get the reason why it failed
        error = response.json()['error']
        user = response.json()['name']
        sys.stdout.write(bcolors.RED+\
              "** ERROR ** - cannot get info for user " + user + " : " + error + bcolors.ENDC + "\n")
    else:
        print_response_error(response)


def do_notify(args):
    """notify : Switch on / off email notifications of the completion of GET | PUT | MIGRATE requests.  Default is on."""
    ###Send the HTTP request (PUT) to switch on / off notifications for the user###
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
        elif response.status_code < 500:
            # get the reason why it failed
            error = response.json()['error']
            user = response.json()['name']
            sys.stdout.write(bcolors.RED+\
                  "** ERROR ** - cannot update notify for user " + user + " : " + error + bcolors.ENDC + "\n")
        else:
            print_response_error(response)
    elif response.status_code < 500:
        # get the reason why it failed
        error = response.json()['error']
        user = response.json()['name']
        sys.stdout.write(bcolors.RED+\
              "** ERROR ** - cannot update notify for user " + user + " : " + error + bcolors.ENDC + "\n")
    else:
        print_response_error(response)


def get_request_type(req_type):
    """Get a string from a request type integer.  See jdma_control.models.MigrationRequest for details"""
    request_types = ["PUT", "GET", "MIGRATE"]
    return request_types[req_type]


def get_request_stage(stage):
    request_stages = ["ON_DISK",            # 0  - Migration starts here
                      "PUT_PENDING",        # 1
                      "PUTTING",            # 2
                      "VERIFY_PENDING",     # 3
                      "VERIFY_GETTING",     # 4
                      "VERIFYING",          # 5
                      "ON_STORAGE",         # 6
                      "FAILED",             # 7
                      "",                   # 8
                      "",                   # 9
                      "ON_STORAGE",         # 10 - MigrationRequest starts here
                      "GET_PENDING",        # 11
                      "GETTING",            # 12
                      "ON_DISK",            # 13
                      "FAILED"]             # 14

    return request_stages[stage]


def get_permissions_string(p):
    # this is unix permissions
    is_dir = 'd'
    dic = {'7':'rwx', '6' :'rw-', '5' : 'r-x', '4':'r--', '0': '---'}
    perm = oct(p)[-3:]
    return is_dir + ''.join(dic.get(x,x) for x in perm)


def do_request(args):
    """request <request_id> : List all requests, or the details of a particular request with <request_id>."""
    ###Send the HTTP request (GET) to get the details about a single request.
    # determine whether to list one request or all
    if len(args.arg):
        req_id = int(args.arg)
    else:
        do_list_requests()
        return

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
    elif response.status_code < 500:
        # get the reason why it failed
        data = response.json()
        error_msg = "** ERROR ** - cannot list request " + str(data["request_id"]) + " for user " + data["name"]
        error_msg += " : " + data["error"] + "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_response_error(response)


def do_list_requests():
    """Called from do_requests if request_id is None.  Lists all the requests."""
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
            print "{:>6} {:<8} {:<8} {:<16} {:16} {:<11} {:<16}".format("req id", "type", "batch id", "workspace", "batch label", "stage", "date")
            sys.stdout.write(bcolors.ENDC)
            for r in data["requests"]:
                print "{:>6} {:<8} {:<8} {:<16} {:16} {:<11} {:<16}".format(\
                    r["request_id"],
                    get_request_type(r["request_type"]),
                    r["migration_id"],
                    r["workspace"],
                    r["migration_label"][0:16],
                    get_request_stage(r["stage"]),
                    r["date"][0:16].replace("T"," "))
    elif response.status_code < 500:
        error_data = response.json()
        error_msg = "** ERROR ** - cannot list requests for user " + error_data["name"]
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_response_error(response)


def do_batch(args):
    """batch <batch_id> : List all batches, or all the details of a particular batch with <batch_id>."""
    ### Send the HTTP request (GET) to get the details of a single migration for the user.
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
        do_list_batches(workspace)
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
        sys.stdout.write(bcolors.MAGENTA)
        sys.stdout.write("Batch for user: " + data["user"] + "\n")
        sys.stdout.write(bcolors.ENDC)
        sys.stdout.write("    Batch id     : " + str(data["migration_id"])+"\n")
        sys.stdout.write("    Workspace    : " + data["workspace"]+"\n")
        sys.stdout.write("    Label        : " + data["label"]+"\n")
        if "registered_date" in data:
            sys.stdout.write("    Date         : " + data["registered_date"][0:16].replace("T"," ")+"\n")
        sys.stdout.write("    Stage        : " + get_request_stage(data["stage"])+"\n")
        if "storage" in data:
            sys.stdout.write("    Ex. storage  : " + str(data["storage"])+"\n")
        if "external_id" in data:
            sys.stdout.write("    External id  : " + str(data["external_id"])+"\n")
        sys.stdout.write("    Directory    : " + data["original_path"]+"\n")
        sys.stdout.write("    Unix uid     : " + data["unix_user_id"]+"\n")
        sys.stdout.write("    Unix gid     : " + data["unix_group_id"]+"\n")
        sys.stdout.write("    Unix filep   : " + get_permissions_string(data["unix_permission"])+"\n")
    elif response.status_code < 500:
        # get the reason why it failed
        data = response.json()
        error_msg = "** ERROR ** - cannot list batch " + str(data["migration_id"]) + " for user " + data["name"]
        if "workspace" in data:
            error_msg += " in workspace " + data["workspace"]
        error_msg += " : " + data["error"] + "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_response_error(response)


def do_list_batches(workspace=None):
    """Called from do_batch when batch_id == None.  Lists all batches=."""
    ###Send the HTTP request (GET) to get the details of all the users migrations.
    ###Optionally filter on the workspace."""

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
            print "{:>8} {:<16} {:<16} {:<16} {:<11} {:<16}".format("batch id", "workspace", "batch label", "storage", "stage", "date")
            sys.stdout.write(bcolors.ENDC)
            for r in data["migrations"]:
                print "{:>8} {:<16} {:<16} {:<16} {:<11} {:<16}".format(\
                    r["migration_id"],
                    r["workspace"][0:16],
                    r["label"][0:16],
                    r["storage"][0:16],
                    get_request_stage(r["stage"]),
                    r["registered_date"][0:16].replace("T"," "))
    elif response.status_code < 500:
        error_data = response.json()
        error_msg = "** ERROR ** - cannot list batches for user " + error_data["name"]
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_response_error(response)


def add_credentials(args, data):
    if args.storage:
        # check whether there is a default storage backend and read it from the credentials file if there is
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
        # read the credentials for this backend from the ~/.jdma.json file and add them to the request
        # if there are no credentials in ~/.jdma.json for this backend then add nothing
        # if the backend is expecting credentials and none are supplied then the server will return an error
        try:
            data["credentials"] = settings.user_credentials['storage'][storage]['required_credentials']
        except:
            # don't add any credentials
            pass


def do_migrate_or_put(args, request_type):
    ###Send the HTTP request (POST) to indicate a directory is to be migrated.###
    # get the path, workspace and label (if any) from the args
    assert(request_type == "PUT" or request_type == "MIGRATE")
    url = settings.JDMA_API_URL + "request"
    # set the user and request type data
    data = {"name" : settings.USER,
            "request_type" : request_type}

    # add the path and workspace - if the workspace is none then don't add
    # in this case the HTTP API will return an error as a workspace is required
    if len(args.arg):
        data["original_path"] = args.arg
    else:
        data["original_path"] = os.getcwd()

    if args.workspace == "default":
        try:
            workspace = settings.user_credentials["default_gws"]
        except:
            workspace = None
    else:
        workspace = args.workspace
    data["workspace"] = workspace

    if args.label:
        data["label"] = label

    # add the credentials to the request
    add_credentials(args, data)

    # do the request (POST)
    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        sys.stdout.write(bcolors.GREEN+ \
                         "** SUCCESS ** - batch (" + request_type + ") requested:\n" + bcolors.ENDC)
        sys.stdout.write("    Request id   : " + str(data["request_id"])+"\n")
        sys.stdout.write("    Workspace    : " + data["workspace"]+"\n")
        sys.stdout.write("    Label        : " + data["label"]+"\n")
        sys.stdout.write("    Date         : " + data["registered_date"][0:16].replace("T"," ")+"\n")
        sys.stdout.write("    Request type : " + get_request_type(data["request_type"])+"\n")
        sys.stdout.write("    Ex. storage  : " + data["storage"]+"\n")
        sys.stdout.write("    Stage        : " + get_request_stage(data["stage"])+"\n")
        sys.stdout.write("    Directory    : " + data["original_path"]+"\n")
        sys.stdout.write("    Unix uid     : " + data["unix_user_id"]+"\n")
        sys.stdout.write("    Unix gid     : " + data["unix_group_id"]+"\n")
        sys.stdout.write("    Unix filep   : " + get_permissions_string(data["unix_permission"])+"\n")
    elif response.status_code < 500:
        # print the error
        error_data = response.json()
        error_msg = "** ERROR ** - cannot "+request_type+" directory"
        if "original_path" in error_data:
            error_msg += " " + error_data["original_path"]
        error_msg += " for user " + settings.USER
        if "workspace" in error_data:
            error_msg += " in workspace " + error_data["workspace"]
        if "error" in error_data:
            error_msg += " : " + error_data["error"]
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_response_error(response)


def do_put(args):
    """put <path>|<filelist>: Create a batch upload of the current directory, or directory in <path> or a list of files (with --filelist switch).  Use --label= to give the batch a label.  Use --storage to specify which external storage to target for the migration.  Use command list_storage to list all the available storage targets."""
    do_migrate_or_put(args, "PUT")


def do_migrate(args):
    """migrate <path>|<filelist>: Create a batch upload of the current directory, or directory in <path> or a list of files (with --filelist switch).  Use --label= to give the batch a label.  Use --storage to specify which external storage to target for the migration.  Use command list_storage to list all the available storage targets.  The data in the directory or filelist will be deleted after the upload is completed."""
    do_migrate_or_put(args, "MIGRATE")


def do_get(args):
    """get <batch_id> : Retrieve a batch upload of a directory or filelist with the id <request_id>.  A different target directory to the original directory can be specified with --target=."""
    ###Send the HTTP request (POST) to add a GET request to the MigrationRequests###
    # get the request id
    if len(args.arg):
        batch_id = int(args.arg)
    else:
        batch_id = None

    # get the target directory if any
    if args.target:
        target_dir = args.target
    else:
        target_dir = None

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

    # add the credentials to the request
    add_credentials(args, data)

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

    elif response.status_code < 500:
        error_data = response.json()
        error_msg = "** ERROR ** - cannot retrieve (GET) batch"
        if error_data["migration_id"]:
            error_msg += " with id " + str(error_data["migration_id"])
        if error_data["error"]:
            error_msg += ": " + str(error_data["error"])
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_response_error(response)


def do_get_files(args):
    """get_files <batch_id> <filelist> : Retrieve a (subset) list of files from a batch with <batch_id>.  <filelist> is the name of a file containing a list of filenames to retrieve.  The filenames in the filelist must be the full path, as obtained by list <batch_id>."""
    raise NotImplementedError


def do_delete(args):
    """delete <batch_id> : Delete the batch with <batch_id> from the storage"""
    raise NotImplementedError


def list_storage():
    """Return a list of the available external storage backends"""
    url = settings.JDMA_API_URL + "list_backends"
    response = requests.get(url, verify=settings.VERIFY)
    storage = {}
    if response.status_code == 200:
        # parse the JSON that comes back
        data = response.json()
        for r in range(0, len(data)):
            storage[data.keys()[r]] = data[data.keys()[r]]

    elif response.status_code < 500:
        error_msg = "** ERROR ** - cannot list storage"
        try:
            error_data = response.json()
            error_msg += ": " + str(error_data["error"])
        except:
            error_msg += " (" + str(response.status_code) + ")"
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print response.status_code
        print_response_error(response)
    return storage


def do_list_storage(args):
    """list_storage : list the storage targets that batches can be written to"""
    storage = list_storage()
    if storage != {}:
        sys.stdout.write(bcolors.MAGENTA)
        print "{:>4} {:<24} {:16}".format("", "Name", "Short ID")
        sys.stdout.write(bcolors.ENDC)
        r = 0
        for k in storage:
            sys.stdout.write("{:>4} {:<24} {:16}".format(r, storage[k], k))
            sys.stdout.write("\n")
            r+=1
        sys.stdout.write(bcolors.ENDC)


def do_list(args):
    """list <batch_id> : List the original paths of files in a batch."""
    ###Send the HTTP request (GET) to list the files in a Migration###
    # get the batch id if any
    if len(args.arg):
        batch_id = int(args.arg)
    else:
        batch_id = None

    url = settings.JDMA_API_URL + "migration?name=" + settings.USER
    if batch_id:
        url += ";batch_id=" + str(batch_id)

    # do the request (POST)
    response = requests.get(url, verify=settings.VERIFY)
    if response.status_code == 200:
        data = response.json()
        print data
    elif response.status_code < 500:
        pass
    else:
        print_response_error(response)


def do_label(args):
    """label <batch_id> : Change the label of the batch with <batch_id>."""
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

    url = settings.JDMA_API_URL + "migration?name=" + settings.USER
    if batch_id != None:
        url += ";migration_id=" + str(batch_id)
    data = {}
    if label:
        data["label"] = label
    response = requests.put(url, data=json.dumps(data), verify=settings.VERIFY)
    if response.status_code == 200:
        sys.stdout.write(bcolors.GREEN+ \
                         "** SUCCESS ** - label of batch " + str(batch_id) + " changed to: " + bcolors.ENDC + label + "\n")
    elif response.status_code < 500:
        # print the error
        error_data = response.json()
        error_msg = "** ERROR ** - cannot relabel batch " + str(batch_id)
        error_msg += " : " + error_data["error"]
        error_msg += "\n"
        sys.stdout.write(bcolors.RED + error_msg)
        sys.stdout.write(bcolors.ENDC)
    else:
        print_response_error(response)


def read_credentials_file():
    """Read in the credentials file.  It is JSON formatted"""
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
        raise IOError("User credentials file does not exist with path: " + jdma_user_config_filename)
    except Exception as e:
        raise IOError("Error in credentials file at: " + jdma_user_config_filename + "\n" + str(e))

    return jdma_user_credentials


def main():
    command_help = "Type help <command> to get help on a specific command"
    command_choices = ["init", "email", "info", "notify", "request", "batch",
                       "put", "get", "list", "find", "label", "migrate", "get_files", "delete",
                       "list_storage", "help"]
    command_text = "[" + " | ".join(command_choices) + "]"

    parser = argparse.ArgumentParser(prog="JDMA", formatter_class=argparse.RawTextHelpFormatter,
                                     description="JASMIN data migration app (JDMA) command line tool",
                                     epilog=command_help)
    parser.add_argument("cmd", choices=command_choices, metavar="command", help=command_text)
    parser.add_argument("arg", help="Argument to the command", default="", nargs="?")
    parser.add_argument("-e", "--email", action="store", default="", help="Email address for user in the init and email commands.")
    parser.add_argument("-w", "--workspace", action="store", default="default", help="Group workspace to use in the request.")
    parser.add_argument("-l", "--label", action="store", default="", help="Label to name the request.")
    parser.add_argument("-r", "--target", action="store", default="", help="Optional target directory for GET.")
    parser.add_argument("-f", "--filelist", action="store_true", default=False, help="Use filelist in put and migrate.")
    parser.add_argument("-s", "--storage", action="store", default="default", help="Specify external storage to use for migration.  Use "+bcolors.BOLD+"list_migration"+bcolors.ENDC+" to list the available storage targets.  Default is elastictape.")

    # read the credentials file
    settings.user_credentials = read_credentials_file()

    args = parser.parse_args()

    method = globals().get("do_" + args.cmd)

    method(args)

if __name__ == "__main__":
    main()
