Tutorial
========

This tutorial documents how to use JDMA from the ``jdma`` command line interface
for a typical user workflow.  It details how to set up the user to use JDMA,
and examples of data migration and retrieval.  All of the functions of JDMA will
be covered in this tutorial.

Setting up the user, user settings and user info
------------------------------------------------

Initialisation
^^^^^^^^^^^^^^

To use JDMA, first install the JDMA client software by following the instructions
in the :doc:`installation` section.

Once the JDMA client software is installed, and the virtual environment is
activated, the user needs to initialise their account with the command:

``jdma init <email_address> -w <default_workspace>``

which returns, on success:

.. code-block:: none

   ** SUCCESS ** - user initiliased with:
      Username : <user_name>
      Email    : <email_address>

This will do two things:

1. Create a user account on the JDMA server.
2. Create a configuration file in the user's home directory with the path
   ``~/.jdma.json``.  See the section :doc:`configuration_file` for full
   details of this file.  The user may wish to change the ``default_storage``
   and ``default_gws`` settings in the configuration file to their preferred
   defaults.

User info
^^^^^^^^^

The user can get the details stored on the server with the command:

``jdma info``

which will return, on success:

.. code-block:: none

   ** SUCCESS ** - user info:
      username: <user_name>
      email   : <email_address>
      notify  : off

User settings
^^^^^^^^^^^^^

JDMA has the ability to notify a user, via email, when their data migration or
retrieval has completed.  These notifications can be switched on or off, and
rely on a valid email address for the user.  These settings can be changed using
two commands of the JDMA client.

The user can change the email address used for notifications with the command:

``jdma email <new_email_address>``

which returns, on success:

.. code-block:: none

   ** SUCCESS ** - user email updated to: <new_email_address>

The user can switch notifications on or off with the command:

``jdma notify``

which returns, on success:

.. code-block:: none

   ** SUCCESS ** - user notifications updated to: off

Note that this is a toggle.  Issuing the ``jdma notify`` command again will
result in:

.. code-block:: none

   ** SUCCESS ** - user notifications updated to: *on*

Listing storage
^^^^^^^^^^^^^^^

The storage systems that data can be uploaded to can be listed with the command:

``jdma storage``

which results in:

.. code-block:: none

     Name                     Short ID
   0 FTP                      ftp
   1 Elastic Tape             elastictape
   2 Object Store             objectstore

(Note that not all of these storage systems may be returned when the user
issues the same command.)

When performing ``jdma put`` or ``jdma migrate`` commands, the storage system to
upload the data to can be specified with the ``-s <storage short id>`` option.
However, if no ``-s`` option is given then the ``default_storage`` field in the
user's ``.jdma.json`` configuration file will be used.  This file can be edited,
using a text editor, and the ``Short ID`` of the storage system should be set
for the ``default_storage`` field.  See the section :doc:`configuration_file`
for full details of this file.

Uploading data to a storage system
----------------------------------

There are two different methods of uploading data with JDMA: ``PUT`` and
``MIGRATE``.  ``PUT`` uploads the data and leaves the data where it is, whereas
``MIGRATE`` uploads the data and then **deletes** the data from its original
location.

Two different methods of specifying the data to upload are also available.  The
first is to specify the directory at the command.  The second is to specify a
list of file-names to upload in a text-file.  The file-names in the text-file
must contain the full path to the file and be separated by a line break (i.e.
each file-name is on a separate line.)

Put
^^^

To begin a ``PUT`` upload of a directory to a storage system use the command:

``jdma -s <storage_short_id> -w <workspace> put <directory>``

The ``-s <storage_short_id>`` can be omitted.  In this case the data will be
uploaded to the storage system indicated in the ``default_storage`` field in
the ``~/.jdma.json`` configuration file.  Similarly, the ``-w <workspace>`` can
be omitted and the data will be uploaded as part of the workspace named in the
``default_workspace`` field in the configuration file.
An optional label for the batch can be specified with the ``-l <label>`` option.
If no label is specified then it will default to the name of the directory to be
uploaded

On success the command will output:

