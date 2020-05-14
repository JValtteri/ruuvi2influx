#!/bin/bash
echo "Start logging and web service"
sleep 1
echo ""
echo "Start logger"
./start_logger.sh
sleep 1
echo ""
echo "Start web server"
./start_web.sh
echo ""
echo "done"
