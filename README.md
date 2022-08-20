# praktikum_new_diplom

# Проект Foodgram
[![foodgram_workflow](https://github.com/Grizzzley/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/Grizzzley/foodgram-project-react/actions/workflows/foodgram_workflow.yml)
## Адрес развернутого проекта
http://84.201.167.163

## Описание

Cайт Foodgram - онлайн-сервис, на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии
* Django
* Django rest framework
* Djoser
* Postgresql
* Docker Compose
* Nginx
* Gunicorn


## Автор

[Михаил Васильев](https://github.com/Grizzzley)


## Ресурсы API Foodgram

- Ресурс auth: аутентификация.
- Ресурс users: пользователи.
- Ресурс tags: получение данных тега или списка тегов рецепта.
- Ресурс recipes: создание/редактирование/удаление рецептов, а также получение списка рецептов или данных о рецепте.
- Ресурс shopping_cart: добавление/удаление рецептов в список покупок.
- Ресурс download_shopping_cart: cкачать файл со списком покупок.
- Ресурс favorite: добавление/удаление рецептов в избранное пользователя.
- Ресурс subscribe: добавление/удаление пользователя в подписки.
- Ресурс subscriptions: возвращает пользователей, на которых подписан текущий пользователь. В выдачу добавляются рецепты.
- Ресурс ingredients: получение данных ингредиента или списка ингредиентов.


 ## Установка

Soon..



## Примеры

Примеры запросов по API:

- [GET] /api/users/ - Получить список всех пользователей.
- [POST] /api/users/ - Регистрация пользователя.
- [GET] /api/tags/ - Получить список всех тегов.
- [POST] /api/recipes/ - Создание рецепта.
- [GET] /api/recipes/download_shopping_cart/ - Скачать файл со списком покупок.
- [POST] /api/recipes/{id}/favorite/ - Добавить рецепт в избранное.
- [DEL] /api/users/{id}/subscribe/ - Отписаться от пользователя.
- [GET] /api/ingredients/ - Список ингредиентов с возможностью поиска по имени.