.. code-block:: none

    ** SUCCESS ** - batch (PUT) requested:
        Request id   : 17
        Request type : PUT
        Batch id     : 8
        Workspace    : <workspace>
        Label        : jdma_test
        Date         : 2018-12-17 16:15
        Ex. storage  : <storage_short_id>
        Stage        : PUT_START

Request
^^^^^^^

To query which requests a user has made, use the command:

``jdma request``

Which returns a list of all the requests a user has made, information about the
requests and the stage each request is at:

.. code-block:: none

    req id type     batch id workspace        batch label      storage          date              stage
        17 PUT      8        cedaproc         jdma_test        elastictape      2018-12-17 16:15  PUTTING

A list of stages and what they mean is available in the section
:doc:`transfer_states`.

To get information about a specific request use the command:

``jdma request <req_id>``

which returns:

.. code-block:: none

    Request for user: nrmassey
        Request id   : 17
        Request type : PUT
        Batch id     : 8
        Workspace    : <workspace>
        Batch label  : jdma_test
        Ex. storage  : <storage_short_id>
        Request date : 2018-12-17 16:15
        Stage        : PUTTING

This has assigned both a Request id (``17``) and a Batch id (``8``) to the
request.  These ids are used for identifying the request and batch in the
subsequent commands.

While the data is being transferred, the stage will go through a number of
values describing the process that is currently happening.  These stages are
(in order):

1.  ``PUT_START``
2   ``PUT_BUILDING``
3.  ``PUT_PACKING``
4.  ``PUT_PENDING``
5.  ``PUTTING``
6.  ``VERIFY_PENDING``
7.  ``VERIFY_GETTING``
8.  ``VERIFYING``
9.  ``PUT_TIDY``
10.  ``PUT_COMPLETED``

When the stage ``PUT_COMPLETED`` is reached the data is successfully stored on
the external storage and can then be downloaded.

To ensure that the data has been written to the external storage without any
corruption, a verification process takes place.  This downloads the data from
the external storage system (``VERIFY_GETTING``) and, during the ``VERIFYING``
stage compares a checksum to one that was calculated on the data during the
``PUT_START`` stage.

JDMA treats each upload (PUT) request as a batch.  The data transferred via this
PUT request is stored on the external storage as a batch, which can be thought
of as a collection of files.

If notifications are switched on, and a valid email address is supplied, then the
user will get an email notification once their batch has fully uploaded.

The final stage for a ``put`` request is ``PUT_COMPLETED``.  Requests that
have reached this stage will be shown in the list of requests for one day after
completion.

Querying data on a storage system
----------------------------------

Batches
^^^^^^^

When a user has some data stored on one or more of the external storage systems,
as batches, they can list the batches that belong to them with the command:

``jdma batch``

which results in:

.. code-block:: none

    batch id workspace        batch label      storage          date              stage
           7 cpdn_rapidwatch  OXPEWWES_2_calib elastictape      2018-10-05 13:54  ON_STORAGE
           8 cedaproc         jdma_test        elastictape      2018-12-17 16:15  PUTTING

For more information about batches, see the :ref:`Batches` section.

Users can filter which workspace they list batches for using the `-w <workspace>`
option:

``jdma batch -w <workspace>``

.. code-block:: none

    batch id workspace        batch label      storage          date              stage
           7 cpdn_rapidwatch  OXPEWWES_2_calib elastictape      2018-10-05 13:54  ON_STORAGE

To get information about a specific batch, the batch id can be supplied to the
batch command:

``jdma batch <batch_id>``

returns:

.. code-block:: none

    Batch for user: nrmassey
        Batch id     : 7
        Workspace    : cpdn_rapidwatch
        Batch label  : OXPEWWES_2_calibration
        Ex. storage  : elastictape
        Date         : 2018-10-05 13:54
        External id  : 14048
        Stage        : ON_STORAGE

Archives
^^^^^^^^

To see which archives belong to the user, use the command:

``jdma archives``

which returns:

