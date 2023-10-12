Authentication
=========================================
Authentication is based on OAuth2. The docker-compose contains a KeyCloak Service for handling the user management.
The Realm already contains the client configuration for qunicorn
After start up of the KeyCloak Service one can add users via the management interface.
The management interface is exposed on port `8081`. The following credentials are required to login: username: `kc_user`, password: `kc_pass`.
After login the realm has to switched to qunicorn in the top left dropdown menu.

Authentication token can retrieved by using the `Resource Owner Password Credentials Grant Flow <https://datatracker.ietf.org/doc/html/rfc6749#section-4.3>`_
The following shows an example how to accomplish this by using curl

.. code-block:: bash

curl --location 'http://localhost:8081/auth/realms/qunicorn/protocol/openid-connect/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'client_id=qunicorn' \
--data-urlencode 'grant_type=password' \
--data-urlencode 'username=alice' \
--data-urlencode 'password=passw0rd'

