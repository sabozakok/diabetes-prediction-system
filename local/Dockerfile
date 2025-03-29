# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /apps_Server

# Copy the current directory contents into the container at /app
COPY . /apps_Server

# Ensure templates folder is copied
COPY templates /apps_Server/templates

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for Flask
EXPOSE 5000 5050

# Define environment variable to disable Flask debugging in production
ENV FLASK_ENV=production

# Run the application
CMD ["python", "app.py"]
