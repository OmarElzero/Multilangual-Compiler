# PolyRun Deployment Guide
**Making PolyRun Publicly Accessible**
*Updated: July 30, 2025*

## 🚀 Deployment Options Overview

### Quick Start Options (5-10 minutes)
1. **Render.com** - Free tier, zero configuration ⭐ **RECOMMENDED**
2. **Railway** - Free tier, GitHub integration
3. **Fly.io** - Free tier, great performance

### Production Options (30-60 minutes)
4. **DigitalOcean App Platform** - $5/month, managed
5. **AWS EC2** - Scalable, professional
6. **Google Cloud Run** - Serverless, pay-per-use

---

## 🎯 Option 1: Render.com (Recommended for Beginners)

**Cost**: FREE (with limitations: sleeps after inactivity, 512MB RAM)
**Setup Time**: 5 minutes
**Best For**: Demo, testing, learning, sharing with friends

### Step 1: Prepare Your Code ✅ DONE
Files already created:
- ✅ `requirements.txt` - Python dependencies
- ✅ `render.yaml` - Deployment configuration  
- ✅ `Dockerfile` - Container setup
- ✅ Server updated with port configuration

### Step 2: Deploy to Render
1. **Create GitHub Repository**:
```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "PolyRun ready for deployment"

# Add your GitHub remote (replace with your username)
git remote add origin https://github.com/YOUR_USERNAME/polyrun.git

# Push to GitHub
git push -u origin main
```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com)
   - Sign up/login with GitHub
   - Click "New+" → "Web Service"
   - Connect your `polyrun` repository
   - Render will auto-detect the `render.yaml` configuration
   - Click "Deploy Web Service"
   - ⏳ Wait 3-5 minutes for build and deploy

3. **Access Your Live App**:
   - 🌐 URL: `https://polyrun-YOUR_HASH.onrender.com`
   - 🎉 Your PolyRun is now publicly accessible!

### Step 3: Test Your Deployment
Visit your URL and test with this example:
```
#lang: python
print("🎉 PolyRun is live!")
message = "Hello from the cloud!"
numbers = [1, 2, 3, 4, 5]
print(f"Message: {message}")
#export: message, numbers

#lang: javascript
#import: message, numbers
console.log("JavaScript received:", message);
console.log("Numbers:", numbers);
let sum = numbers.reduce((a, b) => a + b, 0);
console.log("Sum of numbers:", sum);

#lang: bash
#import: message
echo "Bash received: $message"
echo "🚀 Multi-language execution working in the cloud!"
```

---

## 🎯 Option 2: Railway (Alternative Free Option)

**Cost**: FREE ($5 credit/month)
**Setup Time**: 3 minutes
**Best For**: Persistent apps, better performance than Render

### Deploy to Railway:
1. **Go to [railway.app](https://railway.app)**
2. **Login with GitHub**
3. **Click "Deploy from GitHub repo"**
4. **Select your PolyRun repository**
5. **Railway auto-detects Dockerfile and deploys**
6. **Access via provided railway.app URL**

---

## 🎯 Option 3: Fly.io (Best Performance)

**Cost**: FREE (generous limits)
**Setup Time**: 10 minutes
**Best For**: Production-like performance

### Deploy to Fly.io:
```bash
# Install fly CLI
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Initialize app
flyctl launch

# Deploy
flyctl deploy
```

---

## 🎯 Option 4: DigitalOcean App Platform (Production)

**Cost**: $5/month
**Setup Time**: 15 minutes
**Best For**: Reliable production hosting

### Steps:
1. **Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)**
2. **Create App → GitHub → Select repository**
3. **Configure**:
   - Runtime: Docker
   - Plan: Basic ($5/month)
   - Environment: Production
4. **Deploy and get custom domain**

---

## 🎯 Option 5: Quick Local Network Access

**Cost**: FREE
**Setup Time**: 30 seconds
**Best For**: Share with local network users

### Using ngrok (Tunnel):
```bash
# Install ngrok
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip

# Start your server
python web/backend/modern_server.py &

# Create public tunnel
./ngrok http 8000
```

**Result**: Get public URL like `https://abc123.ngrok.io`

---

## ⚡ Option 6: Vercel (Serverless)

**Cost**: FREE
**Setup Time**: 5 minutes
**Best For**: Static frontend + serverless API

### Deploy:
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow prompts - auto-detects as Python app
```

---

## 🔧 Production Optimizations

### 1. Environment Variables
Update your deployment to use environment variables:

```python
# In modern_server.py, add:
import os

# Configuration from environment
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
MAX_EXECUTION_TIME = int(os.getenv('MAX_EXECUTION_TIME', '30'))
```

### 2. Health Check Endpoint ✅ ALREADY ADDED
Your server already has `/health` endpoint for monitoring.

### 3. CORS Configuration ✅ ALREADY CONFIGURED
CORS is already properly configured for public access.

### 4. Security for Production
For production deployment, consider:

```python
# Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/execute")
@limiter.limit("10/minute")  # Limit to 10 executions per minute
async def execute_code(request: Request, code_request: CodeRequest):
    # Your existing code
    pass
```

---

## 🎉 Deployment Summary

### **Recommended Path for Beginners:**

1. **✅ Use Render.com** (Files already prepared!)
2. **📤 Push to GitHub** 
3. **🌐 Deploy in 5 minutes**
4. **🎯 Share your live URL** 

### **Your Live PolyRun URL will be:**
`https://polyrun-[random].onrender.com`

### **Features Working in Cloud:**
- ✅ Multi-language execution (Python, C++, JavaScript, Bash)
- ✅ Data passing between languages  
- ✅ Modern web interface
- ✅ Real-time code execution
- ✅ Example library
- ✅ Download functionality

### **Limitations on Free Tier:**
- 😴 Sleeps after 15 minutes of inactivity
- 🐌 Cold start delay (10-30 seconds)
- 💾 512MB RAM limit
- ⏱️ 30-second execution timeout

### **For Production Use:**
- Upgrade to paid plan ($7/month on Render)
- Use DigitalOcean App Platform ($5/month)
- Add custom domain
- Implement user authentication
- Add rate limiting and monitoring
<function_calls>
<invoke name="read_file">
<parameter name="filePath">/root/Multilangual Compilor/V1/web/backend/modern_server.py
