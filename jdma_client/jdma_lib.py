"""
Set of abstracted out routines to interface with the JDMA.
This effectively forms an API that can be used to interact directly with JDMA
via Python.
Each function forms the HTTP API request call required to carry out each task.

Requires: requests library (pip install requests)

"""

import requests
import json
import ldap
import os
import sys
from jinja2 import Environment, FunctionLoader

# switch off warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

####################### Settings for the user / server etc ####################

class settings:
    """Settings for the jdma command line tool."""
    # location of the jdma_control server / app
    #JDMA_SERVER_URL = "https://jdma-test.ceda.ac.uk/jdma_control"
    JDMA_SERVER_URL = "https://192.168.51.26/jdma_control"
    JDMA_API_URL = JDMA_SERVER_URL + "/api/v1/"
    # template for the .config file
    JDMA_CONFIG_URL = "https://raw.githubusercontent.com/cedadev/jdma_client/master/jdma_client/.jdma.json.template"
    # get the user from the environment
    USER = os.environ["USER"] # the USER name
    USER = "nrmassey"
    # version of this software
    VERSION = "0.2"
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
    conn = ldap.initialize("ldap://homer.esc.rl.ac.uk")
    query = "memberUid={}".format(name)
    result = conn.search_s(
        "OU=ceda,OU=Groups,O=hpc,DC=rl,DC=ac,DC=uk",
        ldap.SCOPE_SUBTREE,
        query)
    workspace = ""
    for r in result:
        group = (r[1]['cn'])
        if b"gws" in group[0]:
            workspace = group[0][4:].decode("utf-8")
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
    except Exception:
        sys.stdout.write((
            "{}** ERROR ** - Error in credentials file at: {}{}\n"
        ).format(bcolors.RED, jdma_user_config_filename, bcolors.ENDC))
        sys.exit(1)

    return jdma_user_credentials


##### User functions - interact with HTTP API to manipulate users         ######

def create_user(name, email=None):
    """Create a user with the username: name
       :param string name: (`required`) name of the user to create
       :param string email: (`optional`) email address of user for notifications

       :return: A HTTP Response object. The two most important elements of this
                object are:

                    - **status_code** (`integer`): the HTTP status code:

                        - 200 OK: Request was successful
                        - 403 FORBIDDEN: User already initialized
                        - 404 NOT FOUND: name not supplied in POST request

                    - **json()** (`Dictionary`): information about the request,
                         the possible keys are:

                        - **name**  (`string`): the name of the user
                        - **email** (`string`): the email address of the user
                        - **error** (`string`): information about the error, if
                        one occurred

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
       """
    # create the credentials file - this function will check whether it exists
    create_credentials_file(name)
    url = settings.JDMA_API_URL + "user"
    data = {"name" : name}
    if email is not None:
        data["email"] = email
    ### Send the HTTP request (POST) to initialise a user.###
    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)
    return response


def update_user(name, email=None, notify=None):
    """Update a user's information with the username: name
       :param string name: (`required`) name of the user to modify
       :param string email: (`optional`) email address of user for notifications
       :param bool notify: (`optional`) whether the user should be notified,
       via email, of their requests completing.

       :return: A HTTP Response object. The two most important elements of this
                object are:

                    - **status_code** (`integer`): the HTTP status code:

                        - 200 OK: Request was successful
                        - 404 NOT FOUND: name not supplied in POST request

                    - **json()** (`Dictionary`): information about the request,
                         the possible keys are:

                        - **name**  (`string`): the name of the user
                        - **email** (`string`): the email address of the user
                        - **notify** (`bool`): whether to notify the user
                        - **error** (`string`): information about the error, if
                        one occurred

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """
    ### Send the HTTP request (PUT) to update the email address of the user by
    ### sending a PUT request.###
    url = settings.JDMA_API_URL + "user?name=" + name
    data = {"name" : name}
    if email is not None:
        data["email"] = email
    if notify is not None:
        data["notify"] = notify
    response = requests.put(url, data=json.dumps(data), verify=settings.VERIFY)
    return response


def info_user(name):
    """Get a user's information with the username: name
       :param string name: (`required`) name of the user to create
       :param string email: (`optional`) email address of user for notifications
       :param bool notify: (`optional`) whether the user should be notified,
       via email, of their requests completing.

       :return: A HTTP Response object. The two most important elements of this
                object are:

                    - **status_code** (`integer`): the HTTP status code:

                        - 200 OK: Request was successful
                        - 403 FORBIDDEN: User not initialized yet
                        - 404 NOT FOUND: name not supplied in POST request

                    - **json()** (`Dictionary`): information about the request,
                         the possible keys are:

                        - **name**  (`string`): the name of the user
                        - **email** (`string`): the email address of the user
                        - **notify** (`bool`): whether to notify the user
                        - **error** (`string`): information about the error, if
                        one occurred

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """
    ###Send the HTTP request (GET) to return information about the user###
    url = settings.JDMA_API_URL + "user?name=" + name
    response = requests.get(url, verify=settings.VERIFY)
    return response


##### Request functions - interact with HTTP API to manipulate requests   ######
