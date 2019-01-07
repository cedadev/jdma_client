JDMA library
============

To enable the JDMA to be used programatically in automated workflows, a
Python library is provided to expose the functionality of the JDMA as an API.
The functions of the API are outlined below.

User functions
--------------
.. autofunction:: jdma_lib.create_user
.. autofunction:: jdma_lib.update_user
.. autofunction:: jdma_lib.info_user

Query functions
---------------
.. autofunction:: jdma_lib.get_storage
.. autofunction:: jdma_lib.get_request
.. autofunction:: jdma_lib.get_batch
.. autofunction:: jdma_lib.get_files
.. autofunction:: jdma_lib.get_archives

File transfer functions
-----------------------
.. autofunction:: jdma_lib.upload_files
.. autofunction:: jdma_lib.delete_batch
.. autofunction:: jdma_lib.download_files
.. autofunction:: jdma_lib.modify_batch
