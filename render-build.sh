#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🔧 Installing Chrome and ChromeDriver..."

# Update package list
apt-get update

# Install dependencies
apt-get install -y wget unzip curl

# Install Google Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

# Find Chrome version and install matching ChromeDriver
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
echo "Chrome version: $CHROME_VERSION"

# Get the latest ChromeDriver version for this Chrome version
CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION%%.*}")
echo "ChromeDriver version: $CHROMEDRIVER_VERSION"

# Download and install ChromeDriver
wget -O /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"
unzip /tmp/chromedriver.zip -d /tmp/
mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver
chmod +x /usr/bin/chromedriver

# Verify installations
echo "✅ Chrome path: $(which google-chrome)"
echo "✅ ChromeDriver path: $(which chromedriver)"

# Install Python dependencies
pip install -r requirements.txt
