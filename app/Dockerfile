# Start from base image with Python and Playwright
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

# Set work directory
WORKDIR /app

# Copy . project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Start the app 
CMD ["python", "app.py"]