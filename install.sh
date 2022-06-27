#!/bin/bash
echo "Updating package list"
sudo apt-get update

sudo apt-get install bluez-hcidump

echo "Installing pip3"
sudo apt-get -y install python3-pip

echo "Updating pip"
pip3 install --upgrade pip

echo "Installing requirements"
pip3 install -r requirements.txt
