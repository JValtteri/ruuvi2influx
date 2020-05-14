#!/bin/bash
# Setup sctipt for installing RuuviTag-logger and it's dependancies

echo "+++ Installing Python 3 +++"
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip

echo "+++ Installing screen +++"
sudo apt-get install python3

echo "+++ Installing libraries +++"
sudo apt-get install bluez-hcidump && echo +++ bluez installed +++
sudo pip3 install --upgrade setuptools
sudo pip3 install --user ruuvitag-sensor

echo "================="
echo -e "\nInstall complete!"
echo "================="
echo -e "\nYou can run RuuviTag-logger by running run.sh"

echo -e "\n\nCreate a config.yml that matches your hardware configuration."
echo -e "\n\nAn example_config.yml can be found in the RuuviTag-logger folder."
echo -e "\n\n.You can access the outputs of ruuvitag-logger and ruuvitag-web"
echo "via commands:"
echo "screen -r logger"
echo "and"
echo "screen -r web"
echo -e "\n\n.You can exit a screen with Ctrl + A, Ctrl + D.\n"
