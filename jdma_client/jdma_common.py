"""Common functions for the jdma client"""
import ldap3
from jinja2 import Environment, FunctionLoader
import os
import sys
import json
import math

####################### Settings for the user / server etc ####################

class settings:
    """Settings for the jdma command line tool."""
    # location of the jdma_control server / app
    JDMA_SERVER_URL = "https://jdma-test.ceda.ac.uk/jdma_control"
    JDMA_API_URL = JDMA_SERVER_URL + "/api/v1/"
    # template for the .config file
    JDMA_CONFIG_URL = "https://raw.githubusercontent.com/cedadev/jdma_client/master/jdma_client/.jdma.json.template"
    # get the user from the environment
    USER = os.environ["USER"] # the USER name
    # version of this software
    VERSION = "0.2.2"
    VERIFY = False
    user_credentials = {}
    DEBUG = True

##### Lovely colours! ######

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

##### Jinja2 function #####

def load_template_from_url(url):
    """Load a Jinja2 template from a URL"""
    # fetch the template from the URL as a string
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            "Could not fetch the configuration template from the URL {}".format(
                url
            )
        )
    return response.text

##### Some helper functions to convert the numerical request types, stages #####
##### and batch stages into strings                                        #####

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
        3 : 'FAILED',
        4 : 'DELETING',
        5 : 'DELETED'
    }
    return batch_stages[stage]

##### Helper function to convert permission numbers into string representations

def get_permissions_string(p):
    # this is unix permissions
    is_dir = 'd'
    dic = {'7':'rwx', '6' :'rw-', '5' : 'r-x', '4':'r--', '0': '---'}
    perm = oct(p)[-3:]
    return is_dir + ''.join(dic.get(x,x) for x in perm)

##### Create / read the credentials file stored in ~/.jdma.json ################

def create_credentials_file(name):
    ("""Create the credentials file.  It is JSON formatted""")
    # get the default groupworkspace from the ldap
    server = ldap3.Server("ldap://homer.esc.rl.ac.uk")
    base = "OU=ceda,OU=Groups,O=hpc,DC=rl,DC=ac,DC=uk"
    query = "(memberUid={})".format(name)
    with ldap3.Connection(server, auto_bind=True) as conn:
        result = conn.search(base, query, attributes=['*'])
    workspace = ""
    for r in conn.entries:
        group = r.cn.value
        if "gws" in group:
            workspace = group[4:].decode("utf-8")
            break
    # check that a workspace was found for this user
    if workspace == "":
        raise Exception("User {} is not a member of any group workspace".format(
            name
        ))
    # form the config file name
    jdma_user_config_filename = os.environ["HOME"] + "/" + ".jdma.json"
    if not os.path.exists(jdma_user_config_filename):
        env = Environment(loader=FunctionLoader(load_template_from_url))
        template = env.get_template(settings.JDMA_CONFIG_URL)
        with open(jdma_user_config_filename, 'w') as fh:
            fh.write(template.render(
                et_user='"{}"'.format(name),
                default_storage='"elastictape"',
                default_gws='"{}"'.format(workspace)
            ))


def read_credentials_file(user_home=""):
    ("""Read in the credentials file.  It is JSON formatted"""
    )
    # path is in user directory
    if user_home == "":
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
    except Exception as e:
        sys.stdout.write((
            "{}** ERROR ** - Error in credentials file at: {}{}\n"
        ).format(bcolors.RED, jdma_user_config_filename, bcolors.ENDC))
        sys.exit(1)

    return jdma_user_credentials

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


def get_credentials(storage):
    # check whether there is a default storage backend and read it from the
    # credentials file if there is
    if storage == "default":
        try:
            storage = settings.user_credentials['default_storage']
        except:
            # the default default is elastictape
            storage = "elastictape"
    # read the credentials for this backend from the ~/.jdma.json file and
    # add them to the request if there are no credentials in ~/.jdma.json
    # for this backend then add nothing if the backend is expecting
    # credentials and none are supplied then the server will return an error
    try:
        credentials = settings.user_credentials['storage'][storage]['required_credentials']
    except:
        # don't add any credentials
        credentials = []
    return storage, credentials


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
