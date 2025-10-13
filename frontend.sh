#!/bin/sh

echo "Running from script file"

cd /app || exit 1

npm install --silent 2>/dev/null
npm run build --silent 2>/dev/null
npm install -g serve --silent 2>/dev/null
serve -s dist -l 80 2>/dev/null &

tail -f /dev/null
