Transfer states
===============

When the JDMA is asked to PUT, MIGRATE, GET or DELETE some data, the request
goes through a number of states, and the batch also has a number of possible
states.  The states can be queried by using the ``jdma request <id>`` command
from ``jdma_client`` or the ``get_request`` function from ``jdma_lib``

Request states
--------------

There is a function for a mapping between the numerical code for PUT, MIGRATE, GET
or DELETE requests and a string representation in ``jdma_client.jdma_common.get_request_type``

There is a function for a mapping between the numerical code for the stage returned by
``get_request`` and a string representation in ``jdma_client.jdma_common.get_request_stage``

PUT or MIGRATE states
^^^^^^^^^^^^^^^^^^^^^
+-----+---------------------+---------------------------------------------------------------------------+
|``0``|``'PUT_START'``      | - register ``PUT`` request with JDMA                                      |
|     |                     | - **TRANSITION** ``PUT_START`` -> ``PUT_BUILDING``                        |
+-----+---------------------+---------------------------------------------------------------------------+
|``1``|``'PUT_BUILDING'``   | - lock the migration files (transfer ownership to root)                   |
|     |                     | - create a filelist for directories                                       |
|     |                     | - calculate the digests (checksums) for the files                         |
|     |                     | - **TRANSITION** ``PUT_BUILDING`` -> ``PUT_PACKING``                      |
+-----+---------------------+---------------------------------------------------------------------------+
|``2``|``'PUT_PENDING'``    | - create an upload batch on the external storage backend                  |
|     |                     | - set the batch state to PUTTING                                          |
|     |                     | - initiate the transfer                                                   |
|     |                     | - **TRANSITION** ``PUT_PENDING`` -> ``PUTTING``                           |
+-----+---------------------+---------------------------------------------------------------------------+
|``3``|``'PUT_PACKING'``    | Some backends require the files to be packed into tarfiles before transfer|
|     |                     | to the storage.  If this is the case for this transfer then:              |
|     |                     |                                                                           |
|     |                     | - create the staging directory                                            |
|     |                     | - create the tarfiles in the staging directory                            |
|     |                     | - calculate the digest (checksum) for the tarfile                         |
|     |                     | - **TRANSITION** ``PUT_PACKING`` -> ``PUT_PENDING`` (always)              |
+-----+---------------------+---------------------------------------------------------------------------+
|``4``|``'PUTTING'``        | - upload the batch to the external storage backend                        |
|     |                     | - close the upload batch on the external storage backend                  |
|     |                     | - **TRANSITION** ``PUTTING`` -> ``VERIFY_PENDING``                        |
+-----+---------------------+---------------------------------------------------------------------------+
|``5``|``'VERIFY_PENDING'`` | - create the temporary verification directory                             |
|     |                     | - create a download batch on the storage for the verification             |
|     |                     | - **TRANSITION** ``VERIFY_PENDING`` -> ``VERIFY_GETTING``                 |
+-----+---------------------+---------------------------------------------------------------------------+
|``6``|``'VERIFY_GETTING'`` | - download the batch to the temporary verification directory              |
|     |                     | - close the download batch on the external storage                        |
|     |                     | - **TRANSITION** ``VERIFY_GETTING`` -> ``VERIFYING``                      |
+-----+---------------------+---------------------------------------------------------------------------+
|``7``|``'VERIFYING'``      | - verify the batch files - make sure that the digest of the downloaded    |
|     |                     |   files matches those of the digest calculated in PUT_PACKING or          |
|     |                     |   PUT_START                                                               |
|     |                     | - set the batch state to ON_STORAGE                                       |
|     |                     | - **TRANSITION** ``VERIFYING`` -> ``PUT_TIDY``                            |
+-----+---------------------+---------------------------------------------------------------------------+
|``8``|``'PUT_TIDY'``       | - delete the staged archive tarfiles (created in PUT_PACKING)             |
|     |                     | - delete the verified downloaded archive tarfiles (created in             |
|     |                     |   VERIFY_GETTING)                                                         |
|     |                     | - delete the original files if request_type == MIGRATE or restore         |
|     |                     |   permissions on original files if request_type == PUT                    |
|     |                     | - **TRANSITION** ``PUT_TIDY`` -> ``PUT_COMPLETED``                        |
+-----+---------------------+---------------------------------------------------------------------------+
|``9``|``'PUT_COMPLETED'``  | - indicate that the request is completed. This status will remain for 72  |
|     |                     |   hours after the request is completed                                    |
|     |                     | - send the notification email that the upload of the batch has completed  |
|     |                     |   successfully                                                            |
|     |                     | - subtract the uploaded data volume amount from the workspace quota       |
|     |                     | - set the batch status to ``ON_STORAGE``                                  |
+-----+---------------------+---------------------------------------------------------------------------+

GET states
^^^^^^^^^^

