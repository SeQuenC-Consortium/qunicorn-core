Run using docker-compose
=========================================
Execute the following command the deployment will be started using docker-compose. This will build the dockerimage
containing the application and creates all required containers including the database and the message queue.

.. code-block:: bash

  docker-compose up -d
  docker-compose exec server python -m flask create-and-load-db

.. image:: ../resources/images/docker-compose-architecture.svg
  :width: 700
  :alt: Architecture

