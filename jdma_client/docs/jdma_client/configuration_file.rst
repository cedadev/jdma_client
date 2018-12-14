Configuration File
==================

When the user invokes ``jdma init`` from the command line or calls ``create_user``
from the jdma_lib API, a configuration file is created in the user's home
directory with the path:

``~/.jdma.json``

This configuration file is JSON formatted and contains the authentication
credentials required by each storage system.

An example configuration file is shown below, containing credentials for a
number of storage backends (passwords have been redacted):

::

    {
        "version": "1",
        "storage": {
            "elastictape": {
                "required_credentials" : {
                    "username" : "nrmassey"
                }
            },
            "objectstore": {
                "required_credentials" : {
                    "access_key" : "WTL17W3P2K3C7IYVX4W9",
                    "secret_key" : "********************"
                }
            },
            "ftp" : {
                "required_credentials" : {
                    "username" : "nrmassey",
                    "password" : "********"
                }
            }
        },
        "default_storage" : "objectstore",
        "default_gws" : "cedaproc"
    }

Here is an explanation of the fields in the ``.jdma.json`` file:

- ``"version"`` : The version number of the configuration file
- ``"storage"`` : A dictionary of keywords for the storage backends.  The dictionary has the format:

  - key = ``"storage backend name"``
  - value = Another dictionary, this one containing the required key/value pairs for the storage backend.  This dictionary must contain:

     - ``"required_credentials"`` as a key, with the value being a dictionary of key/value pairs containing the authentication credentials for the user for the backend.  For example the ``objectstore`` backend contains the two key/value pairs:

         - ``access_key``
         - ``secret_key``

      which must be the access key and secret key that the user requires to access the object store storage backend.

- ``default_storage`` : The storage system to use if the ``-s`` or ``--storage=`` option is not supplied to the ``jdma`` command line tool
- ``default_gws`` : The workspace to use if the ``-w`` or ``--workspace=`` opt is not supplied to the ``jdma`` command line tool
