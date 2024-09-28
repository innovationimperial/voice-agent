# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the VERBI folder into the container at /app
COPY ./VERBI ./app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run run_voice_assistant.py when the container launches
CMD ["python", "/.Verbi/.app/run_voice_assistant.py"]
