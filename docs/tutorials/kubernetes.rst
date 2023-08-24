Minikube | Kubernetes
=========================================

Installation / Starting Minikube (tested for windows)
----------------------

1. Install`Chocolatey <https://chocolatey.org/install#individual>`_

2. Install Minikube `Minikube <https://minikube.sigs.k8s.io/docs/>`_

.. code-block:: bash

    choco install minikube

3. Install kubectl `kubectl <https://kubernetes.io/docs/setup/>`_

.. code-block:: bash

    choco install kubernetes-cli

4. Install kubernetes-kompose

.. code-block:: bash

    choco install kubernetes-kompose

5. (If kubernetes files not existing): Create Kubernetes Configuration Files.
    This will generate a folder called minikube with all the kubernetes configuration files based on the cocker-compose.
    However this might overwrite custom changes made to the files, if already existing. Proceed with caution.

.. code-block:: bash

    kompose convert -f docker-compose.yaml --out minikube

6. Start Docker (e.g. Docker Desktop)
7. Start minikube

.. code-block:: bash

    minikube start

8. Set minikube as docker env
    Minkube needs to be set as docker environment to be able to build images for minikube. Otherwise Minikube would not
    be able to find the images. This needs to be done every time a new terminal is opened.

.. code-block:: bash

    minikube docker-env | Invoke-Expression

9. Build qunicorn image

.. code-block:: bash

    docker build -t qunicorn:local .

10. Start services and pods with configuration

.. code-block:: bash

    kubectl apply -f minikube

11. Expose qunicorn through minikube (start in another terminal)
    Exposes the qunicorn service to the internet. This is needed to be able to access the service from outside the cluster.

.. code-block:: bash

    minikube tunnel

12. List service information using

.. code-block:: bash

    kubectl get svc

13. Get existing pos and fill database with data

.. code-block:: bash

    kubectl get po --selector=io.kompose.service=server

    kubectl exec {name of server pod}  -- python -m flask create-and-load-db

14. Now you can access qunicorn using [EXTERNAL-IP]:8080/swagger-ui of the server service


Other useful commands
----------------------

* Clear all kubectl pods and services

.. code-block:: bash

    kubectl delete daemonsets,replicasets,services,deployments,pods,rc,ingress --all --all-namespaces

* Expose service and create Tunnel

.. code-block:: bash

    minikube service {service}
