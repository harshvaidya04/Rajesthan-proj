#!/bin/bash
CONFIG_FILE=/etc/apache2/sites-available/deploy_attendance_app.conf

# Write Apache config
echo "
<VirtualHost *:80>
    ServerName <domain or ip address>
    Redirect / https://<domain or ip address>
</VirtualHost> 

<VirtualHost *:443>
    ServerName <domain or ip address>
    SSLEngine on
    SSLProxyEngine On
    SSLCertificateFile      /etc/ssl/certs/ssl-cert-snakeoil.pem
    SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key

    ProxyRequests     Off
    ProxyPreserveHost On
    <Proxy *>
        Order deny,allow
        Allow from all
    </Proxy>

    ProxyPass         /_stcore        ws://localhost:8501/_stcore
    ProxyPassReverse  /_stcore        ws://localhost:8501/_stcore

    ProxyPass         /        http://localhost:8000/
    ProxyPassReverse  /        http://localhost:8000/
</VirtualHost>" > $CONFIG_FILE

# Enable site and reload Apache
a2ensite deploy_attendance_app.conf
systemctl reload apache2
