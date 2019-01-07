Command Reference
=================

``jdma command [command] [arg] [options]``

Options:

  | ``[-h|--help]``
  | ``[-e|--email=EMAIL]``
  | ``[-w|--workspace=WORKSPACE]``
  | ``[-l|--label=LABEL]``
  | ``[-r|--target=TARGET]``
  | ``[-s|--storage=STORAGE]``
  | ``[-n|--limit=LIMIT]``
  | ``[-d|--digest]``
  | ``[-j|--json]``
  | ``[-t|--simple]``
  | ``[-f|--force]``

Help command
------------
.. autofunction:: jdma.do_help

User and system commands
------------------------
.. autofunction:: jdma.do_init
.. autofunction:: jdma.do_email
.. autofunction:: jdma.do_info
.. autofunction:: jdma.do_notify
.. autofunction:: jdma.do_storage

Data transfer commands
----------------------
.. autofunction:: jdma.do_put
.. autofunction:: jdma.do_migrate
.. autofunction:: jdma.do_get
.. autofunction:: jdma.do_delete

Data transfer properties and status commands
--------------------------------------------
.. autofunction:: jdma.do_label
.. autofunction:: jdma.do_request
.. autofunction:: jdma.do_batch
.. autofunction:: jdma.do_files
.. autofunction:: jdma.do_archives

Options
-------
.. autofunction:: jdma.main
