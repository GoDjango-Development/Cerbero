# Cerbero
Cerbero is a protocol services monitoring system that is responsible for verifying the proper functioning of the institution's protocol services. Can do reviews of http/s, tcp, icmp, dns, tfprotocol services

## Info
![Badge en Desarollo](https://img.shields.io/badge/STATUS-EN%20DESAROLLO-greem)

##  Project Features

# Help for maintenance and improvements of the product 
### You can donate in BTC to help us maintain and drive these products for the benefit of all of us.

Bitcoin Wallet :coin: : 129ziaFyteW1rGzTcjcPD644fn4RC9ayh9



## Server installations and execution 🔧
_1 - You need to have Python version 3.9 or higher_

_2 - Create the virtual environment_

```
python3 -m venv venv
```

_3 - Activate virtualenv_
#### linux
source venv/bin/activate
#### windows
cd venv/scripts/activate

_4 - Installing project dependencies_

```
pip install -r requirements.txt
```

_5 - create migrations, migrate, createsuperadmin and runserver project_

```
# migrations
python3 manage.py makemigrations

# migrate
python3 manage.py migrate

# createsuperuser
python3 manage.py createsuperuser

# runserver
python3 manage.py runserver


```


_celery_
### windows
celery -A cerbero worker -l info --pool=solo

### linux
celery -A cerbero worker -l info 



## Ejecutando las pruebas ⚙️


##### ns1.google.com. [IP: 216.239.32.10],
##### ns4.google.com. [IP: 216.239.38.10], 
##### ns2.google.com. [IP: 216.239.34.10], 
##### ns3.google.com. [IP: 216.239.36.10],
##### ns-cloud-b2.googledomains.com   149.154.167.99 
##### 216.155.132.172

