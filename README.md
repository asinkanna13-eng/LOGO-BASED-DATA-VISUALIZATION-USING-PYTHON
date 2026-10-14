# Math Identity Engine

A local Flask application for generating mathematical identity images for Company, College, School, Vehicle, and Phone. The existing Pillow renderers remain in `modules/`; Flask passes each renderer its identity fields and category-specific output directory.

## Run on Windows

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000/, create an account, and sign in. Set `FLASK_SECRET_KEY` to a stable random value outside local development; the generated local key is intended only for development. SQLite accounts are stored in `database/users.db`.

## Data and outputs

The app creates `data/<category>/` and `generated/<category>/` when it starts. The `data/` folders remain unused by the website. Category forms accept only the identity fields used by their corresponding Python programs. College, School, Vehicle, and Phone use their existing internal data selection, and Company retrieves market history for its ticker. Generated images are saved with unique names in the matching `generated/` folder.

Company generation requests market history for the ticker through Yahoo Finance. Network/API failures are logged and shown as a readable page message. Generated images and category pages require an authenticated session.

The existing renderers refer to Windows font files. On Railway/Linux those files may be unavailable, so the modules use their built-in Pillow font fallback; calculations, geometry, colors, and output flow remain, but the selected typeface can differ unless compatible licensed fonts are installed.

## Deploy on Railway

Push the project to GitHub, create a Railway project from that repository, and deploy with the included `Procfile` (`gunicorn --bind 0.0.0.0:$PORT app:app`). Configure `FLASK_SECRET_KEY` as a Railway variable with a long random value.

Railway's application filesystem is not durable across redeployments. To retain SQLite accounts and generated images, attach a Railway volume mounted at `/data` and set `MATH_IDENTITY_STORAGE_DIR=/data`. Without a mounted volume, generated output and local SQLite data can be lost when the service is redeployed or its instance is replaced.

## Requirements

The requirements file covers Flask/Werkzeug, Gunicorn, the existing Pillow and QR renderers, pandas/numpy utilities, and Yahoo Finance market history.