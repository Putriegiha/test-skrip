# Deployment notes

## Local Docker Compose

Build and run the app and Redis locally with Docker Compose:

```bash
docker-compose build
docker-compose up -d
# open http://localhost:8000
```

## Procfile / PaaS

For Heroku / Render, the included `Procfile` runs Gunicorn using `wsgi:app`:

```text
web: gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
```

## Systemd (example)

An example unit file is provided at `deploy/sidita.service`. Copy it to `/etc/systemd/system/` and adjust `WorkingDirectory` and `ExecStart` paths to match your installation, then enable:

```bash
sudo cp deploy/sidita.service /etc/systemd/system/sidita.service
sudo systemctl daemon-reload
sudo systemctl enable --now sidita.service
```

## Notes

- Ensure the FastText model and any preprocessed `VEKTOR_ITEM` data are present on the host or mounted into the container.
- Update `REDIS_URL` and database DSN via environment variables in production.
- Run `scripts/preprocess_vectors.py` locally to (re)compute `VEKTOR_ITEM` if needed.
