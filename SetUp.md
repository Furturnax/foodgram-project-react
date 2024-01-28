## Развёртывание проекта:
+ Клонировать репозиторий и перейти в него в командной строке:
```shell script
git clone git@github.com:Furturnax/foodgram-project-react.git
```

```shell script
cd foodgram-project-react/
```

+ Cоздать и активировать виртуальное окружение `(Windows/Bash)`:
```shell script
cd backend/
```

```shell script
python -m venv venv
```

```shell script
source venv/Scripts/activate
```

+ Установить зависимости из файла `requirements.txt`:
```shell script
python -m pip install --upgrade pip
```

```shell script
pip install -r requirements.txt
```

+ Установите [Docker compose](https://www.docker.com/) на свой компьютер.

+ Запустите проект через `docker-compose`:
```shell script
cd foodgram-project-react/infra
```
+ Создать файл `.env` с переменными окружения в `infra`:

[Примеры переменных окружения](./infra/.env.example)

```shell script
docker compose -f docker-compose.production.yml up --build -d
```

+ Выполнить миграции:
```shell script
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

+ Соберите статику:
```shell script
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

+ Скопируйте статику:
```shell script
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /app/static/
```

<br>

## Развёртывание на удаленном сервере:
#### Подготовка Docker образов:
+ Включить установленный ранее `Docker`.
+ Залогиниться в свой аккаунт:
```shell script
docker login
```

+ Создать образы контейнеров `Backend`, `Frontend` из главной директории в локальном проекте (`BD` и `Nginx` создадутся автоматически):
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
    server_name <your-ip> <your-domen?;
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

## Порядок запросов к API:
Для работы понадобится программа **Postman**. Она существует в `desktop` и `web` версии. Она удобна функционалом. Либо использовать стандартный интерфейс `DRF` без установки дополнительного ПО. 

Superuser создан ранее.

Получить JWT-токен через **Postman**.  
+ По адресу https://foodgramdrew.webhop.me/api/auth/token/login/, через POST запрос передать данные в формате `JSON`:
```
{
    "email": "email",
    "password": "password"
}
```

Авторизировать токен во вкладке **Headers**.
- В разделе **Key** указать `Authorization`;
- В разделе **Value** указать `Token <auth_token>`;
- Выполнять запросы к `API`, описанных в документации. 

<br>

## Работа с SPA приложением:

#### Данные для входа:
Пожалуйста, не надо делать плохие посты, или потрить, что либо. Оставайтесь хорошими булочками :3
```
# Superuser
furturnax@gmail.com
123123qQq

# Staffuser
sosogeg@gmail.com
123123qQq

# Users
gorgekeln@gmail.com
123123qQq

annarose@gmail.com
123123qQq

alisablade@gmail.com
123123qQq

```

#### Доступные ресурсы:
https://foodgramdrew.webhop.me/recipes - Основной ресурс.

https://foodgramdrew.webhop.me/admin/ - Административная панель.

https://foodgramdrew.webhop.me/api/ - API.

https://foodgramdrew.webhop.me/api/docs/ - Документация к API.