# Inventory

A stock management system built with Django.

# Installation
Create an environment file that contains the following variables:

`.env.dev`
```
DEBUG=1
SECRET_KEY=<YOUR_SECRET_KEY>
DJANGO_ALLOWED_HOSTS=*
SQL_USER=<YOUR_USERNAME>
SQL_PASSWORD=<YOUR_PASSWORD>
SQL_HOST=db
SQL_PORT=5432
```

Then, create a `docker-compose.yml` such as the one below, filling in your details as required.

```yaml
version: '3.8'

services:
  web:
    image: fredsheppard/inventory
    ports:
      - "8000:8000"
    env_file:
      - ./.env.dev
    depends_on:
      - db
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=<YOUR_USERNAME>
      - POSTGRES_PASSWORD=<YOUR_PASSWORD>

volumes:
  postgres_data:
```

To start the server, simply run:
```bash
docker-compose up -d
```
