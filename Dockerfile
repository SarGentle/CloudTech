FROM python:3.10.13-bullseye

RUN apt-get update

RUN apt-get update && \
    apt-get install -y wget && \
    wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add - && \
    echo "deb http://repo.mongodb.org/apt/debian bullseye/mongodb-org/5.0 main" > /etc/apt/sources.list.d/mongodb-org-5.0.list && \
    apt-get update && \
    apt-get install -y mongodb-org

RUN apt-get install git -y

RUN git clone https://github.com/SarGentle/CloudTech.git

WORKDIR /CloudTech

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["bash", "-c", "systemctl", "start", "mongod"]

CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080"]
