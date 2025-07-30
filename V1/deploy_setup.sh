#!/bin/bash
# Quick Deployment Setup Script for PolyRun

echo "🚀 PolyRun Deployment Setup"
echo "=========================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
fi

# Check if files exist
echo "✅ Checking deployment files..."
for file in "requirements.txt" "render.yaml" "Dockerfile" ".dockerignore"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ❌ $file missing"
    fi
done

# Add all files
echo "📁 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "✨ No new changes to commit"
else
    echo "💾 Committing changes..."
    git commit -m "Prepare PolyRun for deployment - $(date)"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Create GitHub repository: https://github.com/new"
echo "2. Add remote: git remote add origin https://github.com/USERNAME/polyrun.git"
echo "3. Push code: git push -u origin main"
echo "4. Deploy on Render: https://render.com (connect GitHub repo)"
echo ""
echo "🌐 Your PolyRun will be live at: https://polyrun-[hash].onrender.com"
echo "📖 Full guide: cat DEPLOYMENT_GUIDE.md"
