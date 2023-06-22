#!/bin/bash

set -e


# Confirm that kubectl is available
if ! [ -x "$(command -v kubectl)" ]; then
    echo "kubectl is not installed. Please install kubectl and try again."
    exit 1
fi

# Display the active kubernetes context
echo "Active kubernetes context:"
kubectl config current-context

# Ask if the user wants to continue with the current context
read -p "Continue with this context? (y/n) " -n 1 -r
echo ""

# if the user does not want to continue, then exit
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Exiting..."
    exit 1
fi

echo "Enabling ingress..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.7.0/deploy/static/provider/cloud/deploy.yaml

# loop until nginx-ingress controller is ready
until kubectl get pods -n ingress-nginx | grep 'ingress-nginx-controller' | grep '1/1'; do
    echo "Waiting for ingress-nginx-controller to be ready..."
    sleep 5
done

echo "Enabling postgres..."
kubectl apply -f k8s/persistent/postgres.yaml


echo "Initialization complete! 🎉🎉🎉"
echo ""
echo "You will need to add the following entries to your hosts file:"
echo "127.0.0.1 postgres.k8s.local"
echo "127.0.0.1 gateway.110yards.local"
echo ""
echo "After adding the hosts, you should be able to access the following consoles:"
echo ""
echo "Mongo:    http://mongo.k8s.local"
