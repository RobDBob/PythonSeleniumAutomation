#!/bin/bash
set +x

secret=$(aws secretsmanager get-secret-value --region eu-west-1 --secret-id "smtp-credentials-dev" | jq .SecretString | jq fromjson)
USER=$(echo $secret | jq -r .username)
PASSWORD=$(echo $secret | jq -r .password)

config="$1"
build="$2"
link="$3"
shift 3

SMTP_USER=$USER SMTP_PASSWORD=$PASSWORD python3.6 ./RunUIAutomation.py -c $config -b $build -l $link -r $@