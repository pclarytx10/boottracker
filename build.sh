#!/bin/bash

# Production build script for boottracker
# This script builds the site with the "boottracker" basepath for production deployment

echo "Building boottracker site for production..."
python3 main.py "/boottracker/"
echo "Production build complete!"
