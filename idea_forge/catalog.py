"""Illustrative catalog for Idea Forge.

Every problem is an example for planning, not a cited fact. There are no
source URLs. Impact, portfolio, and feasibility numbers are author judgments
used only for ranking. Scope and difficulty are planning inputs for a week
estimate. Considerations are planning notes, not findings from a study.
"""

DIFFICULTY_EXTRA_WEEKS = {
    "Low": 1,
    "Moderate": 2,
    "High": 4,
}

DIFFICULTIES = ["Low", "Moderate", "High"]

PROBLEMS = [
    {
        "id": "slips",
        "area": "Schools",
        "noun": "Slip",
        "detail": "unsigned slips",
        "impact": 44,
        "illustrative": True,
        "summary": "Permission slips that stay in a bag until the day of the trip.",
    },
    {
        "id": "prep",
        "area": "Kitchens",
        "noun": "Prep",
        "detail": "prep gaps",
        "impact": 67,
        "illustrative": True,
        "summary": "A kitchen that finds a prep gap only after service has started.",
    },
    {
        "id": "tools",
        "area": "Workshops",
        "noun": "Tool",
        "detail": "borrowed tools",
        "impact": 36,
        "illustrative": True,
        "summary": "Tools that leave the bench and come back late.",
    },
    {
        "id": "holds",
        "area": "Libraries",
        "noun": "Hold",
        "detail": "unclaimed items",
        "impact": 51,
        "illustrative": True,
        "summary": "A hold shelf filling up with items nobody collects.",
    },
    {
        "id": "turns",
        "area": "Hostels",
        "noun": "Room",
        "detail": "room turns",
        "impact": 63,
        "illustrative": True,
        "summary": "A room marked ready before anyone checks the linen.",
    },
    {
        "id": "water",
        "area": "Farms",
        "noun": "Field",
        "detail": "irrigation checks",
        "impact": 74,
        "illustrative": True,
        "summary": "A field watered again because the last check was only spoken.",
    },
    {
        "id": "chart",
        "area": "Clinics",
        "noun": "Chart",
        "detail": "unfinished notes",
        "impact": 86,
        "illustrative": True,
        "summary": "Clinic notes still open at the end of the day.",
    },
    {
        "id": "edits",
        "area": "Studios",
        "noun": "Edit",
        "detail": "open revisions",
        "impact": 58,
        "illustrative": True,
        "summary": "Revision requests arriving in separate chats.",
    },
    {
        "id": "loans",
        "area": "Galleries",
        "noun": "Loan",
        "detail": "outgoing loans",
        "impact": 71,
        "illustrative": True,
        "summary": "Artwork loans whose return dates live in one person's mail.",
    },
    {
        "id": "shifts",
        "area": "Depots",
        "noun": "Shift",
        "detail": "shift handoffs",
        "impact": 79,
        "illustrative": True,
        "summary": "A depot handoff written on a note stuck to a monitor.",
    },
]