.. code-block:: none

    b.id workspace       batch label  storage      archive                size
       7 cpdn_rapidwatch OXPEWWES_2_c elastictape  archive_0000000002  71.7 MB
       8 cedaproc        jdma_test    elastictape  archive_0000000003  25.0 GB

or list the archives in a single batch:

``jdma archives <batch_id>``

Files
^^^^^

To get a list of files belonging to the user, use the command:

``jdma files``

This returns all of the files for the user, so it is more useful to list the
files in a batch:

``jdma files <batch_id>``

which returns:

.. code-block:: none

    b.id workspace    batch label  storage      archive            file                                                                 size
       7 cedaproc     OXPEWWES_2_c elastictape  archive_0000000002 ents/2003_2004/oxfaga_2003-09-01T01-00-00_2004-04-08T07-00-00.nc   4.0 MB
                                                                   ents/1993_1994/oxfaga_1993-09-01T01-00-00_1994-04-29T19-00-00.nc   3.9 MB
                                                                   ents/1990_1991/oxfaga_1990-09-01T01-00-00_1991-04-30T19-00-00.nc   3.8 MB
                                                                   ents/2007_2008/oxfaga_2007-09-01T01-00-00_2008-04-29T19-00-00.nc   3.8 MB
                                                                   ents/1994_1995/oxfaga_1994-09-01T07-00-00_1995-04-22T19-00-00.nc   3.7 MB
                                                                   ents/1995_1996/oxfaga_1995-09-02T01-00-00_1996-04-30T19-00-00.nc   3.7 MB
                                                                   ents/1996_1997/oxfaga_1996-09-01T01-00-00_1997-04-28T07-00-00.nc   3.7 MB
                                                                   ents/1997_1998/oxfaga_1997-09-01T01-00-00_1998-04-29T07-00-00.nc   3.7 MB
                                                                   ents/1991_1992/oxfaga_1991-09-01T13-00-00_1992-04-13T01-00-00.nc   3.6 MB
                                                                   ents/1992_1993/oxfaga_1992-09-01T01-00-00_1993-04-11T13-00-00.nc   3.6 MB
                                                                   ents/2002_2003/oxfaga_2002-09-01T01-00-00_2003-04-30T01-00-00.nc   3.6 MB
                                                                   ents/2000_2001/oxfaga_2000-09-01T01-00-00_2001-04-08T01-00-00.nc   3.6 MB
                                                                   ents/2008_2009/oxfaga_2008-09-01T01-00-00_2009-04-01T07-00-00.nc   3.6 MB
                                                                   ents/2005_2006/oxfaga_2005-09-01T01-00-00_2006-04-29T13-00-00.nc   3.6 MB
                                                                   ents/1999_2000/oxfaga_1999-09-01T01-00-00_2000-04-12T13-00-00.nc   3.5 MB
                                                                   ents/1998_1999/oxfaga_1998-09-01T01-00-00_1999-04-20T19-00-00.nc   3.5 MB
                                                                   ents/2006_2007/oxfaga_2006-09-01T01-00-00_2007-04-27T01-00-00.nc   3.5 MB
                                                                   ents/2004_2005/oxfaga_2004-09-01T01-00-00_2005-04-20T13-00-00.nc   3.5 MB
                                                                   ents/2001_2002/oxfaga_2001-09-01T01-00-00_2002-04-30T19-00-00.nc   3.4 MB
                                                                   ents/1989_1990/oxfaga_1989-12-01T01-00-00_1990-04-01T19-00-00.nc   2.5 MB

This produces a hierarchical view of the files, showing which batch and archive
each file belongs to, along with a truncated path.  To get a simple list of
files with full pathnames, the ``-t`` option can be used:

``jdma -t files <batch_id>``

