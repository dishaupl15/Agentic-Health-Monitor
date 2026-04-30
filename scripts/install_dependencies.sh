#!/bin/bash

cd /home/ec2-user/Agentic-Health-Monitor/agentic-health-monitor

sudo yum update -y
sudo yum install -y python3 python3-pip nodejs npm

cd backend
pip3 install -r requirements.txt

cd ../frontend
npm install
npm run build