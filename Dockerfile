# 1. Use slim Python image
FROM python:3.10-slim

# 2. Install required dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget unzip gnupg curl \
    fonts-liberation libnss3 libatk1.0-0 libatk-bridge2.0-0 libx11-xcb1 \
    libxcomposite1 libxrandr2 libxi6 libxcursor1 libxdamage1 libxfixes3 \
    libgbm1 libpango-1.0-0 libasound2 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Google Chrome (stable)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# 4. Set working directory
WORKDIR /app

# 5. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy project files
COPY . .

# 7. Expose port (for FastAPI/Flask/Django etc.)
EXPOSE 8000

# 8. Start the app
CMD ["python", "main.py"]
