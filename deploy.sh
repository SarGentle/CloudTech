#/bin/bash

sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.10 -y
sudo apt install python3.10-venv -y

git clone https://github.com/nottolstybai/DemidovCourse.git

sudo apt install mongodb-org-community
sudo systemctl start mongod
sudo systemctl status mongod

bash -c "cd CloudTech && python3.10 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8080 --reload"