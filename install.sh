# !/bin/sh 
sudo apt-get update -y 
sudo apt-get install python3-pip -y 
pip3 install pytest==5.3.1 urllib3==1.25.7 Flask==1.1.1 Flask-HTTPAuth==3.3.0 flask-marshmallow==0.10.1 Flask-Migrate==2.5.2 Flask-Script==2.0.6 Flask-SQLAlchemy==2.4.1 Flask-Testing==0.8.0 marshmallow==3.2.2
cd /home/labuser/Desktop/Project/t4_ecommerce_flaskh/ecommerceapp;
export FLASK_APP=main.py;
python3 -m flask seeddata