.. code-block:: none

    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/2003_2004/oxfaga_2003-09-01T01-00-00_2004-04-08T07-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/1993_1994/oxfaga_1993-09-01T01-00-00_1994-04-29T19-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/1990_1991/oxfaga_1990-09-01T01-00-00_1991-04-30T19-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/2007_2008/oxfaga_2007-09-01T01-00-00_2008-04-29T19-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/1994_1995/oxfaga_1994-09-01T07-00-00_1995-04-22T19-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/1995_1996/oxfaga_1995-09-02T01-00-00_1996-04-30T19-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/1996_1997/oxfaga_1996-09-01T01-00-00_1997-04-28T07-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/1997_1998/oxfaga_1997-09-01T01-00-00_1998-04-29T07-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/1991_1992/oxfaga_1991-09-01T13-00-00_1992-04-13T01-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/1992_1993/oxfaga_1992-09-01T01-00-00_1993-04-11T13-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/2002_2003/oxfaga_2002-09-01T01-00-00_2003-04-30T01-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/2000_2001/oxfaga_2000-09-01T01-00-00_2001-04-08T01-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/2008_2009/oxfaga_2008-09-01T01-00-00_2009-04-01T07-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/2005_2006/oxfaga_2005-09-01T01-00-00_2006-04-29T13-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/1999_2000/oxfaga_1999-09-01T01-00-00_2000-04-12T13-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/1998_1999/oxfaga_1998-09-01T01-00-00_1999-04-20T19-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/2006_2007/oxfaga_2006-09-01T01-00-00_2007-04-27T01-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/2004_2005/oxfaga_2004-09-01T01-00-00_2005-04-20T13-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/2001_2002/oxfaga_2001-09-01T01-00-00_2002-04-30T19-00-00.nc
    /group_workspaces/jasmin4/cedaproc/nrmassey/OXPEWWES_2/calibration/events/1989_1990/oxfaga_1989-12-01T01-00-00_1990-04-01T19-00-00.nc

Downloading data from a storage system
--------------------------------------

A user can download the files contained in an uploaded batch with the command:

``jdma -r <target_path> get <batch_id>``

which, on success, produces:

.. code-block:: none

    ** SUCCESS ** - retrieval (GET) requested:
        Request id   : 32
        Batch id     : <batch_id>
        Workspace    : cedaproc
        Label        : OXPEWWES_2_calibration
        Date         : 2018-12-20 13:08
        Request type : GET
        Stage        : GET_START
        Target       : <target_path>


This will download all the files in the batch to the directory specified in
``<target_path>``.

To download a subset of the files, the user can specify which files to download
in a **filelist** file:

``jdma -r <target_path> get <batch_id> <filelist_filename>``

which, on success, outputs:

.. code-block:: none

    ** SUCCESS ** - retrieval (GET) requested:
        Request id   : 33
        Batch id     : <batch_id>
        Workspace    : cedaproc
        Label        : OXPEWWES_2_calibration
        Date         : 2018-12-20 13:08
        Request type : GET
        Stage        : GET_START
        Target       : <target_path>
        Filelist     : events/1989_1990/oxfaga_1989-12-01T01-00-00_1990-04-01T19-00-00.nc...

The best way to generate the filelist file is to use the ``files`` command with
the ``--simple`` (or ``-t``) option and pipe the output to a file.  This file
can then be edited.

``jdma -t files <batch_id> > filelist``

To check the progress of a download, use the ``request`` command, either on its
own, or with the request id as an option:

``jdma request <request_id>``

.. code-block:: none

    Request for user: nrmassey
        Request id   : 33
        Request type : GET
        Batch id     : 10
        Workspace    : cedaproc
        Batch label  : calibration
        Ex. storage  : objectstore
        Request date : 2018-12-21 09:57
        Stage        : GET_COMPLETED

If notifications are switched on, and a valid email address is supplied, then the
user will get an email notification once their batch (or sub-batch if a filelist
is used) has fully downloaded.

The final stage for a ``get`` request is ``GET_COMPLETED``.  Requests that
have reached this stage will be shown in the list of requests for one day after
completion.

Deleting data on a storage system
---------------------------------

Users can delete batches from a storage system.  Deleting a batch will also
delete any requests associated with it. For example, the ``put`` request issued
to upload the batch to the storage system may still be progressing.  If a
``delete`` command is issued for the batch, the upload will stop, any files that
have been uploaded will be deleted and the ``put`` request will also be deleted.

Users can delete a batch with the command:

``jdma delete <batch_id>``

