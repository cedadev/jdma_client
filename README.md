
# jdma_client

A command line client to access the JASMIN data migration app service on groupworkspaces on JASMIN.

### Installing in a virtualenv for beta testing on JASMIN

To install in a virtualenv, so that you can connect to the jdma-test.ceda.ac.uk test server and carry out some test migrations, do the following:

1. log into a JASMIN sci machine (jasmin-sci?.ceda.ac.uk)
2. create a virtual environment in your home directory (or wherever you choose):

  * `virtualenv ~/jdma_venv`

3. activate the virtual environment:

  * `source ~/jdma_venv/bin/activate`

4. install the jdma client into the virtualenv using pip and the github repo:

  * `pip install -e git+https://github.com/cedadev/jdma_client#egg=jdma_client`

5. install a user credentials file into your home directory:

  * `cp jdma_venv/src/jdma-client/jdma_client/.jdma.json.template ~/.jdma.json`

6. edit the ~/.jdma.json file:

  * change `{{ default_storage }}` to `"elastictape"`
  * change `{{ default_gws }}` to your default groupworkspace (with "" around)
  * change `{{ et_user }}` to you elastic tape user name (with "" around)

7. create your user account:

  * `jdma -e neil.massey@stfc.ac.uk init`

  * note: you might get the error "JDMA already initialized for this user".
   This is because we have imported all the groupworkspace managers for elastic tape into the JDMA system already.

8. migrate some data:

  * `jdma put <path_to_some_data>`
