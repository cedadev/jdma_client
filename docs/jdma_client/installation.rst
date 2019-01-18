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

4. clone the jdma client from the github repository:

  * ``git clone https://github.com/cedadev/jdma_client.git``

5. install the jdma client into the virtualenv using pip and the cloned repository:

  * ``pip install -e ./jdma_client``
