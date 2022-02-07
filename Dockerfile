FROM continuumio/anaconda3:latest

WORKDIR /home/cartblanche22

COPY app app
COPY application.py config.py boot.sh requirements.txt ./

RUN chmod +x boot.sh

RUN conda create -c rdkit -n cartblanche-rdkit-env rdkit -y
RUN echo "conda activate cartblanche-rdkit-env" > ~/.bashrc
ENV PATH /opt/conda/envs/cartblanche-rdkit-env/bin:$PATH
RUN pip install -r requirements.txt

RUN apt-get install -y --no-install-recommends software-properties-common
RUN add-apt-repository -y ppa:openjdk-r/ppa
RUN apt-get update
RUN apt-get install -y openjdk-8-jdk
RUN apt-get install -y openjdk-8-jre
RUN apt-get vim

RUN update-alternatives --config java
RUN update-alternatives --config javac

EXPOSE 5000

ENTRYPOINT ["./boot.sh"]