FROM alpine:3.13.1

ENV AWS_CDK_VERSION=1.88.0

RUN apk -v --no-cache --update add \
        docker-cli \
        nodejs \
        npm \
        python3 \
        py3-pip \
        ca-certificates \
        groff \
        less \
        bash \
        make \
        curl \
        wget \
        zip \
        && \
    update-ca-certificates && \
    npm install -g aws-cdk@${AWS_CDK_VERSION}

RUN mkdir -p /repo/deploy
WORKDIR /repo/deploy
COPY requirements.txt /repo/deploy/requirements.txt
RUN python3 -m pip install -r requirements.txt

VOLUME [ "/root/.aws" ]

ENTRYPOINT ["cdk"]
