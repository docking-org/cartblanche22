FROM continuumio/anaconda3:latest

WORKDIR /home/cartblanche22

ADD application.py config.py boot.sh requirements.txt ./

RUN conda create -c rdkit -n cartblanche-rdkit-env rdkit -y
RUN echo "conda activate cartblanche-rdkit-env" > ~/.bashrc
ENV PATH /opt/conda/envs/cartblanche-rdkit-env/bin:$PATH
RUN pip install -r requirements.txt
ADD app app
RUN chmod +x boot.sh

RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean;



RUN apt-get install -y vim
RUN apt-get install -y rabbitmq-server

EXPOSE 5000

ENTRYPOINT ["./boot.sh"]