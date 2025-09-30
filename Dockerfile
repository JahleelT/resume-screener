# Start from base image with Python and Playwright
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

# Set work directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Install Playwright 
RUN playwright install

# Install gunicorn
RUN pip install gunicorn

# Set Production Environment
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Start the app 
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]