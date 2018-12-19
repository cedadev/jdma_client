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

``jdma init <email_address>``

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
2.  ``PUT_PACKING``
3.  ``PUT_PENDING``
4.  ``PUTTING``
5.  ``VERIFY_PENDING``
6.  ``VERIFY_GETTING``
7.  ``VERIFYING``
8.  ``PUT_TIDY``
9.  ``PUT_COMPLETED``

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

``jdma get <batch id>``
