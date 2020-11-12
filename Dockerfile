FROM continuumio/miniconda3

WORKDIR /src
COPY environment.yml /src/environment.yml
RUN apt-get update -y && apt install -y freeglut3-dev
RUN conda env create -f environment.yml -n z
SHELL ["conda", "run", "-n", "z", "/bin/bash", "-c"]

COPY . /src
ENTRYPOINT ["conda", "run", "-n", "z", "make"]
