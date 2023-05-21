fuser -k 5000/tcp; # kill the process if the port is already in use
cd /home/labuser/Desktop/Project/t4_ecommerce_flaskh/ecommerceapp;
export FLASK_APP=main.py;
python3 -m flask run;
