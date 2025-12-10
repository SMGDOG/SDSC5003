# PaperHub Quick Start Guide

## For new users

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the database

```bash
docker-compose up -d
```

### 3. Initialize the database

```bash
python -m app.database
```

### 4. Start the application

```bash
python -m streamlit run app/main.py
```

or use start.bat：

```bash
start.bat
```

## Common Commands

### check DB
```bash
docker-compose ps
```

### stop DB
```bash
docker-compose down
```

### check log
```bash
docker-compose logs -f postgres
```

### restart DB
```bash
docker-compose restart
```

### delete DB
```bash
docker-compose down -v
docker-compose up -d
python -m app.database
```
