# Деплой Telegram бота на Render.com

## ⚠️ ВАЖНО: Исправления для Render

Проблема с ошибкой `AttributeError: 'Updater' object has no attribute '_Updater__polling_cleanup_cb'` решена следующими изменениями:

1. **Используется Python 3.11** вместо 3.13
2. **Обновлены версии библиотек** для совместимости
3. **Создан `app.py`** который объединяет веб-сервер и бота
4. **Добавлен health check endpoint** для Render
5. **Убран `job_queue`** который вызывал проблемы на Render

## Подготовка к деплою

### 1. Создайте Git репозиторий

```bash
git init
git add .
git commit -m "Initial commit"
```

### 2. Загрузите код на GitHub/GitLab

Создайте репозиторий на GitHub и загрузите туда ваш код:

```bash
git remote add origin https://github.com/your-username/your-repo-name.git
git branch -M main
git push -u origin main
```

## Деплой на Render.com

### 1. Создайте аккаунт на Render.com
- Перейдите на https://render.com
- Зарегистрируйтесь через GitHub

### 2. Создайте новый Web Service
- Нажмите "New +" → "Web Service"
- Подключите ваш GitHub репозиторий
- Выберите репозиторий с ботом

### 3. Настройте сервис

**Основные настройки:**
- **Name**: `telegram-help-bot` (или любое другое)
- **Environment**: `Python 3`
- **Region**: Выберите ближайший к вам регион
- **Branch**: `main`
- **Root Directory**: оставьте пустым

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python app.py
```

### 4. Настройте переменные окружения

В разделе "Environment Variables" добавьте:

| Key | Value | Description |
|-----|-------|-------------|
| `TELEGRAM_TOKEN` | Ваш токен бота | Токен от @BotFather |
| `OPENAI_API_KEY` | Ваш OpenAI ключ | Ключ API OpenAI |

### 5. Настройки плана
- **Plan**: Free (бесплатный план)
- **Auto-Deploy**: Enabled (включить автоматический деплой)

### 6. Запустите деплой
- Нажмите "Create Web Service"
- Дождитесь завершения сборки и деплоя

## Проверка работы

### 1. Проверьте логи
- В Render Dashboard перейдите в ваш сервис
- Откройте вкладку "Logs"
- Убедитесь, что нет ошибок

### 2. Проверьте health check
- Откройте URL вашего сервиса (например: https://your-app.onrender.com)
- Должно появиться сообщение "Telegram Bot is running!"

### 3. Проверьте бота
- Найдите ваш бот в Telegram
- Отправьте команду `/start`
- Убедитесь, что бот отвечает

## Структура файлов

```
├── app.py              # Основной файл для Render (веб-сервер + бот)
├── main.py             # Оригинальный файл бота
├── db.py               # Работа с базой данных
├── requirements.txt    # Зависимости Python
├── render.yaml         # Конфигурация Render
├── Procfile           # Альтернативная конфигурация
├── runtime.txt        # Версия Python
├── health_check.py    # Простой health check
└── README_DEPLOY.md   # Эти инструкции
```

## Важные замечания

### База данных
- SQLite база данных (`helpers.db`) будет создана автоматически
- Данные сохраняются в файловой системе сервера
- При перезапуске сервиса данные сохраняются

### Ограничения бесплатного плана
- 750 часов работы в месяц
- Автоматическое "засыпание" после 15 минут неактивности
- Пробуждение при первом запросе (может занять 30-60 секунд)

### Мониторинг
- Регулярно проверяйте логи в Render Dashboard
- Настройте уведомления о сбоях

## Troubleshooting

### Ошибка AttributeError с Updater
**Решение**: 
1. Используйте `app.py` вместо `main.py` 
2. Убедитесь, что используется Python 3.11
3. Убран `job_queue` - команды меню устанавливаются при первом использовании

### Бот не отвечает
1. Проверьте логи в Render Dashboard
2. Убедитесь, что токен бота правильный
3. Проверьте, что бот не заблокирован

### Ошибки сборки
1. Проверьте `requirements.txt`
2. Убедитесь, что все зависимости указаны
3. Проверьте версию Python в `runtime.txt`

### Проблемы с базой данных
1. Убедитесь, что файл `db.py` загружен
2. Проверьте права доступа к файловой системе

## Альтернативы

### Если нужен Jobs план
Если вы хотите использовать Jobs вместо Web Service:

1. Создайте **Background Worker** вместо Web Service
2. Измените Start Command на: `python main.py`
3. Это даст вам больше ресурсов, но менее подходит для Telegram бота

### Если нужен PostgreSQL
Для продакшена рекомендуется использовать PostgreSQL:

1. Создайте PostgreSQL сервис в Render
2. Измените `db.py` для работы с PostgreSQL
3. Добавьте `psycopg2-binary` в `requirements.txt`

## Контакты для поддержки

При возникновении проблем:
1. Проверьте документацию Render: https://render.com/docs
2. Обратитесь в поддержку Render
3. Проверьте логи и статус сервиса 