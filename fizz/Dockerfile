FROM python:3.11.0a5-alpine

# Set the application directory
WORKDIR .

# Install requirements.txt
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy code from the current folder to /app inside container
ADD . /app

# Define command to be run when launching container
CMD ["/app/run.py"]