# SDA — Sentinel Deforestation Analysis

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-CC2927?logo=databricks&logoColor=white)](https://www.sqlalchemy.org/)
[![Pytest](https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Ruff](https://img.shields.io/badge/Lint-ruff-2C2D72?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

SDA is a Python codebase for deforestation analysis over Sentinel-2 imagery. It provides configuration management, database models, and data-access helpers for scenes, assets, indices, runs, and change detection. The repository is organized for local experimentation with geospatial rasters while keeping database interactions explicit and auditable.

## Repository Layout
- `sda/` core package.
- `sda/auth/` configuration and profile loading.
- `sda/db/` SQLAlchemy engine, sessions, and data-access helpers.
- `sda/models/` ORM models for scenes, assets, indices, runs, and related entities.
- `sda/tests/` unit and integration-style tests.
- `sda/data/` local assets and runtime data/cache.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration
Copy `.env.example` to `.env` and adjust values as needed. Key fields include:
- `SDA_PROFILE` (`user` or `dev`)
- `SDA_DATA_DIR`, `SDA_CACHE_DIR`, `SDA_LOG_LEVEL`
- `PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER`, `PG_PASS`

Environment loading is handled in `sda/auth/config.py`.

## Run Locally
```bash
python -m sda.main
```
This loads configuration, initializes the database engine, and writes logs to `sda/data/data/logs/sda.log`.

## Testing
```bash
python -m sda.tests.test_main
pytest sda/tests
```
Tests use `unittest` under the hood and exercise SQLAlchemy logic against isolated SQLite databases.

## Linting
```bash
ruff check .
```

## Data Assets
Large rasters and derived products live under `sda/data/data/`. A typical scene folder includes JP2 bands, derived GeoTIFFs, and a `manifest.json` with SHA256 hashes for integrity checks. Avoid committing secrets or large binary data to Git.

## License
MIT License. See `LICENSE`.
