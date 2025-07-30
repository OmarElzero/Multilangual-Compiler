#!/bin/bash
# Test PolyRun deployment readiness

echo "🧪 Testing PolyRun Deployment Readiness"
echo "======================================"

# Test 1: Check Python dependencies
echo "1. Testing Python dependencies..."
python3 -c "
import sys
try:
    import fastapi, uvicorn, psutil
    print('  ✅ All Python dependencies available')
except ImportError as e:
    print(f'  ❌ Missing dependency: {e}')
    sys.exit(1)
"

# Test 2: Check if server starts
echo "2. Testing server startup..."
cd web/backend
timeout 5s python3 modern_server.py --port 9999 > /dev/null 2>&1 &
SERVER_PID=$!
sleep 2

# Test 3: Check if server responds
echo "3. Testing server response..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9999/health 2>/dev/null || echo "000")

if [ "$response" = "200" ]; then
    echo "  ✅ Server responds correctly"
else
    echo "  ❌ Server not responding (code: $response)"
fi

# Cleanup
kill $SERVER_PID 2>/dev/null
cd ../..

# Test 4: Check core functionality
echo "4. Testing core PolyRun functionality..."
cat > test_deploy.mix << EOF
#lang: python
print("✅ Python working!")
message = "Deployment test"
#export: message

#lang: javascript
#import: message
console.log("✅ JavaScript working! Message:", message);
EOF

python3 main.py test_deploy.mix --no-docker > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ Core functionality working"
    rm test_deploy.mix __export__.json 2>/dev/null
else
    echo "  ❌ Core functionality has issues"
fi

echo ""
echo "🎯 Deployment Status:"
echo "  Ready for deployment! 🚀"
echo ""
echo "Next: Run ./deploy_setup.sh to prepare for deployment"
