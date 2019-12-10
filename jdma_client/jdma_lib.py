"""
Set of abstracted out routines to interface with the JDMA.
This effectively forms an API that can be used to interact directly with JDMA
via Python.
Each function forms the HTTP API request call required to carry out each task.

Requires: requests library (pip install requests)

"""

import requests
import json
# switch off warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from jdma_client.jdma_common import *

##### User functions - interact with HTTP API to manipulate users         ######

def create_user(name, email=None, workspace="default"):
    """Create a user with the username: name

       :param string name: (`required`) name of the user to create
       :param string email: (`optional`) email address of user for notifications
       :param string workspace: (`optional`) default workspace of the user

       :return: A HTTP Response object. The two most important elements of this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful
                - 403 FORBIDDEN: User already initialized
                - 404 NOT FOUND: Name not supplied in POST request
                - 404 NOT FOUND: Email not supplied in POST request

            - **json()** (`Dictionary`): information about the user, the possible keys are:

                - **name**  (`string`): the name of the user
                - **email** (`string`): the email address of the user
                - **error** (`string`): information about the error, if one occurred

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
       """
    # create the credentials file - this function will check whether it exists
    create_credentials_file(name, workspace)
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
       :param bool notify: (`optional`) whether the user should be notified, via email, of their requests completing.

       :return: A HTTP Response object. The two most important elements of this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful
                - 403 FORBIDDEN: User not initialised yet
                - 404 NOT FOUND: name not supplied in POST request
                - 404 NOT FOUND: email not supplied

            - **json()** (`Dictionary`): information about the user, the possible keys are:

                - **name**  (`string`): the name of the user
                - **email** (`string`): the email address of the user
                - **notify** (`bool`): whether to notify the user
                - **error** (`string`): information about the error, if one occurred

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

       :param string name: (`required`) name of the user
       :param string email: (`optional`) email address of user for notifications
       :param bool notify: (`optional`) whether the user should be notified, via email, of their requests completing.

       :return: A HTTP Response object. The two most important elements of this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful
                - 403 FORBIDDEN: User not initialized yet
                - 404 NOT FOUND: Name not supplied in GET request
                - 404 NOT FOUND: User not found

            - **json()** (`Dictionary`): information about the user, the possible keys are:

                - **name**  (`string`): the name of the user
                - **email** (`string`): the email address of the user
                - **notify** (`bool`): whether to notify the user
                - **error** (`string`): information about the error, if one occurred

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """
    ###Send the HTTP request (GET) to return information about the user###
    url = settings.JDMA_API_URL + "user?name=" + name
    response = requests.get(url, verify=settings.VERIFY)
    return response


##### Request functions - interact with HTTP API to manipulate requests   ######

def get_request(name, req_id=None, workspace=None, ffilter=None):
    """Get a list of a user's requests or the details of a single request.

       :param string name: (`required`) name of the user.
       :param integer req_id: (`optional`) request id to list.  If `none` then get all of the user's requests.
       :param string ffilter: (`optional`) filter the results on `user` name or `workspace`

       :return: A HTTP Response object. The two most important elements of this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful
                - 404 NOT FOUND: name not supplied in GET request
                - 404 NOT FOUND: request id was not found (for the user)

            - **json()** (`Dictionary`): information about the request (or a list of Dictionaries), the possible keys are:

                - **request_id** (`integer`): the unique request id
                - **user** (`string`): the name of the user that the request belongs to
                - **request_type** (`string`): one of GET|PUT|MIGRATE|DELETE
                - **migration_id** (`integer`): the batch id that the request refers to
                - **label** (`string`): the label of the batch
                - **workspace** (`string`): the workspace that the batch belongs to
                - **storage** (`string`): the storage system the batch resides on
                - **stage** (`string`): the stage of the request, see documentation
                - **failure_reason** (`string`): why the request failed if stage==FAILED
                - **date** (`date`): the time and date the request was made
                - **filelist** (`filelist`): the list of files in the request for GET|PUT|MIGRATE
                - **error** (`string`): information about the error, if one occurred

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """
    url = settings.JDMA_API_URL + "request?name=" + name
    if req_id != None:
        url += ";request_id=" + str(req_id)
    if workspace != None:
        url += ";workspace=" + workspace
    if ffilter != None:
        url += ";filter=" + ffilter
    # send the request
    response = requests.get(url, verify=settings.VERIFY)
    return response


def get_batch(name, batch_id=None, workspace=None, label=None, ffilter=None):
    """Get a list of a user's batches or the details of a single batch.

       :param string name: (`required`) name of the user.
       :param integer batch_id: (`optional`) batch id to list.  If `none` then get all of the users' batches.
       :param string workspace: (`optional`) workspace to list batches for.  If `none` then list batch(es) for all of the users' workspaces.
       :param string ffilter: (`optional`) filter the results on `user` name or `workspace`

       :return: A HTTP Response object. The two most important elements of this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful
                - 404 NOT FOUND: batch id was not found (for the user)
                - 404 NOT FOUND: workspace was not found (for the user)

            - **json()** (`Dictionary`): information about the batch (or a list of Dictionaries), the possible keys are:

                - **migration_id** (`integer`) batch id.
                - **user** (`string`) the name of the user that the batch belongs to.
                - **workspace** (`string`) the workspace the batch belongs to
                - **label** (`string`) the label for the batch
                - **stage** (`string`) the stage of the batch
                - **storage** (`string`) the external storage the batch is on
                - **external_id** (`string`) the unique id of the batch on the external storage
                - **registered_date** (`string`) the date the batch was uploaded

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """
    # send the HTTP request
    url = settings.JDMA_API_URL + "migration?name=" + name
    if batch_id != None:
        url += ";migration_id=" + str(batch_id)
    if workspace != None:
        url += ";workspace=" + workspace
    if label != None:
        url += ";label=" + label
    if ffilter != None:
        url += ";filter=" + ffilter
    response = requests.get(url, verify=settings.VERIFY)
    return response


def get_storage():
    """Get a list of storage backends.

       :return: A HTTP Response object. The two most important elements of this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful
                - 404 NOT FOUND: URL not found

            - **json()** (`Dictionary`): a Dictionary of backends, the format is:

                - **key** (`integer`) the numeric id of the storage backend
                - **value** (`string`) the name of the backend

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """
    url = settings.JDMA_API_URL + "list_backends"
    response = requests.get(url, verify=settings.VERIFY)
    return response


def get_files(name, batch_id=None, workspace=None, limit=0, digest=0, ffilter=None):
    """Get a list of files that belong to a batch.

       :param string name: (`required`) name of the user to get files for.
       :param integer batch_id: (`optional`) batch id to list files for.  If `none` then get all of the users' files.
       :param string workspace: (`optional`) workspace to list files for.  If `none` then list files for all of the users' workspaces.
       :param integer limit: (`optional`) limit the number of files returned.
       :param integer digest: (`optional`) output the digest (checksum) for each file.

       :return: A HTTP Response object. The two most important elements of this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful
                - 404 NOT FOUND: name not supplied
                - 404 NOT FOUND: batch id was not found (for the user)

            - **json()** (`List`): a list of files, each one containing a Dictionary, the format is:

                - **migration_id** (`integer`) the unique id of the batch
                - **user** (`string`) the user the batch belongs to
                - **workspace** (`string`) the workspace the batch resides in
                - **label** (`string`) the batch label
                - **storage** (`string`) the external storage the batch resides on
                - **archives** (`list of dictionaries`) a list of archives that makes up the batch, each entry in the list is a dictionary, the format of which is:

                    - **archive_id** (`string`) the unique ID of the archive
                    - **pk** (`integer`) the numeric ID of the archive
                    - **size** (`integer`) the total size of the archive in bytes
                    - **limit** (`integer`) the limit of the returned number of files
                    - **digest** (`string`) the digest (checksum) of the total archive (if packed)
                    - **digest_format** (`string`) the algorithm of the digest
                    - **files** (`list of dictionaries`) a list of files that make up the archive.  Each entry is a dictionary, the format of which is:

                        - **pk** (`integer`) the numeric ID of the file
                        - **path** (`string`) the full, original path of the file
                        - **size** (`integer`) the size of the file, in bytes
                        - **digest** (`string`) the digest (checksum) of the file
                        - **digest_format** (`string`) the algorithm of the digest

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """

    url = settings.JDMA_API_URL + "file?name=" + settings.USER
    if batch_id is not None:
        url += ";migration_id=" + str(batch_id)
    if workspace is not None:
        url += ";workspace=" + workspace
    if ffilter != None:
        url += ";filter=" + ffilter

    # add the limit (the number of files output)
    url += ";limit=" + str(limit)
    # add whether to list the digest or not
    url += ";digest="+ str(digest)
    # do the request (POST)
    response = requests.get(url, verify=settings.VERIFY)
    return response


def get_archives(name, batch_id=None, workspace=None, limit=0, digest=0, ffilter=None):
    """Get a list of archives that are in a batch.

       :param string name: (`required`) name of the user to get archives for.
       :param integer batch_id: (`optional`) batch id to list archives for.  If `none` then get all of the users' archives.
       :param string workspace: (`optional`) workspace to list archives for.  If `none` then list archives for all of the users' workspaces.
       :param integer limit: (`optional`) limit the number of archives returned.
       :param integer digest: (`optional`) output the digest (checksum) for each archive.

       :return: A HTTP Response object. The two most important elementsof this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful
                - 404 NOT FOUND: name was not supplied
                - 404 NOT FOUND: batch id was not found (for the user)

            - **json()** (`List`): a list of archives, each one containing a Dictionary, the format is:

                - **migration_id** (`integer`) the unique id of the batch
                - **user** (`string`) the user the batch belongs to
                - **workspace** (`string`) the workspace the batch resides in
                - **label** (`string`) the batch label
                - **storage** (`string`) the external storage the batch resides on
                - **archives** (`list of dictionaries`) a list of archives that makes up the batch, each entry in the list is a dictionary, the format of which is:

                    - **archive_id** (`string`) the unique ID of the archive
                    - **pk** (`integer`) the numeric ID of the archive
                    - **size** (`integer`) the total size of the archive in bytes
                    - **limit** (`integer`) the limit of the returned number of files
                    - **digest** (`string`) the digest (checksum) of the total archive (if packed)
                    - **digest_format** (`string`) the algorithm of the digest

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """
    url = settings.JDMA_API_URL + "archive?name=" + settings.USER
    if batch_id:
        url += ";migration_id=" + str(batch_id)
    if workspace:
        url += ";workspace=" + workspace
    if ffilter != None:
        url += ";filter=" + ffilter

    # add the limit (the number of files output)
    url += ";limit=" + str(limit)
    # add whether to list the digest or not
    url += ";digest=" + str(digest)
    # do the request (POST)
    response = requests.get(url, verify=settings.VERIFY)

    return response


def upload_files(name, workspace=None, filelist=[], label=None, request_type=None,
                 storage=None, credentials=None):
    """Put a list of files to a storage backend.

       :param string name: (`required`) name of the user to get archives for.
       :param string workspace: (`optional`) workspace to put files to.
       :param list[`string`] filelist: (`optional`) list of files to put to storage.  Absolute paths must be used.
       :param string label: (`optional`) user label to give to the batch.  If omitted a default will be used.
       :param string request_type: (`optional`) request type for putting files to storage.  Can be either `PUT`, which is non-destructive, or `MIGRATE` which will delete the source files after a successful upload.
       :param string storage: (`optional`) the storage backend to put the files to.  e.g. `objectstore` or `elastictape`.
       :param Dictionary[`string`] credentials: (`optional`) value:key pairs of credentials required by backend and groupworkspace.

       :return: A HTTP Response object. The two most important elements of this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful
                - 403 FORBIDDEN: User not initialised yet
                - 403 FORBIDDEN: User does not have write permissions or the workspace does not exist for external storage
                - 403 FORBIDDEN: User does not have write permission for file/directory
                - 403 FORBIDDEN: User has insufficient quota remaining for workspace for external storage
                - 403 FORBIDDEN: Filelist or directory is already in a batch
                - 404 NOT FOUND: Name not supplied
                - 404 NOT FOUND: No request type supplied
                - 404 NOT FOUND: Invalid request method
                - 404 NOT FOUND: No workspace supplied
                - 404 NOT FOUND: Workspace has no associated groupworkspace quota set
                - 404 NOT FOUND: No directory path or filelist supplied
                - 404 NOT FOUND: Filelist is empty
                - 404 NOT FOUND: External storage not specified in PUT / MIGRATE request
                - 404 NOT FOUND: Path does not exist
                - 404 NOT FOUND: External storage has not been attached to the groupworkspace

            - **json()** (`List`): a Dictionary containing information about the uploaded batch, the format is:

                - **name** (`string`) user name for the request (input data)
                - **batch_id** (`integer`) the assigned batch id
                - **workspace** (`string`) workspace (input data)
                - **filelist** (`string`) filelist (input data)
                - **label** (`string`) label (input data)
                - **request_id** (`integer`) assigned id of the request
                - **request_type** request_type = PUT | MIGRATE (input data)
                - **storage** (`string`) storage (input data)
                - **filelist** (`List`) the list of files in the request (input data but may be modified by request)
                - **request_id** (`integer`) assigned id of the request
                - **stage** (`string`) the stage that the request is at
                - **registered_date** (`string`) the date the request was made
                - **error** (`string`) the error description if an error occurred

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """
    # build the URL
    url = settings.JDMA_API_URL + "request"

    # set the data
    data = {"name" : name,
            "workspace" : workspace,
            "filelist" : filelist,
            "label" : label,
            "request_type" : request_type,
            "storage" : storage,
            "credentials" : credentials}

    # do the request (POST)
    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)
    return response


def delete_batch(name, batch_id=None, storage=None, credentials=None):
    """Delete a single batch from a storage backend.

       :param string name: (`required`) name of the user to get archives for.
       :param integer batch_id: (`optional`) unique id of the batch
       :param Dictionary[`string`] credentials: (`optional`) value:key pairs of credentials required by backend and groupworkspace.

       :return: A HTTP Response object. The two most important elements of this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful
                - 403 FORBIDDEN User does not have permission to delete batch
                - 403 FORBIDDEN Duplicate DELETE request made
                - 404 NOT FOUND No batch id supplied
                - 404 NOT FOUND Batch not found
                - 404 NOT FOUND: batch id was not found (for the user)

            - **json()** (`Dictionary`): a Dictionary containing information about the deleted batch, the format is:

                - **name** (`string`) user name for the request (input data)
                - **batch_id** (`integer`) batch id (input data)
                - **storage** (`string`) storage the batch is stored on (input data)
                - **request_id** (`integer`) assigned id of the request
                - **request_type** (`string`) = DELETE
                - **workspace** (`string`) workspace that the batch is stored in
                - **stage** (`string`) the stage that the request is at
                - **registered_date** (`string`) the date the request was made
                - **label** (`string`) label of the batch
                - **error** (`string`) the error description if an error occurred

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """
    # use the same POST URL as GET and PUT
    url = settings.JDMA_API_URL + "request"
    # set the user and request type data
    data = {"name" : name,
            "request_type" : "DELETE",
            "migration_id" : batch_id,
            "storage" : storage,
            "credentials" : credentials}
    # do the request (POST)
    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)

    return response


def download_files(name, batch_id=None, filelist=[], target_dir=None,
                   credentials=None):
    """Download files from a storage backend.

       :param string name: (`required`) name of the user to get archives for.
       :param integer batch_id: (`optional`) unique id of the batch
       :param list[`string`] filelist: (`optional`) list of files to put to storage.  Absolute paths must be used.
       :param string target_dir: (`optional`) path to download the files to.
       :param Dictionary[`string`] credentials: (`optional`) value:key pairs of credentials required by backend and groupworkspace.

       :return: A HTTP Response object. The two most important elements of this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful

                - 403 FORBIDDEN: User not initialised yet
                - 403 FORBIDDEN: User does not have permission to request batch
                - 403 FORBIDDEN: Batch stage is: (~ON_STORAGE).  Cannot retrieve (GET) until stage is ON_STORAGE
                - 403 FORBIDDEN: Duplicate GET request made
                - 403 FORBIDDEN: User does not have write permission to the directory
                - 403 FORBIDDEN: Insufficient diskspace for the retrieval (GET)

                - 404 NOT FOUND: No request type supplied
                - 404 NOT FOUND: Invalid request method
                - 404 NOT FOUND: No batch id supplied
                - 404 NOT FOUND: Batch not found
                - 404 NOT FOUND: Target path not supplied
                - 404 NOT FOUND: Parent of target path does not exist
                - 404 NOT FOUND: Requested file list contains zero files that belong to batch

            - **json()** (`List`): a Dictionary containing information about the downloaded batch, the format is:

                - **name** (`string`) user name for the request (input data)
                - **batch_id** (`integer`) batch id (input data)
                - **storage** (`string`) storage the batch is stored on (input data)
                - **filelist** (`List`) the list of files downloaded (input data but may be modified by the request)
                - **target_path** (`string`) the directory the files have been downloaded to
                - **request_id** (`integer`) assigned id of the request
                - **request_type** (`string`) = GET
                - **workspace** (`string`) workspace that the batch is stored in
                - **stage** (`string`) the stage that the request is at
                - **registered_date** (`string`) the date the request was made
                - **label** (`string`) label of the batch
                - **error** (`string`) the error description if an error occurred


       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """
    # use the same POST URL as DELETE and PUT
    url = settings.JDMA_API_URL + "request"

    data = {"name" : name,
            "request_type" : "GET",
            "migration_id" : batch_id,
            "target_path" : target_dir,
            "credentials" : credentials}
    # Only add filelist if non-empty
    if filelist != []:
        data["filelist"] = filelist
    # do the request (POST)
    response = requests.post(url, data=json.dumps(data), verify=settings.VERIFY)

    return response


def modify_batch(name, batch_id=None, label=None):
    """Modify the details of a batch.  Currently limited to changing the label

       :param string name: (`required`) name of the user to get archives for.
       :param integer batch_id: (`required`) unique id of the batch
       :param string label: (`optional`) new batch label

       :return: A HTTP Response object. The two most important elements of this object are:

            - **status_code** (`integer`): the HTTP status code:

                - 200 OK: Request was successful
                - 403 FORBIDDEN: Cannot edit this batch as they do not own it
                - 404 NOT FOUND: No name supplied
                - 404 NOT FOUND: No batch id supplied
                - 404 NOT FOUND: No label supplied
                - 404 NOT FOUND: Batch id not found

            - **json()** (`Dictionary`): a Dictionary containing information about the modified batch, the format is:

                - **name** (`string`) user name for the request (input data)
                - **batch_id** (`integer`) batch id (input data)
                - **label** (`string`) new label of the batch (input data)
                - **error** (`string`) the error description if an error occurred

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
    """
    # PUT URL for migration
    url = settings.JDMA_API_URL + "migration/?name=" + settings.USER
    if batch_id:
        url += ";migration_id=" + str(batch_id)
    data = {}
    if label:
        data["label"] = label
    # do the request (PUT)
    response = requests.put(url, data=json.dumps(data), verify=settings.VERIFY)
    return response
