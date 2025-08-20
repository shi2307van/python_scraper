#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🔧 Installing Chrome and dependencies..."

# Update package list
apt-get update

# Install essential dependencies
apt-get install -y wget unzip curl gnupg software-properties-common

# Method 1: Install Chrome via official repository
echo "📦 Adding Google Chrome repository..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

# Update and install Chrome
apt-get update
apt-get install -y google-chrome-stable

# Method 2: Direct download if repository method fails
if ! command -v google-chrome &> /dev/null; then
    echo "📥 Repository installation failed, trying direct download..."
    wget -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    apt-get install -y /tmp/google-chrome.deb
    rm -f /tmp/google-chrome.deb
fi

# Verify Chrome installation
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version 2>/dev/null || echo "Version detection failed")
    echo "✅ Chrome installed successfully: $CHROME_VERSION"
    echo "✅ Chrome location: $(which google-chrome 2>/dev/null || echo 'Path detection failed')"
    
    # Create symlinks for common paths
    ln -sf $(which google-chrome) /usr/bin/google-chrome-stable 2>/dev/null || true
    ln -sf $(which google-chrome) /opt/google/chrome/google-chrome 2>/dev/null || true
else
    echo "❌ Chrome installation failed, but continuing..."
fi

# Install ChromeDriver
echo "🔧 Installing ChromeDriver..."

# Try to get Chrome version for matching ChromeDriver
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION_FULL=$(google-chrome --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+\.\d+' || echo "")
    if [ -n "$CHROME_VERSION_FULL" ]; then
        CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION_FULL | cut -d. -f1)
        echo "🔍 Chrome version: $CHROME_VERSION_FULL (Major: $CHROME_MAJOR_VERSION)"
        
        # Get matching ChromeDriver version
        CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_MAJOR_VERSION}" 2>/dev/null || echo "")
        
        if [ -n "$CHROMEDRIVER_VERSION" ]; then
            echo "📥 Downloading ChromeDriver version: $CHROMEDRIVER_VERSION"
            wget -O /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" 2>/dev/null || {
                echo "⚠️ ChromeDriver download failed, trying alternative..."
                wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" 2>/dev/null || true
            }
        fi
    fi
fi

# If specific version download failed, try latest stable
if [ ! -f /tmp/chromedriver.zip ]; then
    echo "📥 Downloading latest stable ChromeDriver..."
    LATEST_STABLE=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE" 2>/dev/null || echo "120.0.6099.109")
    wget -O /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${LATEST_STABLE}/linux64/chromedriver-linux64.zip" 2>/dev/null || {
        echo "⚠️ All ChromeDriver downloads failed, continuing without it..."
    }
fi

# Extract and install ChromeDriver if download succeeded
if [ -f /tmp/chromedriver.zip ]; then
    echo "📦 Extracting ChromeDriver..."
    unzip -q /tmp/chromedriver.zip -d /tmp/ 2>/dev/null || true
    
    # Find the chromedriver binary
    CHROMEDRIVER_BINARY=$(find /tmp -name "chromedriver" -type f 2>/dev/null | head -1)
    
    if [ -n "$CHROMEDRIVER_BINARY" ] && [ -f "$CHROMEDRIVER_BINARY" ]; then
        cp "$CHROMEDRIVER_BINARY" /usr/bin/chromedriver
        chmod +x /usr/bin/chromedriver
        
        # Create symlinks
        ln -sf /usr/bin/chromedriver /usr/local/bin/chromedriver 2>/dev/null || true
        
        echo "✅ ChromeDriver installed: $(chromedriver --version 2>/dev/null || echo 'Version check failed')"
    else
        echo "⚠️ ChromeDriver extraction failed"
    fi
    
    # Clean up
    rm -rf /tmp/chromedriver* 2>/dev/null || true
fi

# Install additional fonts and libraries for better compatibility
echo "📚 Installing additional dependencies..."
apt-get install -y \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libgtk-4-1 \
    xdg-utils \
    2>/dev/null || echo "⚠️ Some additional dependencies failed to install"

echo "🎉 Chrome and ChromeDriver setup completed!"

# Final verification
echo "🔍 Final verification:"
echo "Chrome: $(which google-chrome 2>/dev/null || echo 'Not found in PATH')"
echo "ChromeDriver: $(which chromedriver 2>/dev/null || echo 'Not found in PATH')"

# Install Python dependencies
pip install -r requirements.txt
