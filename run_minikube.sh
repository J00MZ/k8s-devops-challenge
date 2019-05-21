#!/usr/bin/env bash


export MINIKUBE_WANTUPDATENOTIFICATION=false
export MINIKUBE_WANTREPORTERRORPROMPT=false
export MINIKUBE_HOME=$HOME
export CHANGE_MINIKUBE_NONE_USER=true

if [ ! -d $HOME/.kube ]; then
    mkdir -p $HOME/.kube
fi

if [ ! -f $HOME/.kube/config ]; then
    touch $HOME/.kube/config
fi

export KUBECONFIG=$HOME/.kube/config

sudo -E minikube start --vm-driver=virtualbox
eval $(minikube docker-env)