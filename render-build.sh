#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🔧 Installing Chrome and ChromeDriver..."

# Update package list
apt-get update

# Install dependencies
apt-get install -y wget unzip curl gnupg

# Add Google's official GPG key and repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

# Update package list again and install Chrome
apt-get update
apt-get install -y google-chrome-stable

# Verify Chrome installation
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version)
    echo "✅ Chrome installed: $CHROME_VERSION"
    echo "✅ Chrome location: $(which google-chrome)"
else
    echo "❌ Chrome installation failed"
    exit 1
fi

# Extract Chrome version number for ChromeDriver
CHROME_VERSION_NUMBER=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+')
CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION_NUMBER | cut -d. -f1)
echo "🔍 Chrome version: $CHROME_VERSION_NUMBER"
echo "🔍 Chrome major version: $CHROME_MAJOR_VERSION"

# Get the latest ChromeDriver version for this Chrome version
CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_MAJOR_VERSION}")
echo "🔍 ChromeDriver version: $CHROMEDRIVER_VERSION"

# Download and install ChromeDriver
echo "📥 Downloading ChromeDriver..."
wget -O /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"

echo "📦 Extracting ChromeDriver..."
unzip /tmp/chromedriver.zip -d /tmp/
cp /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver
chmod +x /usr/bin/chromedriver

# Verify ChromeDriver installation
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_INSTALLED_VERSION=$(chromedriver --version)
    echo "✅ ChromeDriver installed: $CHROMEDRIVER_INSTALLED_VERSION"
    echo "✅ ChromeDriver location: $(which chromedriver)"
else
    echo "❌ ChromeDriver installation failed"
    exit 1
fi

# Clean up
rm -f /tmp/chromedriver.zip
rm -rf /tmp/chromedriver-linux64

echo "🎉 Chrome and ChromeDriver installation completed successfully!"

# Install Python dependencies
pip install -r requirements.txt
