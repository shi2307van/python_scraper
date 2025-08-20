#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Google Chrome
apt-get update
apt-get install -y wget unzip curl
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Find Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9.]+' | head -1)
CHROME_MAJOR=$(echo $CHROME_VERSION | cut -d. -f1)

# Install matching ChromeDriver
wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_MAJOR}.0.0/linux64/chromedriver-linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/bin/
mv /usr/bin/chromedriver-linux64/chromedriver /usr/bin/chromedriver
chmod +x /usr/bin/chromedriver

# Install Python dependencies
pip install -r requirements.txt
