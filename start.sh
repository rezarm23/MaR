#!/bin/bash

echo "⏳ Running migrations..."
python manage.py migrate

echo "👤 Creating admin..."
python create_admin.py

echo "🚀 Starting server..."
gunicorn MaR_site.wsgi:application --bind 0.0.0.0:8000