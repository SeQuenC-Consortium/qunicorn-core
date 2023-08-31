ReadTheDocs - Setup and Testing
===============================

Setting up local testing
-------------------------

* Install Spinx:

.. code-block:: bash

    pip install sphinx

* Run sphinx from the qunicorn root directory:

.. code-block:: bash

    sphinx-build -a docs ./tmp/mydoc

* Open index.html from tmp/mydoc in a browser of your choice

* Regenerate the source files:

.. code-block:: bash

    sphinx-apidoc -o .\docs\source\ .\qunicorn_core\


Updating Requirements
**********************

.. code-block:: bash

    poetry export -f requirements.txt --output docs/requirements.txt --without-hashes

Setting up remote
-------------------------

Initial Setup
**********************

* Registrierung auf: `ReadTheDocs <https://about.readthedocs.com/?ref=readthedocs.org>`_
* Import a Project from GitHub
* Choose Branch
* Build the Docs

Testing
**********************

* Push changes to Github
* Rebuild Docs

Setting Up Webhook
**********************

* Create Webhook in Github (Settings -> Webhooks -> Add Webhook)
    * Data from ReadTheDocs can be found under Admin → Integrations
    * Tutorial: `How to manually configure a Git repository integration <https://docs.readthedocs.io/en/latest/guides/git-integrations.html>`_
* Webhook automatically appears under Integrations
