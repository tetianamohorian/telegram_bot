#!/bin/bash
kubectl create namespace botspace
kubectl create configmap init-sql --from-file=sql/init.sql -n botspace
kubectl create secret generic bot-secret --from-literal=TOKEN=7940259427:AAF_ONkz9XRDFuPRr_pGWBteITMMcnXj7oA -n botspace --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f statefulset.yaml
kubectl apply -f service.yaml
kubectl apply -f deployment.yaml
