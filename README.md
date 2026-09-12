# Credit - Flask-приложение для заявок на кредит

## Начальные требования

- Установлен Python 3.13 и выше
- установлен git

## Установка uv для удобной работы с python

- Linux / macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Клонирование репозитория

```bash
git clone https://github.com/sashagra/credit.git # скачать проект к себе
cd credit # войти в папку с проектом
```

## Установка зависимостей

```bash
uv sync                       # установка зависимостей
uv add --dev pytest           # pytest для тестов (опционально)
```

## Команды

- `uv run flask --app main run` - запуск сервера (Открыть в браузере http://127.0.0.1:5000)
- `uv run pytest -v` - запустить тесты (7 тестов, опцаонально)
- `uv run cli.py list` - список заявок в терминале (если работает сервер, то открыть отдельное окно)
- `uv run cli.py set-status <id> <статус>` - сменить статус заявки

## Как работает

- SQLite-база `credit.db` с таблицей `applications`
- Главная "/" - приветствие
- "/apply" - подача заявки (имя, сумма, срок). После успешной подачи создаётся cookie `current_app_id`
- "/applications" - список заявок с AJAX-обновлением каждые 10 сек. Смена статуса убрана (делает другой сервис)
- "/api/applications" - получение списка, PATCH для смены статуса
- Когда статус заявки меняется на "одобрено" или "отклонено", показывается alert, cookie удаляется
- На всех страницах навигационное меню
