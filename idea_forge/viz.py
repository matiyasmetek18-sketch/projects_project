"""One score ring as inline SVG. Color comes from forge.css, not from here."""


def score_ring_svg(score):
    try:
        number = int(score)
    except (TypeError, ValueError):
        number = 0
    if number < 0:
        number = 0
    if number > 100:
        number = 100
    gap = 100 - number
    return (
        '<svg class="score-ring" viewBox="0 0 72 72" width="72" height="72" role="img" aria-label="Score %d">'
        '<circle class="score-ring__track" cx="36" cy="36" r="28" pathLength="100"></circle>'
        '<circle class="score-ring__value" cx="36" cy="36" r="28" pathLength="100" '
        'stroke-dasharray="%d %d" transform="rotate(-90 36 36)"></circle>'
        '<text class="score-ring__num" x="36" y="36" text-anchor="middle" dominant-baseline="central">%d</text>'
        "</svg>"
    ) % (number, number, gap, number)
