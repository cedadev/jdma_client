Glossary
========

.. _Interfaces:

Interfaces to JDMA
------------------

JDMA offers three interfaces to interact with the JDMA server.  They are:

1.  JDMA command line client, command name is ``jdma``.  This should be used by
    most users who just wish to transfer data to JDMA from the command line.
2.  JDMA python-library, module name is ``jdma_lib``.  This should be used by
    users who wish to automate their workflows.
3.  JDMA HTTP-API, available directly from the JDMA server.  This is recommended
    only for very advanced users.  Users who wish to automate workflows should use
    the ``jdma_lib`` python-library.

.. _Storage:

Storage
-------

JDMA has the capability of transferring user data to one or more different types
of storage system using the same set of commands in the command-line client or
the same calls to the python-library.  These storage systems may be Elastic
Tape, FTP or ObjectStore.

Some storage systems require the data to be packed into tarfiles.  Each tarfile
is an **archive**.  Storage systems that do not require the data to be packed
may still organise the files into archives.  These can then be thought of as
subdirectories of the batch root directory.

.. _Workspaces:

Workspaces and quotas
---------------------

JDMA uses the concept of **workspaces** to group together data from users.  This
is analogous to the groupworkspaces under JASMIN.

On JASMIN, a groupworkspace
is a portion of disk allocated for a project where collaborating users can share
network attached storage.

For JDMA, a workspace is a portion of a storage
system that collaborating users can upload and download data from.  An important
distinction to make is that any user who is a member of the workspace can
download the data of any other user who is also in the workspace.

Each workspace has a quota that cannot be exceeded.  This quota is for the whole
workspace and is allocated to the workspace, not to individual members of the
workspace.

A user must be a member of a workspace before they can transfer data to that
workspace.

.. _Batches:

Batches
-------

Data is arranged on the storage systems, and accounted for in JDMA, as batches.

Each ``put`` or ``migrate`` request will create one batch in JDMA, and the files
in the request will be uploaded to the storage as a batch.

Subsequent ``get`` or ``delete`` requests reference the batch the user wishes to
download or delete.

.. _Archives:

Archives
--------

The external storage system may split the batch into a number of archives.

Some storage systems require the data to be packed into tarfiles.  Each tarfile
is then an archive.

Storage systems that do not require files to be in tarfiles may still split the
batch into archives, so as to avoid lots of files, or a large volume of data, in
one directory or container.  Here the archives can be thought of as
subdirectories of the batch root directory, and the files appear in the archive
subdirectory.

.. _Files:

Files
-----

Each file uploaded to JDMA is contained in an archive, which are in turn
contained in a batch.

.. _Requests:

Requests
--------

Users interact with the JDMA via requests.  These may be instructions to move
data (``put``, ``migrate``, ``get``, ``delete``) or to get information about
the requests (``request``), the user (``info``) or the batches (``batch``)
uploaded to JDMA.

Requests to move data are put in a queue, with JDMA dealing with the requests
on a first-come-first-served basis.  JDMA carries out the requests on behalf of
the user and asynchronously.

.. _Notifications:

Notifications
-------------

Notifications send users emails when their ``put``, ``migrate``, ``get`` or
``delete`` requests have completed.

Users can switch notifications on or off using the command line client.
