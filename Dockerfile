FROM continuumio/anaconda3:latest

WORKDIR /home/cartblanche22

COPY app app
COPY application.py config.py boot.sh requirements.txt ./

RUN chmod +x boot.sh

RUN conda create -c rdkit -n cartblanche-rdkit-env rdkit -y
RUN echo "conda activate cartblanche-rdkit-env" > ~/.bashrc
ENV PATH /opt/conda/envs/cartblanche-rdkit-env/bin:$PATH
RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["./boot.sh"]