mkdir "private" "certs"
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/taged/private/nginx-selfsigned.key -out /etc/ssl/taged/certs/nginx-selfsigned.crt
sudo openssl dhparam -out /etc/ssl/taged/certs/dhparam.pem 2048
