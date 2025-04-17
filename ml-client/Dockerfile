FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install flask requests python-dotenv pymongo
CMD ["python", "app.py"]
