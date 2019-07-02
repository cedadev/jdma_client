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
.. autofunction:: jdma_client.jdma.do_help

User and system commands
------------------------
.. autofunction:: jdma_client.jdma.do_init
.. autofunction:: jdma_client.jdma.do_email
.. autofunction:: jdma_client.jdma.do_info
.. autofunction:: jdma_client.jdma.do_notify
.. autofunction:: jdma_client.jdma.do_storage

Data transfer commands
----------------------
.. autofunction:: jdma_client.jdma.do_put
.. autofunction:: jdma_client.jdma.do_migrate
.. autofunction:: jdma_client.jdma.do_get
.. autofunction:: jdma_client.jdma.do_delete

Data transfer properties and status commands
--------------------------------------------
.. autofunction:: jdma_client.jdma.do_label
.. autofunction:: jdma_client.jdma.do_request
.. autofunction:: jdma_client.jdma.do_batch
.. autofunction:: jdma_client.jdma.do_files
.. autofunction:: jdma_client.jdma.do_archives

Options
-------
.. autofunction:: jdma_client.jdma.main
