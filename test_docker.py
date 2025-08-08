#!/usr/bin/env python3
# test_docker.py - Simple test to verify Docker environment
import os
import sys
from pathlib import Path

print("🐳 Docker Environment Test")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Environment variables loaded:")

# Test environment variables
env_vars = ['TELEGRAM_BOT_API', 'TELEGRAM_GROUP_ID', 'LOG_LEVEL']
for var in env_vars:
    value = os.getenv(var, 'NOT SET')
    print(f"  {var}: {'✅ SET' if value != 'NOT SET' else '❌ NOT SET'}")

# Test file access
print(f"Images directory exists: {'✅' if Path('images').exists() else '❌'}")
print(f"Main.py exists: {'✅' if Path('main.py').exists() else '❌'}")

print("🎉 Test completed!")