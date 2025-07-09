#!/usr/bin/env bash
set -e

# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# shellcheck disable=SC1091
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Copy and configure .env file
cp .env.example .env

# 5. Install frontend dependencies
pushd frontend > /dev/null
npm install
popd > /dev/null

# 6. Start the project
./start.sh