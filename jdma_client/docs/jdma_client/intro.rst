Introduction to JDMA
====================

The joint-storage data migration application (JDMA) is a multi-tiered storage
system which provides a single API to users to allow the movement of data to a
number of different storage systems, query the data they have stored on those
storage systems and retrieve the data.  These interactions are carried out using
a common user interface, which is a command line tool to be used interactively,
and a HTTP API to be used programmatically. The command line tool essentially
provides a wrapper for calls to the HTTP API.

JDMA ​was designed with the following usability criteria in mind:
  - The user experience for moving data, regardless of the underlying storage
    systems, should be identical.
  - The user should not be responsible for maintaining the connection to the
    storage system in the case of asynchronous transfers.
  - The user should receive notifications when the transfers are complete.
  - Users should be able to transfer data from one storage system to another
  - JDMA is only a request and query layer.  Any cataloguing of data should be
    carried out by the backend system.  This is so that, if JDMA fails, then the
    data is still available, independently, from the storage backend.

Command line interface

Storage

Workspaces and quotas

Batches

Requests

Notifications

Data flow (PUT, VERIFY, GET, DELETE, etc)

Using JDMA programmatically
