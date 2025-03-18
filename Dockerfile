# syntax=docker/dockerfile:1.4.0

FROM node:19.9.0 as frontend
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json ./
RUN npm install
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
    apt-get install -y default-jre && \
    apt-get clean;

RUN apt-get install -y vim
RUN apt-get install -y rabbitmq-server
RUN apt-get install gcc g++ -y
RUN apt-get install git -y

ARG SW_GIT_REPO=$SW_GIT_REPO
ARG SW_GIT_KEY=$SW_GIT_KEY

RUN git clone https://oauth2:${SW_GIT_KEY}@${SW_GIT_REPO} smallworld 
ENV SW_INSTAL_DIR=/home/cartblanche22/smallworld
RUN pip install /home/cartblanche22/smallworld/python

COPY --from=frontend /app/build ../build
ADD backend ./
ADD backend/boot-test.sh backend/boot.sh ./

ARG BOOT_SCRIPT=$BOOT_SCRIPT
ENV BOOT_SCRIPT=$BOOT_SCRIPT

RUN chmod +x boot.sh
RUN chmod +x boot-test.sh
EXPOSE 5000
EXPOSE 5555
ENTRYPOINT "./boot.sh"
