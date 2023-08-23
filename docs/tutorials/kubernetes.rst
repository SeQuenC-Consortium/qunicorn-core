Minikube | Kubernetes
=========================================

Installation / Starting Minikube (tested for windows)
----------------------

1. Install Chocolatey

2. Install Minikube Welcome!

.. code-block:: bash

    choco install minikube

3. Install kubectl  Getting started

.. code-block:: bash

    choco install kubernetes-cli

4. Install kubernetes-kompose

.. code-block:: bash

    choco install kubernetes-kompose

5. (If kubernetes files not existing): Create Kubernetes Configuration Files

.. code-block:: bash

    kompose convert -f docker-compose.yaml --out minikube

6. Start Docker
7. Start minikube

.. code-block:: bash

    minikube start

8. Set minikube as docker env

.. code-block:: bash

    minikube docker-env | Invoke-Expression

9. Build qunicorn image

.. code-block:: bash

    docker build -t qunicorn:local .

10. Start services and pods with configuration

.. code-block:: bash

    kubectl apply -f minikube

11. Expose qunicorn through minikube (start in another terminal)

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
