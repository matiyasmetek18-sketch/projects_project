"""Flask app. Bind 127.0.0.1. Score is recomputed on each request."""

import os
import secrets

from flask import Flask, Response, abort, redirect, render_template, request, session, url_for

from idea_forge import catalog, generator, storage, viz


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    db_path = storage.resolve_db_path()
    app.config["DB_PATH"] = db_path
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    secret = os.environ.get("IDEA_FORGE_SECRET_KEY")
    if secret:
        app.secret_key = secret
    else:
        app.secret_key = secrets.token_hex(32)
    storage.init_db(db_path)

    def ensure_csrf():
        token = session.get("csrf_token")
        if not token:
            token = secrets.token_hex(32)
            session["csrf_token"] = token
        return token

    def csrf_matches():
        sent = request.form.get("csrf_token", "")
        saved = session.get("csrf_token", "")
        if not sent or not saved or len(sent) != len(saved):
            return False
        return secrets.compare_digest(sent, saved)

    def present_row(row, weights):
        return generator.assemble(row, weights)

    def load_idea(idea_id, weights):
        row = storage.get_idea(db_path, idea_id)
        if row is None:
            return None
        return present_row(row, weights)

    def select_ideas(ideas, area, difficulty, status, query):
        chosen = []
        needle = query.lower()
        for idea in ideas:
            if area and idea["area"] != area:
                continue
            if difficulty and idea["difficulty"] != difficulty:
                continue
            if status:
                if idea["status"] != status:
                    continue
            elif idea["status"] == "dismissed":
                continue
            if needle:
                haystack = (idea["name"] + " " + idea["pitch"]).lower()
                if needle not in haystack:
                    continue
            chosen.append(idea)
        chosen.sort(key=lambda idea: (-idea["score"], idea["name"], idea["id"]))
        return chosen

    def top_areas(rows):
        counts = {}
        for row in rows:
            area = catalog.get_problem(row["problem_id"])["area"]
            counts[area] = counts.get(area, 0) + 1
        pairs = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        listed = []
        for name, count in pairs[:4]:
            listed.append({"name": name, "count": count})
        return listed

    @app.context_processor
    def inject_csrf():
        return {
            "csrf_token": ensure_csrf(),
            "score_ring": viz.score_ring_svg,
        }

    @app.before_request
    def reject_bad_csrf():
        if request.method != "POST":
            return None
        if csrf_matches():
            return None
        return Response("Missing or invalid CSRF token.\n", status=400, mimetype="text/plain")

    @app.route("/")
    def feed():
        weights = storage.get_weights(db_path)
        rows = storage.list_ideas(db_path)
        ideas = []
        for row in rows:
            ideas.append(present_row(row, weights))
        area = request.args.get("area", "")
        difficulty = request.args.get("difficulty", "")
        status = request.args.get("status", "")
        query = request.args.get("q", "").strip()
        ranked = select_ideas(ideas, area, difficulty, status, query)
        groups = [{"label": "", "items": ranked}]
        return render_template(
            "feed.html",
            groups=groups,
            has_ideas=bool(ranked),
            top_areas=top_areas(rows),
            areas=catalog.areas(),
            difficulties=catalog.DIFFICULTIES,
            statuses=storage.STATUS_LABELS,
            area=area,
            difficulty=difficulty,
            status=status,
            q=query,
            show_dismissed_note=(status == "dismissed"),
        )

    @app.route("/ideas/<int:idea_id>")
    def idea_detail(idea_id):
        weights = storage.get_weights(db_path)
        idea = load_idea(idea_id, weights)
        if idea is None:
            return render_template("idea.html", missing=True), 404
        effective = generator.effective_weights(weights)
        return render_template(
            "idea.html",
            missing=False,
            idea=idea,
            statuses=storage.STATUS_LABELS,
            weight_impact=generator.format_weight(effective[0]),
            weight_portfolio=generator.format_weight(effective[1]),
            weight_feasibility=generator.format_weight(effective[2]),
        )

    @app.route("/ideas/<int:idea_id>/status", methods=["POST"])
    def idea_status(idea_id):
        status = request.form.get("status", "")
        if status not in storage.STATUSES:
            return Response("Unknown status.\n", status=400, mimetype="text/plain")
        if storage.get_idea(db_path, idea_id) is None:
            abort(404)
        storage.set_status(db_path, idea_id, status)
        return redirect(url_for("idea_detail", idea_id=idea_id))

    @app.route("/ideas/<int:idea_id>.md")
    def idea_markdown(idea_id):
        weights = storage.get_weights(db_path)
        idea = load_idea(idea_id, weights)
        if idea is None:
            abort(404)
        body = generator.to_markdown(idea, weights)
        return Response(body, mimetype="text/markdown")

    @app.route("/settings", methods=["GET", "POST"])
    def settings():
        error = None
        if request.method == "POST":
            parsed = []
            for key in ("weight_impact", "weight_portfolio", "weight_feasibility"):
                value = _parse_weight(request.form.get(key, ""))
                if value is None:
                    error = "Enter a weight from 0 to 100 for each judgment."
                    break
                parsed.append(value)
            if error is None:
                storage.set_weights(db_path, parsed[0], parsed[1], parsed[2])
                return redirect(url_for("settings"))
        stored = storage.get_weights(db_path)
        if error is not None:
            entered = (
                request.form.get("weight_impact", ""),
                request.form.get("weight_portfolio", ""),
                request.form.get("weight_feasibility", ""),
            )
        else:
            entered = stored
        effective = generator.effective_weights(stored)
        return render_template(
            "settings.html",
            error=error,
            weight_impact=_display_entered(entered[0]),
            weight_portfolio=_display_entered(entered[1]),
            weight_feasibility=_display_entered(entered[2]),
            effective_impact=generator.format_weight(effective[0]),
            effective_portfolio=generator.format_weight(effective[1]),
            effective_feasibility=generator.format_weight(effective[2]),
        )

    return app


def _parse_weight(raw):
    try:
        number = float(raw)
    except (TypeError, ValueError):
        return None
    if number < 0 or number > 100:
        return None
    return number


def _display_entered(value):
    try:
        return generator.format_weight(value)
    except (TypeError, ValueError):
        return value


def startup_seed(db_path):
    if storage.count_ideas(db_path) > 0:
        return False
    spec = generator.next_spec(set())
    if spec is None:
        return False
    storage.insert_idea(db_path, spec)
    return True


def main():
    db_path = storage.resolve_db_path()
    storage.init_db(db_path)
    startup_seed(db_path)
    app = create_app()
    worker = generator.start_generator(db_path)
    if worker is None:
        print("idea-forge-generator: off", flush=True)
    else:
        print("idea-forge-generator: on", flush=True)
    port = int(os.environ.get("IDEA_FORGE_PORT", "5050"))
    try:
        app.run(host="127.0.0.1", port=port, use_reloader=False, threaded=True)
    finally:
        if worker is not None:
            worker.stop()


if __name__ == "__main__":
    main()
