#!/bin/bash
rm -rf .git
git init
git branch -m main
git add README.md requirements.txt .gitignore
git commit -m "Initialize project documentation and dependencies"
git add config.py app/database/ app/models/ mental_health.db
git commit -m "Configure database models and seed initial data"
git add app/services/
git commit -m "Implement core backend analytical services"
git add app/routes/ app/__init__.py
git commit -m "Implement backend routing endpoints"
git add main.py
git commit -m "Finalize backend REST API entrypoint"
git add frontend/package*.json frontend/bun.lock* frontend/tsconfig*.json frontend/vite.config.ts frontend/tailwind.config.ts frontend/postcss.config.js frontend/eslint.config.js frontend/components.json frontend/index.html frontend/public/ || true
git commit -m "Initialize React frontend configuration"
git add .
git commit -m "Implement frontend UI components and data visualization styles"
git remote add origin https://github.com/Adityaaaaa27/DigitalTwin.git
git push -u origin main -f
