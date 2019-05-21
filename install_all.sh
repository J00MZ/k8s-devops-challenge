#!/usr/bin/env bash

if [[ "$EUID" -ne 0 ]]; then
    echo "Please run as sudo or root" 
    exit 1
fi

die_on_error (){
    MSG=$1
    echo "Error ${MSG}. exiting.." 1>&2; exit 1
}

echo "Installing software depedencies"
sudo apt update -y || die_on_error "Couldnt update packages"
sudo apt install -y git curl perl apt-transport-https ca-certificates gnupg2 software-properties-common || die_on_error "Couldnt install packages"


echo "Installing Docker"
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable edge" || die_on_error "Couldnt add Docker repo"
sudo apt update -y || die_on_error "Couldnt update packages"
sudo apt install -y docker-ce || die_on_error "Couldnt install Docker"

echo "Installing Virtualbox"
wget -q "https://www.virtualbox.org/download/oracle_vbox_2016.asc" -O - | sudo apt-key add -
sudo apt update || die_on_error "Couldnt update packages"
sudo apt install -y virtualbox-5.2 || die_on_error "Couldnt install Virtualbox"
sudo apt --fix-broken install

echo "Installing Minikube and kubectl"
curl -Lo minikube "https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64" && chmod +x minikube && sudo mv minikube /usr/local/bin || die_on_error "Couldnt install Minikube"
curl -Lo kubectl "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" && chmod +x kubectl && sudo mv kubectl /usr/local/bin || die_on_error "Couldnt install kubectl"

echo "Finished Installing all Minikube dependecies"