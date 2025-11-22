FROM python:3.10-slim

# Gerekli sistem paketlerini yükle (Chrome için)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Chrome kurulumu (Scraper için gerekli)
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# FastAPI port
EXPOSE 8000

# Scraper'ı çalıştırmak için script veya sadece API'yi başlatmak için komut
# Varsayılan olarak API başlar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

