FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install flask requests python-dotenv pymongo beautifulsoup4 PyMuPDF playwright && playwright install --with-deps
CMD ["python", "app.py"]