This will result in the batch information being displayed, and the user being
asked whether they really want to delete the batch:

.. code-block:: none

    ** WARNING ** - this will delete the following batch:
    Batch for user: nrmassey
        Batch id     : 10
        Workspace    : cedaproc
        Batch label  : calibration
        Ex. storage  : objectstore
        Date         : 2018-12-20 13:08
        External id  : gws-cedaproc-0000000002
        Stage        : ON_STORAGE
    Do you wish to continue? [y/N]

Answering ``y`` or ``yes`` to this question will result in the output:

.. code-block:: none

    ** SUCCESS ** - removal (DELETE) requested:
        Request id   : 35
        Batch id     : 10
        Workspace    : cedaproc
        Label        : calibration
        Date         : 2018-12-20 13:08
        Request type : DELETE
        Stage        : DELETE_START

If the user does not wish to be asked this question, or the command is issued in
an automated workflow with no user intervention, the ``-f`` (or ``--force``)
option can be supplied to the command:

``jdma delete -f <batch_id>``

**This will delete the batch without any user intervention so use it carefully!**

If notifications are switched on, and a valid email address is supplied, then the
user will get an email notification once their batch is deleted.

The final stage for a ``delete`` request is ``DELETE_COMPLETED``.  Requests that
have reached this stage will be shown in the list of requests for one day after
completion.

Data flow
---------

PUT or MIGRATE requests
^^^^^^^^^^^^^^^^^^^^^^^

When a user instructs JDMA to ``put`` or ``migrate`` some data to JDMA, the
**request** will go through a number of stages.  These stages are listed below,
and more information is available at :doc:`transfer_states`.

``PUT_START -> PUT_PACKING -> PUT_PENDING -> PUTTING -> VERIFY_PENDING``

By this stage (``VERIFY_PENDING``) the data has been transferred to the external
storage system.  However, to ensure that the data held on the storage is not
corrupt and matches exactly the data before the transfer, a verification stage
is performed.  This downloads the data to a temporary area, automatically and
unseen by the user, then verifies the data using checksum information obtained
in the ``PUT_START`` stage.  These stages are:

``VERIFY_PENDING -> VERIFY_GETTING -> VERIFYING``

Once the ``VERIFYING`` stage is passed the data is known to be uncorrupted.
JDMA then cleans up with two stages:

``VERIFYING -> PUT_TIDY`` -> ``PUT_COMPLETED``

The request will stay in the ``PUT_COMPLETED`` stage for one day after
completion and then the request will be removed from JDMA.  The **batch** upload
will, however, will remain on the storage.

The **batch** created by the request also has a number of stages.  These are:

``ON_DISK -> PUTTING -> ON_STORAGE``

With ``ON_STORAGE`` being the last stage and recording that the data uploaded
to the storage successfully.

GET requests
^^^^^^^^^^^^

When a user instructs JDMA to ``get`` some data from JDMA, the
**request** will go through a number of stages.  These stages are listed below,
and more information is available at :doc:`transfer_states`.

``GET_START -> GET_PENDING -> GETTING -> GET_UNPACK``

At this stage the data has been retrieved from the storage system.  JDMA now
does some post-download processing, including unpacking if the data was packed
by JDMA on upload, verifying the checksums to detect any corrupt data, and
restoring the ownership and permissions of the downloaded files.  These
stages are:

``GET_UNPACK -> GET_RESTORE``

The data has now been fully restored and so JDMA cleans up with the two stages:

``GET_RESTORE -> GET_TIDY -> GET_COMPLETED``

The request will stay in the ``GET_COMPLETED`` stage for one day after
completion and then the request will be removed from JDMA.

DELETE requests
^^^^^^^^^^^^^^^

When a user instructs JDMA to ``delete`` some data from JDMA, the
**request** will go through a number of stages.  These stages are listed below,
and more information is available at :doc:`transfer_states`.

``DELETE_START -> DELETE_PENDING -> DELETING -> DELETE_TIDY -> DELETE_COMPLETED``

The request will stay in the ``DELETE_COMPLETED`` stage for one day after
completion and then the request will be removed from JDMA.
