FROM continuumio/anaconda3:latest

WORKDIR /home/cartblanche22

COPY requirements.txt .

RUN conda create -c rdkit -n cartblanche-rdkit-env rdkit -y
RUN echo "conda activate cartblanche-rdkit-env" > ~/.bashrc
ENV PATH /opt/conda/envs/cartblanche-rdkit-env/bin:$PATH
RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean;

COPY app app
COPY application.py config.py boot.sh requirements.txt ./
RUN chmod +x boot.sh

EXPOSE 5000

ENTRYPOINT ["./boot.sh"]
