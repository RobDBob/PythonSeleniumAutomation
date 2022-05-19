FROM centos:7

WORKDIR /tmp
COPY pip.conf /etc/
COPY requirements.txt .

RUN yum update -y && \
    yum -y install https://centos7.iuscommunity.org/ius-release.rpm && \
    yum -y install python36u python36u-pip && \
    yum -y install jq git

RUN yum -y install chromedriver-75.0.3770.100-3.el7 chromium-75.0.3770.100-3.el7

RUN yum clean all && \
    rm -rf /var/cache/yum

# Install python packages
RUN pip3.6 install --no-cache-dir --upgrade pip setuptools && \
    pip3.6 install --no-cache-dir awscli && \
    pip3.6 install --no-cache-dir -r requirements.txt
