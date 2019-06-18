#! /usr/bin/env python
"""
Command line tool for interacting with the joint-storage data migration app
(JDMA) for users who are logged into JASMIN and have full JASMIN accounts."""

# Author : Neil R Massey
# Date   : 28/07/2017

import sys
# switch off warnings
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

import os
import argparse
import json

# import the jdma_lib library
from jdma_client.jdma_lib import *
from jdma_client.jdma_common import *

# definitions for commands

def do_help(args):
    """**help** *<command>* : get help for a command."""
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


def do_init(args):
    ("""**init** *<email address>* : Initialise the Joint-Storage Data Migration App for """
     """your JASMIN login.  Creates a configuration file at ``~/.jdma.json``.""")

    # get the email from the args
    email = args.arg
    if args.email:
        email = args.email

    if args.workspace:
        workspace = args.workspace

    # call the library function
    response = create_user(settings.USER, email, workspace)
    # check the response code
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        sys.stdout.write((
              "{}** SUCCESS ** - user initiliased with{}:\n"
              "    Username : {}\n"
              "    Email    : {}\n"
        ).format(bcolors.GREEN, bcolors.ENDC, data["name"], data["email"]))
    elif response.status_code == 403:   # forbidden = user already created
        sys.stdout.write((
              "{}** SUCCESS ** - user already created{}\n"
        ).format(bcolors.GREEN, bcolors.ENDC))
    else:
        error_message(response, "cannot initialise user", args.json)


def do_email(args):
    ("""**email** *<email address>* : Set / update your email address for """
     """notifications.""")
    # get the email from the args
    email = args.arg
    if args.email:
        email = args.email
    # call the library function
    response = update_user(settings.USER, email)
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
    ("""**info** : get information about you, including email address and """
     """notification setting.""")
    response = info_user(settings.USER)
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
    ("""**notify** : Switch on / off email notifications of the completion of """
     """GET | PUT | MIGRATE requests.  Default is on.""")
    ### Send the HTTP request (PUT) to switch on / off notifications for the
    ### user ###
    # first get the status of notifications
    response = info_user(settings.USER)
    if response.status_code == 200:
        data = response.json()
        notify = data["notify"]
        # update to inverse
        response = update_user(settings.USER, notify=not notify)
        if response.status_code == 200:
            sys.stdout.write((
                "{}** SUCCESS ** - user notifications updated to: {}{}\n"
            ).format(bcolors.GREEN, ["off", "on"][not notify],
                     bcolors.ENDC))
        else:
            error_message(response, "cannot update notify for user", args.json)
    else:
        error_message(response, "cannot update notify for user", args.json)


def do_request(args):
    ("""**request** *<request_id>* : List all requests, or the details of a """
     """particular request with <request_id>.""")
    ###Send the HTTP request (GET) to get the details about a single request.
    # determine whether to list one request or all
    if len(args.arg):
        req_id = int(args.arg)
    else:
        req_id = None

    # make the request using the library
    response = get_request(name=settings.USER, req_id=req_id)
    # process if returned
    if response.status_code == 200:
        data = response.json()
        if args.json == True:
            output_json(data)
            return
        # list the requests if no req_id is given
        if req_id is None:
            list_requests(data)
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
        if "label" in data:
            sys.stdout.write((
                "    Batch label  : {}\n"
            ).format(data["label"]))
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
    else:
        # get the reason why it failed
        message = "cannot list request {} for user".format(req_id)
        error_message(response, message, args.json)


def list_requests(data):
    ("""Called from do_requests if request_id is None.  Lists all the """
     """requests.""")
    n_req = len(data["requests"])
    if n_req == 0:
        error_message(None, "no requests found for user", settings.USER)
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
                r["label"][0:16],
                r["storage"][0:16],
                r["date"][0:16].replace("T"," "),
                get_request_stage(r["stage"]))+"\n"
            )

def display_batch(data):
    """Display a single batch, with data a dictionary derived from JSON"""
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



