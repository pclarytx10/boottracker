#!/bin/bash

# Generate the static site
echo "Generating static site..."
python3 main.py

# Start the web server
echo "Starting web server on port 8888..."
echo "Visit http://localhost:8888 to view the site"
echo "Press Ctrl+C to stop the server"
cd public && python3 -m http.server 8888