#!/bin/bash

# AI Assistant for Raspberry Pi - Setup Script
# This script installs all dependencies and configures the system

echo "🤖 AI Assistant Setup for Raspberry Pi"
echo "========================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    i2c-tools \
    build-essential \
    cmake \
    g++ \
    make \
    libopenblas-dev

# Enable I2C interface
echo "🔌 Configuring I2C interface..."
sudo raspi-config nonint do_i2c 0

# Add user to gpio and i2c groups
echo "👤 Adding user to hardware groups..."
sudo usermod -a -G gpio $USER
sudo usermod -a -G i2c $USER

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv ai_assistant_env

# Activate virtual environment
source ai_assistant_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p models
mkdir -p database

# Download TinyLlama model if not exists
if [ ! -f "models/tinyllama-1.1b-chat-v1.0.Q6_K.gguf" ]; then
    echo "⬇️ Downloading TinyLlama model..."
    wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q6_K.gguf -P models/
else
    echo "✅ TinyLlama model already exists in models/tinyllama-1.1b-chat-v1.0.Q6_K.gguf"
fi

# Initialize database files
echo "📄 Initializing database files..."
if [ ! -f "database/prompts.json" ]; then
    cat > database/prompts.json << EOF
[
  {
    "id": 1,
    "prompt": "Apa itu AI?",
    "response": "AI adalah kecerdasan buatan, teknologi yang memungkinkan komputer meniru kemampuan manusia seperti belajar dan memecahkan masalah."
  },
  {
    "id": 2,
    "prompt": "Siapa penemu Python?",
    "response": "Guido van Rossum adalah penemu bahasa pemrograman Python, diciptakan pada akhir 1980-an."
  }
]
EOF
fi

if [ ! -f "database/history.json" ]; then
    echo "[]" > database/history.json
fi

if [ ! -f "database/users.json" ]; then
    cat > database/users.json << EOF
[
  {
    "id": 1,
    "username": "ficrammanifur",
    "email": "ficrammanifur@example.com",
    "created_at": "2025-08-21T00:00:00Z"
  }
]
EOF
fi

if [ ! -f "database/id_words.txt" ]; then
    cat > database/id_words.txt << EOF
apa
itu
kecerdasan
buatan
python
raspberry
menggunakan
robot
belajar
bantu
membantu
saya
ceritain
joke
EOF
fi

# Test I2C connection
echo "🔍 Testing I2C connection..."
if command -v i2cdetect &> /dev/null; then
    echo "I2C devices detected:"
    sudo i2cdetect -y 1
else
    echo "⚠️  i2cdetect not available, skipping I2C test"
fi

# Create systemd service file
echo "🔧 Creating systemd service..."
cat > ai-assistant.service << EOF
[Unit]
Description=AI Assistant for Raspberry Pi
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/ai_assistant_env/bin
ExecStart=$(pwd)/ai_assistant_env/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "📋 Setup Summary:"
echo "=================="
echo "✅ System packages installed"
echo "✅ I2C interface enabled"
echo "✅ Python virtual environment created"
echo "✅ Dependencies installed"
echo "✅ Project directories created"
echo "✅ TinyLlama model ready at models/tinyllama-1.1b-chat-v1.0.Q6_K.gguf"
echo "✅ Database files initialized at database/"
echo ""
echo "🚀 To start the AI Assistant:"
echo "   source ai_assistant_env/bin/activate"
echo "   python app.py"
echo ""
echo "🌐 Web interface will be available at:"
echo "   http://localhost:5000"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "📝 Optional: Install as system service:"
echo "   sudo cp ai-assistant.service /etc/systemd/system/"
echo "   sudo systemctl enable ai-assistant"
echo "   sudo systemctl start ai-assistant"
echo ""
echo "⚠️  Please reboot to ensure I2C changes take effect:"
echo "   sudo reboot"