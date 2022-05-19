FROM python:3.7

# configure pip
RUN mkdir ~/.config && mkdir ~/.config/pip
COPY pip.conf ./
RUN mv pip.conf ~/.config/pip/

RUN apt-get update && \
    apt-get install -y unzip wget && \
    /usr/bin/wget -O /usr/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 && \
    chmod +x /usr/bin/jq && \
    pip install awscli==1.16.41  --force-reinstall && \
    echo 'all packages are installed'

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install twine
COPY ./CommonCode ./CommonCode
COPY ./setup.py ./setup.py