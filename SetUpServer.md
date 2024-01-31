## Руководство по развёртыванию проекта на удаленном сервере:

[Руководство по развёртыванию проекта локально](./SetUpLocal.md)

#### Подготовка Docker образов:

+ Включить установленный ранее `Docker`.
+ Залогиниться в свой аккаунт:
```shell script
docker login
```

+ Создать образы контейнеров `Backend`, `Frontend` из главной директории в локальном проекте (`DB` и `Nginx` создадутся автоматически):
```shell script
docker build -t <your-docker-username>/foodgram_backend backend/
```

```shell script
docker push <your-docker-username>/foodgram_backend
```

```shell script
docker build -t <your-docker-username>/foodgram_frontend frontend/
```

```shell script
docker push <your-docker-username>/foodgram_frontend
```

#### Подготовка сервера:
Установить `Docker` на сервер:
```shell script
sudo apt update
```

```shell script
sudo apt --fix-broken install
```

```shell script
sudo apt install curl
```

```shell script
curl -fSL https://get.docker.com -o get-docker.sh
```

```shell script
sudo sh ./get-docker.sh
```

```shell script
sudo apt-get install docker-compose-plugin
```

Настроить `Nginx` на сервере:
```shell script
sudo apt install nginx -y
```

```shell script
sudo systemctl start nginx
```

```shell script
sudo nano /etc/nginx/sites-enabled/default
```

+ Добавить конфигурации:
```
server {
    server_name <your-ip> <your-domen>;
    server_tokens off;

    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }
}
```
```shell script
sudo nginx -t
```

```shell script
sudo service nginx reload
```

+ Проверить работоспособность:
```shell script
sudo systemctl status nginx
```

Получить `SSl` сертификат:
+ Настраить `Firewall`:
```shell script
sudo ufw allow 'Nginx Full'
```

```shell script
sudo ufw allow OpenSSH
```

```shell script
sudo ufw enable
```

+ Установить `Certbot`:
```shell script
sudo apt install snapd 
```

```shell script
sudo snap install core; sudo snap refresh core
```

```shell script
sudo snap install --classic certbot
```

```shell script
sudo ln -s /snap/bin/certbot /usr/bin/certbot 
```

```shell script
sudo certbot --nginx 
```

+ Автопродление сертификата:
```shell script
sudo certbot certificates
```

```shell script
sudo certbot renew --dry-run 
```

```shell script
sudo certbot renew --pre-hook "service nginx stop" --post-hook "service nginx start" 
```

Работа с директорией на удаленном сервере:
+ Создать директорию:
```shell script
mkdir foodgram
```

+ Отправить `.env`, `docker-compose.production.yml`, `nginx.conf` из директории `infra` на ваш удаленный сервер используя `SCP`:
```shell script
scp -i <путь к ключам сервера> .env <login@ip>:<путь к директории на сервере>/.env
```
```shell script
scp -i <путь к ключам сервера> docker-compose.production.ym <login@ip>:<путь к директории на сервере>/docker-compose.production.yml
```
```shell script
scp -i <путь к ключам сервера> nginx.conf <login@ip>:<путь к директории на сервере>/nginx.conf
```

+ Перейти в директорию:
```shell script
cd foodgram/
```
Запуск проекта на сервере:
+ Запустить `Docker` контейнеры:
```shell script
scp -i sudo docker compose -f docker-compose.production.yml up -d
```
+ Настроить `Backend`:
```shell script
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

```shell script
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

```shell script
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /app/static/
```

```shell script
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

+ Загрузить список ингредиентов в базу данных:
```shell script
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_csv
```

+ Проверить, что контейнеры работают:
```shell script
scp -i sudo docker compose -f docker-compose.production.yml ps
```

+ Полезные команды:
```shell script
# Выключение контейнеров
sudo docker compose -f docker-compose.production.yml down

# Удаление всех образов для перезаписи
sudo docker rmi -f $(sudo docker images -q)

# Загрузка образов с DockerHub
sudo docker pull <your-docker-username>/foodgram_backend
```

[Порядок запросов к API](./SetUpAPI.md)
