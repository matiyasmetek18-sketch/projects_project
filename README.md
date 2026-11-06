# Idea Forge

Offline ranked feed of short public-benefit ideas. The catalog is author-framed. There is no model and the app makes no network calls.

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

In plain language the default score is 45% of the impact number, plus 25% of the portfolio number, plus 30% of the feasibility number, rounded to a whole number. The percentage is how much of the blend that part counts for.

Each part is an author judgment from 0 to 100, not a measurement. The score is rounded half up to an integer. It is recomputed on every request from the current weights and is not stored.

Settings can change the three shares. The defaults are 45, 25, and 30. If they do not sum to 100, they are scaled so they do before the next response. Dismissed ideas stay off the ranked feed.

Feasibility starts from the pattern's number and is shifted by a small catalog adjustment for the twist, then clamped to 0–100. That shift is still an author judgment, not a measurement.

## Time estimate

Week counts are planning estimates, not measured build times. For a pattern:

```
weeks = scope + extra
```

`scope` is a planning size in weeks. Difficulty adds 1 week (Low), 2 weeks (Moderate), or 4 weeks (High). The difficulty label on each card is the catalog label (Low, Moderate, or High).

## Catalog

Every problem is an author-framed public-benefit idea (health, water, learning, safety, civic access, environment, and similar). None of them cite a source, and none of them state a measured impact. Do not read the summaries as research findings.

Component scores are author judgments for ranking. Week counts are planning estimates. Considerations (risk, ethics, cost, maintenance) are planning notes, written as guidance, not findings from a study.

## Tests

```bash
.venv/bin/python -m unittest discover -s idea_forge/tests -v
```
