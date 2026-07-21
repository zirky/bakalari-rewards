# Bakaláři Rewards

Self-hosted webová aplikace: automatická synchronizace známek z Bakalářů + Lightning Address payouty v sats.

## Stack

- **Backend**: FastAPI + SQLAlchemy + Alembic + APScheduler
- **Frontend**: Vue 3 + Vite + Pinia
- **Databáze**: PostgreSQL 16
- **Platby**: LNBits → Lightning Address (LNURL-pay)

## Rychlý start (lokální vývoj)

```bash
cp .env.example .env
# Vyplň .env (Bakaláři, LNBits, SECRET_KEY)

docker compose up --build
```

| Služba | URL |
|---|---|
| Frontend (dev) | http://localhost:5174 |
| Frontend (prod) | http://localhost:3000 |
| Backend API | http://localhost:8001 |
| API docs | http://localhost:8001/docs |
| pgAdmin | http://localhost:5050 |

## Produkční spuštění

```bash
docker compose -f docker-compose.yml up --build -d
```

## Migrace databáze

```bash
docker compose exec backend alembic upgrade head
```

## Mock / test režim

Nastavit `MOCK_MODE=true` v `.env` — použije `MockPaymentProvider` a načte známky z `backend/app/tests/fixtures/sample_marks.json` bez skutečného Bakaláři volání.

## Struktura projektu

```
bakalari-rewards/
├── backend/          # FastAPI aplikace
│   └── app/
│       ├── models/   # SQLAlchemy ORM
│       ├── schemas/  # Pydantic
│       ├── api/      # REST endpointy
│       ├── services/ # bakalari_client, reward_engine, payment_provider...
│       └── scheduler/# APScheduler týdenní sync
├── frontend/         # Vue 3 + Vite
│   └── src/
│       ├── views/parent/  # Rodičovský panel
│       └── views/child/   # Dětský read-only panel
└── docker-compose.yml
```

## Porty (lokální vývoj)

- Backend host port: **8001** (uvnitř kontejneru 8000)
- Frontend dev port: **5174** (uvnitř kontejneru 5173)
- Frontend prod port: **3000**
- pgAdmin: **5050**

> Porty 8000 a 5173 jsou záměrně přeskočeny — mohou být obsazeny jinými aplikacemi.