+-------+-------------------+---------------------------------------------------------------------------+
|``100``|``'GET_START'``    | - create the target directory for the download                            |
|       |                   | - create the download staging directory, if the batch is packed           |
|       |                   | - **TRANSITION** ``GET_START`` -> ``GET_PENDING``                         |
+-------+-------------------+---------------------------------------------------------------------------+
|``101``|``'GET_PENDING'``  | - create a download batch on the external storage                         |
|       |                   | - initiate the transfer                                                   |
|       |                   | - **TRANSITION** ``GET_PENDING`` -> ``GETTING``                           |
+-------+-------------------+---------------------------------------------------------------------------+
|``102``|``'GETTING'``      | - download the batch, either to the target directory or to the download   |
|       |                   |   staging directory if the batch is packed                                |
|       |                   | - close the download batch on the external storage                        |
|       |                   | - **TRANSITION** ``GETTING`` -> ``GET_UNPACKING``                         |
+-------+-------------------+---------------------------------------------------------------------------+
|``103``|``'GET_UNPACKING'``| - if the batch is packed:                                                 |
|       |                   | - check the digest of the batch tarfile matches that in the database      |
|       |                   | - unpack the tar archives from the download staging directory to the      |
|       |                   |   target directory                                                        |
|       |                   | - **TRANSITION** ``GET_UNPACKING`` -> ``GET_RESTORE`` (always)            |
+-------+-------------------+---------------------------------------------------------------------------+
|``104``|``'GET_RESTORE'``  | - restore the uid, gid and permissions to the files unpacked from the tar |
|       |                   |   archive                                                                 |
|       |                   | - **TRANSITION** ``GET_RESTORE`` -> ``GET_TIDY``                          |
+-------+-------------------+---------------------------------------------------------------------------+
|``105``|``'GET_TIDY'``     | - delete the files from the download staging directory                    |
|       |                   | - **TRANSITION** ``GET_TIDY`` -> ``GET_COMPLETED``                        |
+-------+-------------------+---------------------------------------------------------------------------+
|``106``|``'GET_COMPLETED'``| - indicate that the request is completed. This status will remain for 72  |
|       |                   |   hours after the request is completed                                    |
|       |                   | - send the email notification informing the user that the batch has been  |
|       |                   |   downloaded successfully                                                 |
+-------+-------------------+---------------------------------------------------------------------------+

DELETE states
^^^^^^^^^^^^^

+-------+----------------------+------------------------------------------------------------------------+
|``200``|``'DELETE_START'``    | - lock the batch that is going to be deleted                           |
|       |                      | - **TRANSITION** ``DELETE_START`` -> ``DELETE_PENDING``                |
+-------+----------------------+------------------------------------------------------------------------+
|``201``|``'DELETE_PENDING'``  | - create a delete batch on the external storage                        |
|       |                      | - **TRANSITION** ``DELETE_PENDING`` -> ``DELETING``                    |
+-------+----------------------+------------------------------------------------------------------------+
|``202``|``'DELETING'``        | - delete the batch from the external STORAGE                           |
|       |                      | - close the delete batch                                               |
|       |                      | - **TRANSITION** ``DELETING`` -> ``DELETE_TIDY``                       |
+-------+----------------------+------------------------------------------------------------------------+
|``203``|``'DELETE_TIDY'``     | - delete any container for the batch on the external storage           |
|       |                      | - delete the archive files if batch exists and stage > PUT_PACKING     |
|       |                      | - delete the verify files if batch exists and stage > VERIFY_PENDING   |
|       |                      | - restore permissions on original files if request_type == PUT and / or|
|       |                      |   stage < PUT_TIDY                                                     |
+-------+----------------------+------------------------------------------------------------------------+
|``204``|``'DELETE_COMPLETED'``| - send the email notification informing the user that the batch has    |
|       |                      |   been deleted successfully                                            |
|       |                      | - indicate that the batch is deleted by setting its status to DELETED  |
|       |                      |   in the database                                                      |
|       |                      | - update the quota for the backend storage (add back the used space)   |
+-------+----------------------+------------------------------------------------------------------------+

FAILED state
^^^^^^^^^^^^
+--------+------------+---------------------------------------------------------------------------------+
|``1000``|``'FAILED'``| - The request has failed. The failure reason is given by the ``request`` command|
|        |            |   of the ``jdma`` command line client or by the ``get_request`` function of the |
|        |            |   ``jdma_lib``, in the "failure_reason" field in the returned JSON              |
+--------+------------+---------------------------------------------------------------------------------+

Batch states
------------

There is a function for a mapping between the numerical code returned by ``get_batch``
and a string representation in ``jdma_client.jdma_common.get_batch_stage``

+-----+-----------------+-------------------------------------------------------------------------------+
|``0``|``'ON_DISK'``    | The data is at its original location, on the (POSIX) disk                     |
+-----+-----------------+-------------------------------------------------------------------------------+
|``1``|``'PUTTING'``    | The data is in the process of being transferred to the external storage system|
+-----+-----------------+-------------------------------------------------------------------------------+
|``2``|``'ON_STORAGE'`` | The transfer is complete and the data is on the external                      |
+-----+-----------------+-------------------------------------------------------------------------------+
|``3``|``'FAILED'``     | The transfer failed.  The failure reason is given by the ``request`` command  |
|     |                 | of the ``jdma`` command line client or by the ``get_request`` function of the |
|     |                 | ``jdma_lib``                                                                  |
+-----+-----------------+-------------------------------------------------------------------------------+
|``4``|``'DELETING'``   | The batch is in the process of being deleted from the external storage        |
+-----+-----------------+-------------------------------------------------------------------------------+
|``5``|``'DELETED'``    | The batch has been deleted                                                    |
+-----+-----------------+-------------------------------------------------------------------------------+
