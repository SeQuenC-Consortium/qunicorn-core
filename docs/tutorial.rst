Minikube | Kubernetes
=========================================

Installation / Starting Minikube (tested for windows)
----------------------

1. Install ChocolateyInstalling Chocolatey

2. Install Minikube Welcome!

.. code-block:: bash
    number-lines:

    choco install minikube

3. Install kubectl  Getting started

.. code-block:: bash
    number-lines:

    choco install kubernetes-cli

4. Install kubernetes-kompose

.. code-block:: bash
    number-lines:

    choco install kubernetes-kompose

5. (If kubernetes files not existing): Create Kubernetes Configuration Files

.. code-block:: bash
    number-lines:

    kompose convert -f docker-compose.yaml --out minikube

6. Start minikube

.. code-block:: bash
    number-lines:

    minikube start

7. Set minikube as docker env

.. code-block:: bash
    number-lines:

    minikube docker-env | Invoke-Expression

8. Build qunicorn image

.. code-block:: bash
    number-lines:

    docker build -t qunicorn:local .

9. Start services and pods with configuration

.. code-block:: bash
    number-lines:

    kubectl apply -f minikube

10. Expose qunicorn through minikube

.. code-block:: bash
    number-lines:

    minikube tunnel

11. List service information using

.. code-block:: bash
    number-lines:

    kubectl get cvc

12. Get existing pos and fill database with data

.. code-block:: bash
    number-lines:

    kubectl get po --selector=io.kompose.service=server

    kubectl exec {name of server pod}  -- python -m flask create-and-load-db

13. Now you can access qunicorn using [EXTERNAL-IP]:8080/swagger-ui of the server service


Other useful commands
----------------------

* Clear all kubectl pods and services

.. code-block:: bash
    number-lines:

    kubectl delete daemonsets,replicasets,services,deployments,pods,rc,ingress --all --all-namespaces

* Expose service and create Tunnel

.. code-block:: bash
    number-lines:

    minikube service {service}