def do_batch(args):
    ("""**batch** *<batch_id>* : List all batches, or all the details of a """
     """particular batch with *<batch_id>*.""")
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
    # determine whether we should list one batch or many, or list by label
    label_id = None
    if len(args.arg):
        batch_id = int(args.arg)
    else:
        if args.label:
            label_id = args.label
        batch_id = None

    # send the HTTP request
    response = get_batch(
        name=settings.USER,
        batch_id=batch_id,
        workspace=workspace,
        label=label_id
    )

    if response.status_code == 200:
        data = response.json()
        # check if the JSON option was chosen
        if args.json == True:
            print(data)
            return
        if batch_id is None and label_id is None:
            list_batches(data, workspace)
            return
        display_batch(data)
        return True

    else:
        if batch_id:
            error_msg = ("cannot list batch {}").format(str(batch_id))
        elif label_id:
            error_msg = ("cannot list batch with label {}").format(str(label_id))

        if workspace != None:
            error_msg += " in workspace " + workspace
        error_msg += " for user"
        error_message(response, error_msg, args.json)
        return False


def list_batches(data, workspace=None):
    ("""Called from do_batch when batch_id == None.  Lists all batches=.""")
    ### Send the HTTP request (GET) to get the details of all the user's
    ### migrations.  Optionally filter on the workspace."""

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


def migrate_or_put(args, request_type):
    ###Send the HTTP request (POST) to indicate a directory is to be migrated.
    ###
    # get the path, workspace and label (if any) from the args
    assert(request_type == "PUT" or request_type == "MIGRATE")
    # get absolute path of filelist or directory (we don't know what it is yet)
    current_path = os.path.abspath(args.arg)

    # is this a directory?
    if os.path.isdir(current_path):
        filelist = [current_path]
        label = os.path.basename(current_path)
    # does the filelist exist?
    elif os.path.exists(current_path):
        # read the filelist in and add it to the data
        filelist = read_filelist(current_path)
        # set the label to (the non absolute path of) the filelist - this may
        # be overriden later if args.label is not None
        label = args.arg
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

    if args.label:
        label = args.label

    # get the credentials for the request
    storage, credentials = get_credentials(args.storage)
    # call the library function to start the migration or put
    response = upload_files(
        name=settings.USER,
        workspace=workspace,
        filelist=filelist,
        label=label,
        request_type=request_type,
        storage=storage,
        credentials=credentials)

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
        try:
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
        except:
            error_msg = ""
        error_message(response, error_msg, args.json)


def do_put(args):
    ("""**put** *<path>|<filelist>*: Create a batch upload of the current """
     """directory, or directory in *<path>* or a list of files.\nUse *--label=* """
     """to give the batch a label.\nUse *--storage* to specify which external """
     """storage to target for the migration.  Use command **storage** to """
     """list all the available storage targets.""")
    migrate_or_put(args, "PUT")


def do_migrate(args):
    ("""**migrate** *<path>|<filelist>*: Create a batch upload of the current """
     """directory, or directory in *<path>* or a list of files.\nUse *--label=* """
     """to give the batch a label.\nUse *--storage* to specify which external """
     """storage to target for the migration.\nUse command **storage** to """
     """list all the available storage targets.\nThe data in the directory """
     """or filelist will be deleted after the upload is completed.""")
    migrate_or_put(args, "MIGRATE")

