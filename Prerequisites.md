# Installation

## General dependencies

``` shell
sudo apt update -y
sudo apt install -y git curl perl apt-transport-https ca-certificates gnupg2 software-properties-common && sudo apt --fix-broken install 
```

## Docker

``` shell
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable edge"
sudo apt update -y
sudo apt install -y docker-ce
```

## Virtualbox

``` shell
wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
sudo apt update
sudo apt install -y virtualbox-5.2 && sudo apt --fix-broken install
```

## Kubectl and Minukube

``` shell
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin
curl -Lo kubectl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl && chmod +x kubectl && sudo mv kubectl /usr/local/bin
```

## Initial Run - Minikube

``` shell
export MINIKUBE_WANTUPDATENOTIFICATION=false
export MINIKUBE_WANTREPORTERRORPROMPT=false
export MINIKUBE_HOME=$HOME
export CHANGE_MINIKUBE_NONE_USER=true  

mkdir -p $HOME/.kube
touch $HOME/.kube/config
export KUBECONFIG=$HOME/.kube/config  

sudo -E minikube start --vm-driver=virtualbox
eval $(minikube docker-env)  
minikube dashboard
```