PATTERNS = [
    {
        "id": "queue",
        "name": "queue",
        "label": "Shared queue",
        "scope": 3,
        "difficulty": "Low",
        "portfolio": 66,
        "feasibility": 84,
        "frames": [
            "Keep {detail} in one queue, with the oldest item on top.",
            "A shared queue holds {detail} so they are not left in side notebooks.",
            "The next person picks up {detail} from the top of a single queue.",
        ],
        "considerations": {
            "risk": "A queue with no owner becomes a place where work waits.",
            "ethics": "Do not put private details on a queue other people can browse.",
            "cost": "Start with a board or a sheet the team already uses.",
            "maintenance": "Clear finished items the same day or the queue turns into an archive.",
        },
    },
    {
        "id": "list",
        "name": "list",
        "label": "Checklist",
        "scope": 2,
        "difficulty": "Low",
        "portfolio": 47,
        "feasibility": 91,
        "frames": [
            "Close out {detail} with a checklist short enough to finish in one pass.",
            "One checklist covers {detail}, and finished items are crossed off the same day.",
            "Handle {detail} from a list instead of from memory.",
        ],
        "considerations": {
            "risk": "A long checklist gets skipped. Keep it to the steps that matter.",
            "ethics": "A checklist should not be used to watch how fast someone works.",
            "cost": "Paper or a shared doc is enough for a first version.",
            "maintenance": "Review the list when the work changes, or it will drift.",
        },
    },
    {
        "id": "review",
        "name": "review",
        "label": "Weekly review",
        "scope": 4,
        "difficulty": "Moderate",
        "portfolio": 78,
        "feasibility": 69,
        "frames": [
            "Once a week, read through {detail} and drop anything already done.",
            "A weekly review is the only meeting where {detail} get a yes or a no.",
            "Set one sitting aside each week and clear {detail}.",
        ],
        "considerations": {
            "risk": "A weekly review dies if it has no standing time on the calendar.",
            "ethics": "Do not use the review to rank people against each other.",
            "cost": "The cost is an hour on the calendar, not a new tool.",
            "maintenance": "Keep the same agenda so the meeting stays short.",
        },
    },
    {
        "id": "note",
        "name": "note",
        "label": "Handoff note",
        "scope": 3,
        "difficulty": "Moderate",
        "portfolio": 55,
        "feasibility": 76,
        "frames": [
            "Leave a handoff note for {detail} that the next shift can read in a minute.",
            "One note carries {detail} from this shift to the next.",
            "Write {detail} into the handoff note before leaving, then stop.",
        ],
        "considerations": {
            "risk": "Notes that try to say everything get skipped by the next shift.",
            "ethics": "Write what the next person needs, not gossip about a client.",
            "cost": "One notebook or one shared doc covers the handoff.",
            "maintenance": "Agree on where the note lives or people will write two.",
        },
    },
    {
        "id": "board",
        "name": "board",
        "label": "Exception board",
        "scope": 5,
        "difficulty": "High",
        "portfolio": 83,
        "feasibility": 43,
        "frames": [
            "Put {detail} on a board only when the work is stuck.",
            "An exception board shows {detail} that have waited longer than usual.",
            "Use a board for {detail} that need a decision, and leave routine work off it.",
        ],
        "considerations": {
            "risk": "If everything is an exception, the board is just another inbox.",
            "ethics": "A board in a shared room should not show sensitive names.",
            "cost": "A wall or a single screen is the whole build.",
            "maintenance": "Take items down when they are done so the board stays small.",
        },
    },
]

TWISTS = [
    {
        "id": "paper",
        "name": "Paper",
        "label": "Paper",
        "frame": 0,
        "feasibility_delta": 4,
        "note": "Meant to run on a single paper sheet.",
    },
    {
        "id": "screen",
        "name": "Screen",
        "label": "Screen",
        "frame": 1,
        "feasibility_delta": 0,
        "note": "Meant to run on one shared screen.",
    },
    {
        "id": "rota",
        "name": "Rota",
        "label": "Rota",
        "frame": 2,
        "feasibility_delta": -6,
        "note": "Meant to be tied to a named rota.",
    },
]

_PROBLEMS_BY_ID = dict((item["id"], item) for item in PROBLEMS)
_PATTERNS_BY_ID = dict((item["id"], item) for item in PATTERNS)
_TWISTS_BY_ID = dict((item["id"], item) for item in TWISTS)


def get_problem(problem_id):
    return _PROBLEMS_BY_ID[problem_id]


def get_pattern(pattern_id):
    return _PATTERNS_BY_ID[pattern_id]


def get_twist(twist_id):
    return _TWISTS_BY_ID[twist_id]


def areas():
    found = []
    for problem in PROBLEMS:
        if problem["area"] not in found:
            found.append(problem["area"])
    return found


def combinations():
    """Stable order. Same catalog always yields the same sequence."""
    combos = []
    for problem in PROBLEMS:
        for pattern in PATTERNS:
            for twist in TWISTS:
                combos.append((problem, pattern, twist))
    return combos


def estimate_weeks(pattern):
    """Planning estimate in whole weeks from pattern scope and difficulty.

    scope is a planning size in weeks. Difficulty adds 1 (Low), 2 (Moderate),
    or 4 (High). This is not a measured build time.
    """
    extra = DIFFICULTY_EXTRA_WEEKS[pattern["difficulty"]]
    return int(pattern["scope"]) + extra
