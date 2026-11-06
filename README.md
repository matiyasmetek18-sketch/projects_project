# Idea Forge

Offline ranked feed of short product ideas. The catalog is illustrative. There is no model and the app makes no network calls.

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m idea_forge.web
```

Open http://127.0.0.1:5050. The server binds to 127.0.0.1 only.

`python -m idea_forge` starts the same server.

## Environment

| Variable | Default | Meaning |
| --- | --- | --- |
| `IDEA_FORGE_DB` | `instance/idea_forge.sqlite` | SQLite file, relative to the working directory |
| `IDEA_FORGE_PORT` | `5050` | Port |
| `IDEA_FORGE_SECRET_KEY` | new random value each process start | Flask session secret. Set it to keep sessions across restarts. |
| `IDEA_FORGE_GENERATOR` | `1` | Set to `0` to skip the background generator thread |
| `IDEA_FORGE_INTERVAL` | `3` | Seconds between generated ideas |

On startup the server inserts one seed idea when the database is empty, then the generator thread inserts the next catalog combination on each interval. The same catalog and the same stored ideas always produce the same next idea. The thread is a daemon and is not started when the reloader is off and `IDEA_FORGE_GENERATOR=0`. The development server runs with `use_reloader=False`, so the thread starts once.

## Routes

- `GET /` — feed with filters and ranked cards
- `GET /ideas/<id>` — idea detail
- `POST /ideas/<id>/status` — change status, including dismissed
- `GET /ideas/<id>.md` — markdown export (`text/markdown`)
- `GET /settings` — weights
- `POST /settings` — save weights

Every POST requires the session CSRF token. A missing or invalid token returns 400.

## Ranking

```
score = impact * 0.45 + portfolio * 0.25 + feasibility * 0.30
```

Each component is an author judgment from 0 to 100. The score is rounded half up to an integer. It is recomputed on every request from the current weights and the catalog judgments. It is not stored.

Settings can change the three weights. The defaults are 45, 25, and 30. If they do not sum to 100, they are renormalized before the next response. Dismissed ideas are excluded from the ranked feed.

Feasibility starts from the pattern judgment and is shifted by a small catalog adjustment for the twist, then clamped to 0–100. That shift is still an author judgment, not a measurement.

## Time estimate

Week counts are planning estimates, not measured build times. For a pattern:

```
weeks = scope + extra
```

`scope` is a planning size in weeks. Difficulty adds 1 week (Low), 2 weeks (Moderate), or 4 weeks (High). The difficulty label on each card is the catalog label (Low, Moderate, or High).

## Catalog

Every problem is an illustrative example. None of them cite a source. Do not read the summaries as research findings.

Component scores are author judgments for ranking. Considerations (risk, ethics, cost, maintenance) are planning notes, written as guidance, not findings from a study.

## Tests

```bash
.venv/bin/python -m unittest discover -s idea_forge/tests -v
```
