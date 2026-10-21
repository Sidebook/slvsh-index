# Use an official Python runtime as a parent image
FROM python:3.12-slim-trixie

# Refresh OS trust before bootstrapping the patched pip trust bundle.
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' ca-certificates)" ge '20250419+deb13u1' \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip --use-deprecated=legacy-certs --cert /etc/ssl/certs/ca-certificates.crt \
       install --no-cache-dir --upgrade 'pip>=26.2.2'

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY ./security /app/security
RUN python /app/security/check_trust.py

COPY ./backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY ./backend /app/backend/
COPY ./slvsh_index.json /app/

# Make port 8000 available to the world outside this container
EXPOSE 8000

WORKDIR /app/backend

# Run server.py when the container launches
CMD ["uvicorn", "server:app", "--host=0.0.0.0"]
