FROM python:3.7

# configure pip
WORKDIR /tmp
COPY pip.conf /etc/
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y unzip jq && \
    echo 'all packages are installed'

WORKDIR /usr/src/app

COPY requirements.txt ./

# Install python packages
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir awscli && \
    pip install --no-cache-dir twine && \
    pip install --no-cache-dir -r requirements.txt && \
    echo 'all Python packages are installed'

COPY ./CommonCode ./CommonCode
COPY ./setup.py ./setup.py