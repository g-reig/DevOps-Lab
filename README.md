# DevOps-Lab
Simple laboratory to try DevOps concepts

# Infrastructure

## Machine list
For now there are the following machines in the network:

| Machine       | Service         | IP        |
|---------------|-----------------|-----------|
| linuxtemplate | Template        | 10.0.3.2  |
| loadb         | Load balancer   | 10.0.3.9  |
| web1          | Serve a web app | 10.0.3.10 |

## Networking documentation
Use netplan to change the network configuration.
```
network:
    ethernets:
        enp0s3:
        dhcp4: false
        addresses:
        -   10.0.3.2/24
        gateway4: 10.0.3.1
        nameservers
            addresses: [8.8.8.8]
    version: 2
```
Then run:
```bash
sudo netplan try
sudo netplan apply
```

# Load Balancer
The load balancer used is HAProxy, which can be installed using `sudo apt install haproxy`.

Currently it is configured to balance the traffic between two servers, which right now are just two Docker instances listening in different ports. 

Configuring the proxy only requires to copy the file loadbalancer/haproxy.cfg to /etc/haproxy/haproxy.cfg and then restarting the service using `sudo systemctl restart haproxy`.

It is missing balancing the traffic between different servers.

## TLS Configuration
The first thing that is needed to configure TLS is a public/private key pair. As this is a development environment I've generated the pair (and a self signed certificate) using the following commands:

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes
cat cert.pem key.pem >> full.pem
```

Then I've moved the resulting file to the /etc/ssl/private/ directory and added the following lines to the configuration file, in the frontend section: 

```
bind 10.0.0.3:443 ssl crt /etc/ssl/private/haproxy.key
redirect scheme https if !{ ssl_fc }
```

## L7 capabilities
HAProxy allows to read application level information, such as headers or the path of the HTTP request. In my case I have used the path of the request to select to which backend it should be sent. If the path begins with /bye it gets send to the byeservers backend, otherwise it gets send to the webservers backend.

To configure this I've added a new backend section and a rule in the frontend to match with the path.

```
frontend myfrotend
#...
        use_backend byeservers if { path_beg /bye }
#...
backend byeservers
        server byeweb1 10.0.3.10:5002
```

# Web Application
It is a simple Flask application which sends "Hello, World from {hostname}!", to check from which server it is being sent. 
There is a second version of it which is exactly the same, but it sends "Bye, World from {hostname}!", to check the L7 capabilities of HAProxy.

## Manual installation (without Docker and Gunicorn)
The installation of the webapp is done using pipenv
```
pip install pipenv
cd webapp
pipenv install
pipenv run flask --app wsgi run
```

## Docker installation
```
sudo docker build -t webapp .
sudo docker run --name webapp --rm -p 5000:5000 -it webapp
```
