FROM python:3.10.13-bullseye

RUN apt-get update && apt-get install -y postgresql

RUN apt-get install git -y

RUN git clone https://github.com/nottolstybai/DemidovCourse.git

WORKDIR /DemidovCourse

RUN pip install -r requirements.txt

EXPOSE 8080

USER postgres

CMD ["bash", "-c", "service postgresql start && psql -U postgres -c \"ALTER USER postgres WITH PASSWORD 'postgres'\" && uvicorn main:app --host 0.0.0.0 --port 8080"]
