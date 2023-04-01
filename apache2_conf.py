
import pathlib
import os
import sys
from root.main import settings

project_name = "DjangoGramm"
project_root = pathlib.Path(__file__).parent / 'root'
venv_path = pathlib.Path(__file__).parent / 'venv'


apache2_http = f"""

<VirtualHost *:80>
ServerAdmin {settings.EMAIL_HOST_USER}
DocumentRoot /var/www/html

ServerName {settings.ALLOWED_HOSTS[0]}
ServerAlias www.{settings.ALLOWED_HOSTS[0]}

ErrorLog ${{APACHE_LOG_DIR}}/error.log
CustomLog ${{APACHE_LOG_DIR}}/access.log combined

Alias /static {settings.STATIC_ROOT}
<Directory {settings.STATIC_ROOT}>
        Require all granted
</Directory>

Alias /media {settings.MEDIA_ROOT}
<Directory {settings.MEDIA_ROOT}>
    Require all granted
</Directory>

<Directory {project_root / 'main'}>
    <Files wsgi.py>
        Require all granted
    </Files>
</Directory>

WSGIDaemonProcess {project_name} python-home={venv_path} python-path={project_root}	
WSGIProcessGroup {project_name}
WSGIScriptAlias / {project_root / 'main' / 'wsgi.py'}

</VirtualHost>
"""

apache2_https = f"""
<VirtualHost *:443>

ServerAdmin {settings.EMAIL_HOST_USER}
DocumentRoot /var/www/html

ServerName {settings.ALLOWED_HOSTS[0]}
ServerAlias www.{settings.ALLOWED_HOSTS[0]}

ErrorLog ${{APACHE_LOG_DIR}}/error.log
CustomLog ${{APACHE_LOG_DIR}}/access.log combined

Alias /static {settings.STATIC_ROOT}
<Directory {settings.STATIC_ROOT}>
    Require all granted
</Directory>

Alias /media {settings.MEDIA_ROOT}
<Directory {settings.MEDIA_ROOT}>
    Require all granted
</Directory>

<Directory {project_root / 'main'}>
    <Files wsgi.py>
        Require all granted
    </Files>
</Directory>

WSGIProcessGroup {project_name}
WSGIScriptAlias / {project_root / 'main' / 'wsgi.py'}

</VirtualHost>
"""

apache2_config = apache2_http + apache2_https

with pathlib.Path('/etc/apache2/sites-available/000-default.conf').open(mode='w') as config_file:
    config_file.write(apache2_config)
