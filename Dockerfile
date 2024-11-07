# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./slvsh-tr ./slvsh-tr
RUN pip install -e ./slvsh-tr

# Copy the current directory contents into the container at /app
COPY ./backend /app/backend/
COPY ./slvsh_index.json /app/

# Make port 8000 available to the world outside this container
EXPOSE 8000

WORKDIR /app/backend

# Run server.py when the container launches
CMD ["uvicorn", "server:app", "--host=0.0.0.0"]
