FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

RUN apt-get update
RUN apt-get install -y libgl1-mesa-glx libglib2.0-0 tesseract-ocr

RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g npm@latest
