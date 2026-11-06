"""Deterministic ideas and ranking. No model and no network."""

import math
import os
import threading

from idea_forge import catalog

DEFAULT_WEIGHTS = (45, 25, 30)


def compose(problem, pattern, twist):
    pitch = pattern["frames"][twist["frame"]].format(detail=problem["detail"])
    return {
        "problem_id": problem["id"],
        "pattern_id": pattern["id"],
        "twist_id": twist["id"],
        "name": problem["noun"] + " " + pattern["name"],
        "pitch": pitch,
    }


def next_spec(used):
    """Next unused combination. Same used-set and catalog produce the same spec."""
    for problem, pattern, twist in catalog.combinations():
        key = (problem["id"], pattern["id"], twist["id"])
        if key not in used:
            return compose(problem, pattern, twist)
    return None


def used_keys(rows):
    keys = set()
    for row in rows:
        keys.add((row["problem_id"], row["pattern_id"], row["twist_id"]))
    return keys


def _clamp(value):
    number = int(value)
    if number < 0:
        return 0
    if number > 100:
        return 100
    return number


def effective_weights(weights):
    """Return the three weights renormalized so they sum to 100.

    Defaults are 45, 25, and 30. Those already sum to 100 and stay exact.
    """
    if weights is None:
        return (45.0, 25.0, 30.0)
    wi = float(weights[0])
    wp = float(weights[1])
    wf = float(weights[2])
    total = wi + wp + wf
    if total <= 0:
        return (45.0, 25.0, 30.0)
    if total == 100:
        return (wi, wp, wf)
    return (wi * 100.0 / total, wp * 100.0 / total, wf * 100.0 / total)


def rank_score(impact, portfolio, feasibility, weights=None):
    """Integer score from judgments and weights.

    Default formula: impact*0.45 + portfolio*0.25 + feasibility*0.30.
    Weights that do not sum to 100 are renormalized first.
    Rounded half up to an integer. Not stored.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    wi = float(weights[0])
    wp = float(weights[1])
    wf = float(weights[2])
    total = wi + wp + wf
    if total <= 0:
        wi, wp, wf = 45.0, 25.0, 30.0
        total = 100.0
    numer = (float(impact) * wi) + (float(portfolio) * wp) + (float(feasibility) * wf)
    raw = numer / total
    return int(math.floor(raw + 0.5))


def format_weight(value):
    number = float(value)
    rounded = round(number, 1)
    if abs(rounded - round(rounded)) < 1e-9:
        return str(int(round(rounded)))
    return "%.1f" % rounded


def assemble(row, weights):
    problem = catalog.get_problem(row["problem_id"])
    pattern = catalog.get_pattern(row["pattern_id"])
    twist = catalog.get_twist(row["twist_id"])
    impact = _clamp(problem["impact"])
    portfolio = _clamp(pattern["portfolio"])
    feasibility = _clamp(pattern["feasibility"] + twist["feasibility_delta"])
    return {
        "id": row["id"],
        "name": row["name"],
        "pitch": row["pitch"],
        "status": row["status"],
        "area": problem["area"],
        "difficulty": pattern["difficulty"],
        "weeks": catalog.estimate_weeks(pattern),
        "score": rank_score(impact, portfolio, feasibility, weights),
        "impact": impact,
        "portfolio": portfolio,
        "feasibility": feasibility,
        "summary": problem["summary"],
        "illustrative": bool(problem["illustrative"]),
        "pattern_label": pattern["label"],
        "twist_label": twist["label"],
        "twist_note": twist["note"],
        "considerations": pattern["considerations"],
        "scope": pattern["scope"],
    }


def to_markdown(idea, weights):
    effective = effective_weights(weights)
    considerations = idea["considerations"]
    lines = [
        "# %s" % idea["name"],
        "",
        idea["pitch"],
        "",
        "Author-framed public-benefit idea. Not a cited fact.",
        "",
        idea["summary"],
        "",
        "Area: %s" % idea["area"],
        "Pattern: %s" % idea["pattern_label"],
        "Twist: %s. %s" % (idea["twist_label"], idea["twist_note"]),
        "",
        "## Ranking",
        "",
        "Score: %s" % idea["score"],
        "",
        "%s%% of %s, plus %s%% of %s, plus %s%% of %s, rounded."
        % (
            format_weight(effective[0]),
            idea["impact"],
            format_weight(effective[1]),
            idea["portfolio"],
            format_weight(effective[2]),
            idea["feasibility"],
        ),
        "",
        "The percentage is how much of the blend that part counts for.",
        "",
        "Impact: %s out of 100, %s%% share" % (idea["impact"], format_weight(effective[0])),
        "Portfolio: %s out of 100, %s%% share" % (idea["portfolio"], format_weight(effective[1])),
        "Feasibility: %s out of 100, %s%% share" % (idea["feasibility"], format_weight(effective[2])),
        "",
        "These are author judgments on a 0–100 scale, not measurements. The score is recomputed from the current weights and is not stored.",
        "",
        "## Time",
        "",
        "Planning estimate: %s weeks" % idea["weeks"],
        "Difficulty: %s" % idea["difficulty"],
        "",
        "The week count is a planning estimate from the pattern scope and difficulty. It is not a measured build time.",
        "",
        "## Considerations",
        "",
        "Planning notes, not findings from a study.",
        "",
        "- Risk: %s" % considerations["risk"],
        "- Ethics: %s" % considerations["ethics"],
        "- Cost: %s" % considerations["cost"],
        "- Maintenance: %s" % considerations["maintenance"],
        "",
        "Status: %s" % idea["status"],
        "",
    ]
    return "\n".join(lines)


def generator_enabled():
    raw = os.environ.get("IDEA_FORGE_GENERATOR", "1").strip()
    return raw != "0"


def generator_interval():
    raw = os.environ.get("IDEA_FORGE_INTERVAL", "3").strip()
    try:
        value = float(raw)
    except ValueError:
        value = 3.0
    if value < 0.1:
        return 0.1
    return value


class IdeaGenerator(object):
    """Daemon thread that inserts the next deterministic idea on an interval."""

    def __init__(self, db_path, interval=None):
        self.db_path = db_path
        if interval is None:
            interval = generator_interval()
        self.interval = float(interval)
        self._stop = threading.Event()
        self.thread = None

    def start(self):
        self.thread = threading.Thread(
            target=self._run,
            name="idea-forge-generator",
            daemon=True,
        )
        self.thread.start()
        return self.thread

    def stop(self):
        self._stop.set()
        if self.thread is not None:
            self.thread.join(timeout=max(2.0, self.interval + 1.0))

    def _run(self):
        while not self._stop.is_set():
            if self._stop.wait(self.interval):
                return
            self.tick()

    def tick(self):
        from idea_forge import storage

        rows = storage.list_ideas(self.db_path)
        spec = next_spec(used_keys(rows))
        if spec is not None:
            storage.insert_idea(self.db_path, spec)


def start_generator(db_path):
    """Start the background thread, or return None when generation is off."""
    if not generator_enabled():
        return None
    worker = IdeaGenerator(db_path)
    worker.start()
    return worker
