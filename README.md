# Проект Foodgram - сайт для публикации рецептов

На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а также скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Запуск проекта на локальной машине:

Клонировать репозиторий:
```
git clone git@github.com:Nurbek878/foodgram-project-react.git
```
В директории infra создать файл .env и заполнить такими данными:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='YOUR SECRET_KEY'
```
Создать и запустить контейнеры Docker, выполнив следующую команду в папке infra
```
sudo docker compose up -d
```
Произвести миграции, собрать статике и создать суперпользователя
```
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic --no-input
sudo docker compose exec backend python manage.py createsuperuser
```
Загрузить ингредиенты:
```
sudo docker compose exec backend python manage.py loaddata ingredients.json
```
После запуска проект будут доступен по адресу: [http://localhost/](http://localhost/)

Документация будет доступна по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)

Админка будет доступна по адресу: [http://localhost/admin/](http://localhost/admin/)



### Автор:
[@nurbek878](https://github.com/Nurbek878)
