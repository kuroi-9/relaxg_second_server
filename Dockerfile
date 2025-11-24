FROM nvidia/cuda:13.0.2-base-ubuntu24.04

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install build-essential python3-all python3.12-venv ffmpeg libsm6 libxext6 -y

# Creating VENV and activating by updating the PATH
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install python dependencies:
RUN pip install -r requirements.txt
RUN python manage.py collectstatic
