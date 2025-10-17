#!/bin/bash

# Render build script for Chrome installation
echo "Installing Chrome and dependencies..."

# Update package list
apt-get update

# Install wget and gnupg
apt-get install -y wget gnupg

# Add Google Chrome repository
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Update package list again
apt-get update

# Install Google Chrome
apt-get install -y google-chrome-stable

# Install Chromium as backup
apt-get install -y chromium-browser

# Install Python dependencies
pip install -r requirements.txt

echo "Build completed successfully!"