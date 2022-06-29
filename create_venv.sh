#!/bin/bash
echo "Updating package list"
sudo apt-get update

echo "Installing Python3-venv"
sudo apt-get install -y python3-venv

echo "Creating venv"
python3 -m venv venv
source venv.sh
./install.sh
deactivate
