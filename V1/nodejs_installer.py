#!/usr/bin/env python3
"""
Node.js Runtime Installer for PolyRun
Installs Node.js at runtime if not found
"""

import subprocess
import os
import sys
import requests
import tarfile
import shutil
from pathlib import Path

def install_nodejs():
    """Install Node.js at runtime if not available"""
    print("🔍 Checking for Node.js...")
    
    # Check if Node.js is already available
    node_paths = ['node', 'nodejs', '/usr/bin/node', '/usr/bin/nodejs']
    for path in node_paths:
        try:
            result = subprocess.run([path, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js found at {path}: {result.stdout.strip()}")
                return path
        except FileNotFoundError:
            continue
    
    print("❌ Node.js not found. Installing...")
    
    try:
        # Install via system package manager first
        print("📦 Trying apt-get install...")
        subprocess.run(['apt-get', 'update'], check=True, capture_output=True)
        subprocess.run(['apt-get', 'install', '-y', 'nodejs', 'npm'], check=True, capture_output=True)
        
        # Test if it worked
        try:
            result = subprocess.run(['nodejs', '--version'], capture_output=True, text=True, check=True)
            print(f"✅ Node.js installed via apt-get: {result.stdout.strip()}")
            
            # Create symlink if needed
            if not os.path.exists('/usr/bin/node'):
                subprocess.run(['ln', '-sf', '/usr/bin/nodejs', '/usr/bin/node'], check=True)
            
            return 'node'
        except:
            pass
    
    except Exception as e:
        print(f"⚠️ apt-get failed: {e}")
    
    try:
        # Fallback: Download and install Node.js binary
        print("📥 Downloading Node.js binary...")
        node_version = "v18.17.0"
        node_url = f"https://nodejs.org/dist/{node_version}/node-{node_version}-linux-x64.tar.xz"
        node_dir = "/opt/nodejs"
        
        # Create directory
        os.makedirs(node_dir, exist_ok=True)
        
        # Download
        response = requests.get(node_url, stream=True)
        response.raise_for_status()
        
        # Extract
        with tarfile.open(fileobj=response.raw, mode='r|xz') as tar:
            tar.extractall(path="/opt")
        
        # Create symlinks
        node_bin_dir = f"/opt/node-{node_version}-linux-x64/bin"
        subprocess.run(['ln', '-sf', f'{node_bin_dir}/node', '/usr/local/bin/node'], check=True)
        subprocess.run(['ln', '-sf', f'{node_bin_dir}/npm', '/usr/local/bin/npm'], check=True)
        
        # Test
        result = subprocess.run(['/usr/local/bin/node', '--version'], capture_output=True, text=True, check=True)
        print(f"✅ Node.js installed from binary: {result.stdout.strip()}")
        
        return '/usr/local/bin/node'
        
    except Exception as e:
        print(f"❌ Binary installation failed: {e}")
    
    # Final fallback: Try to use system node if exists
    try:
        subprocess.run(['which', 'node'], check=True, capture_output=True)
        print("✅ Node.js found via 'which node'")
        return 'node'
    except:
        pass
    
    print("❌ All Node.js installation methods failed")
    return None

if __name__ == "__main__":
    install_nodejs()
