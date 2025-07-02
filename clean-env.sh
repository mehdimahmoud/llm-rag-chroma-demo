#!/bin/bash

echo "Unsetting all environment variables defined in .env file..."

if [ -f .env ]; then
    for var in $(grep -E '^[A-Z_]+=' .env | cut -d'=' -f1); do
        echo "Unsetting $var"
        unset "$var"
    done
    echo "Environment variables unset successfully"
else
    echo "No .env file found, skipping environment variable cleanup"
fi 