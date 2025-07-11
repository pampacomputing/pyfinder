#!/usr/bin/env bash
set -e

# 1. Create virtual environment
python -m venv backend/.venv

# 2. Activate virtual environment
# shellcheck disable=SC1091
source backend/.venv/bin/activate

# 3. Install Python dependencies
pip install -r backend/requirements.txt

# 5. Copy and configure .env file
cp .env.example .env

# 6. Install frontend dependencies
pushd frontend > /dev/null
npm install
popd > /dev/null

# 6. Start the project
./start.sh