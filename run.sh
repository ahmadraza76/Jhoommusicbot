#!/bin/bash

# Install system dependencies
apt-get update
apt-get install -y ffmpeg python3-pip

# Install Python dependencies
pip3 install -r requirements.txt

# Start the bot
python3 main.py