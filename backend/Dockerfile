FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run app
CMD ["python", "main.py"]
