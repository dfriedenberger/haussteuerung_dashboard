# Haussteuerung Dashboard

Ein schlankes, containerisiertes Python-Web-Dashboard zur Steuerung und Visualisierung von Haus-Infrastrukturgeräten.

## Features
- Geräte- und Gruppenübersicht
- Steuerung und Werteanzeige
- Protokoll und Historie
- Plugin-Schnittstellen für Erweiterungen
- PostgreSQL Datenbank
- Liquibase für Migrationen
- Bootstrap-basiertes, responsives UI


## Installation

```sh
docker-compose pull 
docker-compose build 
```

### Create Database 
```sh
docker-compose up db liquibase
```

```sh
# lpm add postgresql --global # falls das Plugin fehlt
liquibase update

```

## Analyse

### Datenbank
```sh
docker exec -it <container> bash
psql -U postgres -d haussteuerung
```

## Starten
```bash
docker-compose up --build
```


## Development

```bash
docker compose up -d db
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/haussteuerung
cd app;uvicorn main:app --reload
```


## Lizenz
MIT

