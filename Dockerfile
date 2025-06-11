# Use an official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose port if needed
EXPOSE 8080

# Start the bot
CMD ["bash", "run.sh"]
