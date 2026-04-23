# End-to-End LLM Service

Production-like микросервис для обработки текста с использованием LLM (GigaChat-совместимый). Реализует суммаризацию/генерацию ответов, кеширование с TTL, обработку ошибок, CI-пайплайн и безопасное управление конфигурацией.

## Пользовательский сценарий
Сервис принимает произвольный текст, передаёт его в LLM для краткой суммаризации или генерации ответа, кэширует результат и возвращает пользователю. При недоступности внешнего провайдера автоматически возвращается fallback-ответ.

## Архитектура
```
[HTTP Client] → POST /api/v1/process
        ↓
[FastAPI Router] → Валидация входных данных (Pydantic)
        ↓
[Business Logic] → Проверка кеша → Вызов LLM → Пост-обработка
        ↓
[LLM Adapter]   → OAuth2-авторизация → HTTP-вызов модели → Ретраи (tenacity)
        ↓
[Cache]         → In-memory хранилище с TTL
        ↓
[Response]      → JSON с полем source: "llm" | "cache" | "fallback"
```

### Разделение функционала
- `api/` – HTTP-эндпоинты, маршрутизация
- `services/` – бизнес-логика, клиент LLM, кеш, пост-обработка
- `core/` – конфигурация из `.env`, структурированное логирование
- `models/` – схемы валидации и ответов
- `tests/` – интеграционные и модульные тесты
- `.github/workflows/` – CI-пайплайн (линтер + тесты)

## Быстрый старт

### 1. Подготовка окружения
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Настройка конфигурации
```bash
cp .env.example .env
# Откройте .env и вставьте реальные учётные данные провайдера
```

### 3. Запуск сервиса
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Swagger UI доступен по адресу: `http://localhost:8000/docs`

## API Reference

### `POST /api/v1/process`
Обработка текста с использованием LLM.

**Request: (Пример)**
```json
{
  "text": "Кратко опиши, что такое бизнес-информатика"
}
```

**Response (успех):**
```json
{
  "result": "Бизнес-информатика — это направление на стыке IT и менеджмента...",
  "source": "llm",
  "metadata": { "cached": false }
}
```

**Response (кеш):**
```json
{
  "result": "...",
  "source": "cache",
  "metadata": { "cached": true }
}
```

**Response (fallback при сбое провайдера):**
```json
{
  "result": "Сервис временно недоступен. Пожалуйста, попробуйте позже.",
  "source": "fallback",
  "metadata": { "error": "HTTPStatusError: 401 Unauthorized" }
}
```

## Тестирование сценариев

| Сценарий | Как проверить | Ожидаемый результат |
|----------|--------------|-------------------|
| ✅ Успешный запрос | Валидный текст > 5 символов | `source: "llm"`, ответ от модели |
| ❌ Валидация | `{"text": "аб"}` | Статус `422`, ошибка Pydantic |
| 🔄 Fallback | Неверные/пустые ключи в `.env` | `source: "fallback"`, статус `200` |
| ⚡ Кеш | Одинаковый запрос дважды | 1-й: `Cache MISS`, 2-й: `Cache HIT` в логах |

> Сервис спроектирован устойчиво к сбоям внешних зависимостей. Отсутствие ответа от LLM не приводит к падению приложения, а корректно обрабатывается через fallback-механизм.

## Конфигурация и безопасность
- Все параметры вынесены в переменные окружения (`pydantic-settings`)
- Секреты не хранятся в репозитории (`.env` в `.gitignore`)
- Присутствует `.env.example` с шаблоном переменных
- CI-пайплайн автоматически проверяет линтинг и запускает тесты

## Демонстрация работы
*(Замените эти плейсхолдеры на реальные скриншоты перед отправкой)*

![Swagger UI](https://github.com/VladKoretski/LLM_service/blob/main/docs/swaggerPost.png)  
![Fallback ответ](https://github.com/VladKoretski/LLM_service/blob/main/docs/logCash.png)  
![Логи кеша](https://github.com/VladKoretski/LLM_service/blob/main/docs/logCash.png)  
  
## Лицензия
MIT. Образовательный проект.
