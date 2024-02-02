[Руководство по развёртыванию проекта локально](./SetUpLocal.md)

[Руководство по развёртыванию проекта на удаленном сервере](./SetUpServer.md)

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
