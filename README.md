# Weather DWH

Pet-проект: Data Warehouse для данных о погоде.

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Open-Meteo │────►│   Bronze    │────►│   Silver    │────►│    Gold     │
│     API     │     │  (raw JSON) │     │  (cleaned)  │     │ (aggregates)│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │                   │
                        Airflow              dbt                 dbt
```

**Medallion Architecture:**
- **Bronze** — сырые данные из API (JSONB)
- **Silver** — очищенные, типизированные данные
- **Gold** — агрегаты для аналитики

## Технологии

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Оркестрация | Apache Airflow 2.8 | Запуск ETL по расписанию |
| Трансформации | dbt 1.7 | SQL-модели (Silver, Gold) |
| База данных | PostgreSQL 15 | Хранение данных |
| BI | Metabase | Визуализация |
| Контейнеризация | Docker Compose | Локальный запуск |

## Структура проекта

```
dwh-pet/
├── airflow/
│   ├── Dockerfile           # Образ Airflow с dbt
│   └── dags/
│       └── weather_etl.py   # DAG: API → Bronze → dbt run
├── dbt/
│   ├── profiles.yml         # Подключение к DWH
│   └── weather_dwh/
│       ├── dbt_project.yml
│       └── models/
│           ├── staging/
│           │   ├── sources.yml      # Источник: bronze.raw_weather
│           │   └── stg_weather.sql  # Silver: распаковка JSON
│           └── marts/
│               └── mart_daily_weather.sql  # Gold: агрегаты по дням
├── init-db/
│   ├── 01-create-schemas.sql  # Создание схем
│   └── 02-create-tables.sql   # Создание таблиц
└── docker-compose.yml
```

## Быстрый старт

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

**Доступные сервисы:**
- Airflow UI: http://localhost:8080 (admin / admin)
- Metabase: http://localhost:3000
- PostgreSQL DWH: localhost:5432 (dwh / dwh)

## DAG: weather_etl

Запускается ежедневно, выполняет:

1. **get_data** — получение данных из Open-Meteo API (Москва)
2. **load_to_bronze** — сохранение JSON в `bronze.raw_weather`
3. **run_dbt** — запуск dbt моделей (Silver → Gold)

## dbt модели

### staging/stg_weather (Silver)

Распаковывает JSON массивы в строки:

```sql
-- Вход: JSONB с массивами time[], temperature_2m[]
-- Выход: строки с timestamp и temperature
```

| Колонка | Тип | Описание |
|---------|-----|----------|
| source_id | int | ID записи в bronze |
| measured_at | timestamp | Время измерения |
| temperature | numeric | Температура (°C) |
| loaded_at | timestamp | Время загрузки |

### marts/mart_daily_weather (Gold)

Дневные агрегаты температуры:

| Колонка | Тип | Описание |
|---------|-----|----------|
| date | date | Дата |
| avg_temp | numeric | Средняя температура |
| min_temp | numeric | Минимальная температура |
| max_temp | numeric | Максимальная температура |

## Команды

```bash
# Запуск dbt вручную
docker-compose --profile dbt run --rm dbt run

# Проверка подключения dbt
docker-compose --profile dbt run --rm dbt debug

# Запуск конкретной модели
docker-compose --profile dbt run --rm dbt run --select stg_weather

# Просмотр логов Airflow
docker-compose logs -f airflow-scheduler
```

## Схемы в PostgreSQL

| Схема | Назначение |
|-------|------------|
| bronze | Сырые данные |
| dbt_silver | Очищенные данные (dbt) |
| dbt_gold | Агрегаты (dbt) |
| dbt | Служебная схема dbt |
