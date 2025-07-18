#!/bin/bash

echo "Installing dependencies..."

pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

echo "Done."
