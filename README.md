# Social Network

### Разработчик проекта: Лоскутова Татьяна (Loskutova Tatiana)

### Назначение проекта
Данный проект представляет собой  web приложение YaMDb. Он предоставляет возможность пользователям публиковать посты, оставлять комментарии под ними, добавлять картинки.

### Технологический стек
- Python - основной язык программирования.
- Django - фреймворк для разработки веб-приложений.
- GIT - система контроля версий проекта
- Pytest - инструмент для тестирования проекта

### Как запустить проект:

**1)** Клонировать репозиторий и перейти в него в командной строке:

    git clone https://github.com/TatianaLoskutova/Social_network_for_posts-Django-/

    cd blogicum

**2)** Cоздать и активировать виртуальное окружение:
    
    python -m venv venv

    venv/Scripts/activate

**3)** Установить зависимости из файла requirements.txt:
    
    python -m pip install --upgrade pip

    pip install -r requirements.txt

**4)** Выполнить миграции:
    
    cd blogicum

    python manage.py migrate
    
**5)** Запустить проект:

    python manage.py runserver
