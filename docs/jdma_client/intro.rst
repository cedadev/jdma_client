Introduction to JDMA
====================

The joint-storage data migration application (JDMA) is a multi-tiered storage
system which provides a single API to users to allow the movement of data to a
number of different storage systems, query the data they have stored on those
storage systems and retrieve the data.

These interactions are carried out using a common user interface, which is a
command line tool to be used interactively, a python library or a HTTP API, both
to be used programmatically. The command line tool essentially
provides a wrapper for calls to the python library, which in turn makes calls to
the HTTP API.

JDMA ​was designed with the following usability criteria in mind:
  - The user experience for moving data, regardless of the underlying storage
    systems, should be identical.
  - The user should not be responsible for maintaining the connection to the
    storage system in the case of asynchronous transfers.
  - User and group ownership and permissions should be preserved and restored
    on downloading the data
  - The user should receive notifications when the transfers are complete.
  - Users should be able to transfer data from one storage system to another
  - JDMA is only a request and query layer.  Any cataloguing of data should be
    carried out by the backend system.  So that, if JDMA fails, then the data is
    still available, independently of JDMA, from the storage backend.
