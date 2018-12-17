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
2. Create a configuration file in the user's home directory with the path ``~/.jdma.json``.  See the section :doc:`configuration_file` for full details of this file.  The user may wish to change the ``default_storage`` and ``default_gws`` settings in the configuration file to their preferred defaults.

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

(Note that not all of these storage systems may be returned when you issue the
same command.)

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

To begin a ``PUT`` upload of a directroy to a storage system use the command:

``jdma -s <storage_short_id> put <directory>``

The ``-s <storage_short_id>`` can be omitted.  In this case the data will be
uploaded to 
