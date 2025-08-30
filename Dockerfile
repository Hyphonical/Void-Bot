FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose any ports if needed (e.g., for a web server, but not required here)
# EXPOSE 8080

# Command to run the bot
CMD ["python", "Main.py"]