def do_delete(args):
    ("""**delete** *<batch_id>* : Delete the batch with *<batch_id>* from the
    storage""")
    # get the batch id
    if len(args.arg):
        batch_id = int(args.arg)
    else:
        batch_id = None

    if args.force == True:
        force = True
    else:
        force = False
    # get the batch info
    batch_response = get_batch(name=settings.USER, batch_id=batch_id)
    # check the return
    if batch_response.status_code != 200:
        error_msg = ("cannot delete batch {}").format(str(batch_id))
        error_msg += " for user"
        error_message(batch_response, error_msg, args.json)
        return

    batch_data = batch_response.json()    # don't prompt if force flag set

    if not force:
        # Print a warning message! and the batch info:
        warning_message = "** WARNING ** - this will delete the following batch: \n"
        sys.stdout.write(bcolors.RED + warning_message + bcolors.ENDC)
        # display the batch info
        display_batch(batch_data)

        prompt_message = "Do you wish to continue? [y/N] "
        # prompt user to confirm
        sys.stdout.write(bcolors.RED + prompt_message)
        answer = str(raw_input())
        sys.stdout.write(bcolors.ENDC)
        if answer != "y" and answer != "Y":
            return # do nothing

    # get the credentials for the request
    storage, credentials = get_credentials(batch_data["storage"])
    # do the call to the library function
    response = delete_batch(
        name=settings.USER,
        batch_id=batch_id,
        storage=batch_data["storage"],
        credentials=credentials)

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
    ("""**get** *<batch_id>* : Retrieve a batch upload of a directory or filelist """
     """with the id *<request_id>*.\nA different target directory to the """
     """original directory can be specified with *--target=*. """
     """\n\n**get** *<batch_id>* *<filelist>* : Retrieve a (subset) list of files """
     """from a batch with *<batch_id>*.\n*<filelist>* is the name of a file """
     """containing a list of filenames to retrieve.\nThe filenames in the """
     """filelist must be the relative path, as obtained by """
     """``jdma --simple files <batch_id>``."""
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

    # get a subset of the files in the batch
    if filelist:
        filelist = read_filelist(filelist)
    else:
        filelist = []

    # get the batch so we can get the storage type and then get the credentials
    # for the storage type
    storage = args.storage
    response = get_batch(
        name=settings.USER,
        batch_id=batch_id,
    )

    if response.status_code == 200:
        data = response.json()
        storage = data["storage"]
    else:
        error_data = response.json()
        error_msg = "cannot retrieve (GET) batch"
        if "migration_id" in error_data:
            error_msg += " with id " + str(error_data["migration_id"])
        error_msg += " for user"
        error_message(response, error_msg, args.json)
        return

    # get the credentials for the request
    storage, credentials = get_credentials(storage)

    # do the request
    response = download_files(
        name=settings.USER,
        batch_id=batch_id,
        filelist=filelist,
        target_dir=target_dir,
        credentials=credentials)

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
    ("""**storage** : list the storage targets that batches can be written to.""")
    response = get_storage()
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
    ("""**files** *<batch_id>* : List the original paths of files in a batch.\n"""
     """Use the *--simple* option to produce a simply formatted list which can be """
     """used in conjunction with the **get** command to get a subset of the batch.""")
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

    if args.digest:
        digest = 1
    else:
        digest = 0

    # do the request (POST)
    response = get_files(
        name=settings.USER,
        batch_id=batch_id,
        workspace=workspace,
        limit=limit,
        digest=digest
    )

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
    ("""**archives** *<batch_id>* : List the archives in a batch."""
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

    if args.digest:
        digest = 1
    else:
        digest = 0

    # do the HTTP API call
    response = get_archives(
        name = settings.USER,
        batch_id=batch_id,
        workspace=workspace,
        limit=limit,
        digest=digest
    )

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
    ("""**label** *<batch_id>* : Change the label of the batch with *<batch_id>*."""
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
    # call the library function
    response = modify_batch(
        name = settings.USER,
        batch_id = batch_id,
        label = label
    )
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


def main():
    """
| ``-e|--email=EMAIL`` : Email address for user in the init and email commands.

| ``-w|--workspace=WORKSPACE`` : Group workspace to use in the request.

| ``-l|--label=LABEL`` : Label to name or update the request."

| ``-r | --target`` : Optional target directory for GET."

| ``-s | --storage`` : Specify external storage to use for migration.  Use command **storage** to list the available storage targets.  Default is given in the config file ``~/.jdma.json``.

| ``-n | --limit`` : Limit the number of files output when using the **files** or **archives** command.

| ``-d | --digest`` : Show the SHA256 digest when using the files or archives command.

| ``-j | --json`` : Output JSON, rather than formatted output, for all commands.

| ``-t | --simple`` : Output simple listings for files and archives commands.

| ``-f | --force`` : Force deletion of batch, rather than prompting for user confirmation.

    """
    command_help = "Type help <command> to get help on a specific command"
    command_choices = ["init", "email", "info", "notify", "request", "batch",
                       "put", "get", "files", "label", "migrate",
                       "archives", "delete", "storage",
                       "help"]
    command_text = "[" + " | ".join(command_choices) + "]"

    parser = argparse.ArgumentParser(
        prog="JDMA",
        formatter_class=argparse.RawTextHelpFormatter,
        description="joint-storage data migration app (JDMA) command line tool",
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

    try:
        args = parser.parse_args()
    except:
        print ('JDMA: error: Use "jdma help" to list the '
               'commands and "jdma help <command>" to show help for a command')
        sys.exit()

    # read the credentials file if we are not initialising the user
    if args.cmd != "init":
        settings.user_credentials = read_credentials_file()

    method = globals().get("do_" + args.cmd)

    try:
        method(args)
    except KeyboardInterrupt:
        sys.stdout.write(("{}\n").format(bcolors.ENDC))
    except Exception as e:
        sys.stdout.write((
            "{}** ERROR ** - {} {}\n"
        ).format(bcolors.RED, str(e), bcolors.ENDC))

if __name__ == "__main__":
    main()
