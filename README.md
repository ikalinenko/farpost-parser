# Парсер шин и дисков сервиса [FarPost.ru](https://farpost.ru)

Парсит шины и диски из каталогов [FarPost.ru](https://farpost.ru) и отправляет конечные `.xml` файлы на электронную почту.

## Настройка

1. Скопируйте `.env.example` в `.env` и отредактируйте `.env` файл, заполнив в нём все переменные окружения:
    ```bash
    cp .env.example .env
    ```
2. Создайте 2 директории `input` и `output` в корне проекта:
    ```bash
    mkdir input output
    ```
3. Скопируйте `links.example.csv` в `input/links.csv` и и отредактируйте файл `input/links.csv`, заполнив в нем ссылки на каталоги, которые необходимо спарсить:
    ```bash
    cp links.example.csv input/links.csv
    ```
4. Скопируйте `proxies.example.csv` в `input/proxies.csv` и отредактируйте файл `input/proxies.csv`, заполнив в нем все прокси, которые будут использоваться в процессе парсинга (на каждую ссылку не менее 1 прокси):
    ```bash
    cp proxies.example.csv input/proxies.example.csv
    ```

## Запуск
- Через `Docker Compose`:
   ```bash
    docker-compose up -d
    ```
- Без использования `Docker Compose`:
  1. Установить [Poetry](https://python-poetry.org/).
  2. Выполнить запуск:
     ```bash
     poetry run python -m main.py
     ```

  ### Аргументы командной строки
    В случае, если необходимо выполнить парсинг только по одной ссылке из файла `input/links.csv`, можно выполнить команду:
    ```bash
    poetry run python -m main.py --link-id={link_id} --proxy-id={proxy_id}
    ```
    где, `link_id` — это `id` ссылки, которую необходимо спарсить из файла `input/links.csv`, а `proxy_id` — это `id` прокси из файла `input/proxies.csv`, который необходимо использовать во время парсинга ссылки.

    Для запуска из `Docker` контейнера можно использовать команду:
    ```bash 
    docker exec -d farpost_parser python -m main.py --link-id={link_id} --proxy-id={proxy_id}
    ```

## Crontab
Для запуска парсера по расписанию необходимо добавить в `crontab` следующие команды:
- Если парсер запускается через `Docker`:
    ```bash
   docker start farpost_parser
    ```
- Если парсер запускается через `Poetry`:
    ```bash
   poetry run python -m /path/to/parser_root/main.py
    ```

## Логирование
Для анализа отладочной информации логи сохраняются в файл `root.log`. Ротация логов происходит каждые `n` часов, указанных в конфигурации `.env`, максимальное количество бэкапов — 5.