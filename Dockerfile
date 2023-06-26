# syntax=docker/dockerfile:1.4

FROM node:16.19.1-alpine as frontend
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json ./
RUN npm install --force
COPY ./src ./src
COPY ./public ./public
RUN yarn build

FROM continuumio/anaconda3:latest as backend

WORKDIR /home/cartblanche22

ADD backend/application.py backend/config.py  backend/requirements.txt ./
RUN conda create -c rdkit -n cartblanche-rdkit-env rdkit python=3.7 -y
RUN echo "conda activate cartblanche-rdkit-env" > ~/.bashrc
ENV PATH /opt/conda/envs/cartblanche-rdkit-env/bin:$PATH
RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean;

RUN apt-get install -y vim
RUN apt-get install -y rabbitmq-server

COPY --from=frontend /app/build ../build
ADD backend ./
ADD backend/boot-test.sh backend/boot.sh ./

ARG BOOT_SCRIPT=$BOOT_SCRIPT
ENV BOOT_SCRIPT=$BOOT_SCRIPT

RUN chmod +x boot.sh
RUN chmod +x boot-test.sh
EXPOSE 5000
EXPOSE 5555


ENTRYPOINT "./$BOOT_SCRIPT.sh"
