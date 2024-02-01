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
mkdir foodgram/
```
+ Создать директорию внутри `foodgram`:
```shell script
mkdir infra/
```

+ Отправить `.env`, `docker-compose.production.yml`, `nginx.conf` из директории `infra` на ваш удаленный сервер используя `SCP` в директорию `foodgram/infra/`:
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
cd foodgram/infra/
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

<br>

## Workflows:

Continuous Integration (CI) и Continuous Deployment (CD) реализовано через `GitHub Actions` 

Для работы проекта необходимо прописать переменные окружения в `Settings/Secrets and variables/Actions/New repository secret`:

```txt
# имя пользователя в Docker
NICKNAME

# имя пользователя в DockerHub
DOCKER_USERNAME    

# пароль пользователя в DockerHub
DOCKER_PASSWORD    

# ip_address сервера
SSH_HOST      

# имя пользователя                     
SSH_USER    

# приватный ssh-ключ (cat ~/.ssh/id_rsa)
SSH_KEY    

# пароль для ssh-ключа            
SSH_PASSPHRASE                   

# id телеграм-аккаунта (@userinfobot)
TELEGRAM_TO      

# токен вышего бота (@BotFather)
TELEGRAM_TOKEN                 
```

При `push` в ветку `main` автоматически отрабатывают сценарии:

+ `Tests 3.9, 3.10, 3.11` - проверка кода на соответствие стандарту `PEP8`;
+ `Push Docker image to DockerHub` - сборка и доставка докер-образов на DockerHub;
+ Безопасное копирование `docker-compose.production.yml` и `nginx.conf`;
+ `Deploy` - автоматический деплой проекта на рабочий сервер;
+ `Send message` - отправка уведомления в Telegram.

[Порядок запросов к API](./SetUpAPI.md)
