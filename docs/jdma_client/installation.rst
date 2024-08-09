Installation
============

To use JDMA, first you must install the client software.  This guide will show
you how to install it into a Python virtual-environment (virtualenv) in your
user space or home directory.

1. log into the machine where you wish to install the JDMA client into your user space or home directory.
2. create a virtual environment in your user space or home directory:

  * ``virtualenv ~/jdma_venv``
  * (or with python 3: ``python3 -m venv ~/jdma_venv``)

3. activate the virtual environment:

  * ``source ~/jdma_venv/bin/activate``

4. install the JDMA client into the virtualenv using pip and the cloned repository:

  * ``pip install git+https://github.com/cedadev/jdma_client``

.. note::
  | In **August 2024** the JDMA server was upgraded to a new operating system.
  | This requires an upgraded JDMA client to be installed.
  | If you were using JDMA prior to **August 2024** then you will *have* to upgrade your client.
  | This is a straightforward process:

  1. Activate the virtual environment as above:
    
    * ``source ~/jdma_venv/bin/activate``

  2. Install the upgraded JDMA client:

    * ``pip install --upgrade git+https://github.com/cedadev/jdma_client``

  3. Check the version of the JDMA client:

    * ``pip list | grep jdma-client``

    The correct version is ``1.0.1``