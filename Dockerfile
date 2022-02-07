FROM continuumio/anaconda3:latest

WORKDIR /home/cartblanche22

COPY app app
COPY application.py config.py boot.sh requirements.txt ./

RUN chmod +x boot.sh

RUN conda create -c rdkit -n cartblanche-rdkit-env rdkit -y
RUN echo "conda activate cartblanche-rdkit-env" > ~/.bashrc
ENV PATH /opt/conda/envs/cartblanche-rdkit-env/bin:$PATH
RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y ant && \
    apt-get clean;
    
RUN apt-get update && \
    apt-get install ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f;

ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME
    
RUN apt-get install -y vim

RUN update-alternatives --config java
RUN update-alternatives --config javac

EXPOSE 5000

ENTRYPOINT ["./boot.sh"]