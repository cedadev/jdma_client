
# jdma_client

A command line client to access the JASMIN data migration app service for group workspaces on JASMIN.

### Installing in a virtualenv for beta testing on JASMIN

To install in a virtualenv, so that you can connect to the jdma-test.ceda.ac.uk test server and carry out some test migrations, do the following:

1. log into a JASMIN sci machine (jasmin-sci?.ceda.ac.uk)
2. create a virtual environment in your home directory (or wherever you choose):

  * `virtualenv ~/jdma_venv`

3. activate the virtual environment:

  * `source ~/jdma_venv/bin/activate`

4. install the jdma client into the virtualenv using pip and the github repo:

  * `pip install -e git+https://github.com/cedadev/jdma_client#egg=jdma_client`

5. create your user account:

  * `jdma -e neil.massey@stfc.ac.uk init`

  * note: you might get the error "JDMA already initialised for this user".
   This is because we have imported all the group workspace managers for elastic tape into the JDMA system already.

6. this will create a configuration file called `.jdma.json` in your home directory, even if you get the error message in step 5.  This configuration file contains some "best guess" defaults, based on your JASMIN login credentials and any group workspaces that you belong to.
You can edit this file via (e.g.) `nano $HOME/.jdma.json`:

  * currently `default_storage` should always be `"elastictape"`.  This may change when more storage types become available for use by JDMA.
  * change `default_gws` to your default group workspace (with "" around)
  * change `et_user` to your elastic tape user name (with "" around)

7. migrate some data:

  * `jdma put <path_to_some_data>`
