#!/bin/bash
apt-get update
apt-get install -y libgl1-mesa-glx libglib2.0-0 tesseract-ocr

pip install -r requirements.txt
pip install -e ./slvsh-tr