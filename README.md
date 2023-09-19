[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/event_backend
ExecStart=/home/ubuntu/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          backend.wsgi:application

[Install]
WantedBy=multi-user.target


server {
    listen 80;
    server_name 3.110.115.0;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/ubuntu/event_backend;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}

sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled