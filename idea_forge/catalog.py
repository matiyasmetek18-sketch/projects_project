"""Author-framed public-benefit catalog for Idea Forge.

Every problem is an idea for the public good, written by the author for
planning. There are no source URLs and no cited statistics. Impact,
portfolio, and feasibility numbers are author judgments used only for
ranking. Scope and difficulty are planning inputs for a week estimate.
Considerations are planning notes, not findings from a study.
"""

DIFFICULTY_EXTRA_WEEKS = {
    "Low": 1,
    "Moderate": 2,
    "High": 4,
}

DIFFICULTIES = ["Low", "Moderate", "High"]

PROBLEMS = [
    {
        "id": "wells",
        "area": "Water",
        "noun": "Well",
        "detail": "shared wells",
        "impact": 84,
        "illustrative": True,
        "summary": "People use a shared well and have no simple public way to see if it is open and fit to drink.",
    },
    {
        "id": "clinics",
        "area": "Health",
        "noun": "Clinic",
        "detail": "nearby clinics",
        "impact": 86,
        "illustrative": True,
        "summary": "A person needs care and cannot tell which nearby clinic will see them.",
    },
    {
        "id": "lessons",
        "area": "Learning",
        "noun": "Lesson",
        "detail": "starter lessons",
        "impact": 62,
        "illustrative": True,
        "summary": "A learner looking for a first lesson finds many options and no plain way to choose where to start.",
    },
    {
        "id": "crossings",
        "area": "Safety",
        "noun": "Crossing",
        "detail": "unsafe crossings",
        "impact": 76,
        "illustrative": True,
        "summary": "People walk a crossing that feels unsafe, and there is no shared public note of it.",
    },
    {
        "id": "ballots",
        "area": "Civic",
        "noun": "Ballot",
        "detail": "ballot questions",
        "impact": 73,
        "illustrative": True,
        "summary": "A voter faces a ballot question written in language that is hard to read before the vote.",
    },
    {
        "id": "shelters",
        "area": "Safety",
        "noun": "Shelter",
        "detail": "storm shelters",
        "impact": 90,
        "illustrative": True,
        "summary": "People need a storm shelter and may only learn where it is after a warning.",
    },
    {
        "id": "taps",
        "area": "Water",
        "noun": "Tap",
        "detail": "public taps",
        "impact": 68,
        "illustrative": True,
        "summary": "A public tap stops running, and the news travels only by word of mouth.",
    },
    {
        "id": "records",
        "area": "Civic",
        "noun": "Record",
        "detail": "public records",
        "impact": 58,
        "illustrative": True,
        "summary": "A public record exists, but a person has to already know which office holds it.",
    },
    {
        "id": "shade",
        "area": "Health",
        "noun": "Shade",
        "detail": "cooling sites",
        "impact": 80,
        "illustrative": True,
        "summary": "On a very hot day, a cooling site is open and easy to miss.",
    },
    {
        "id": "waste",
        "area": "Environment",
        "noun": "Waste",
        "detail": "hazardous drop-offs",
        "impact": 66,
        "illustrative": True,
        "summary": "Household hazardous waste needs a public drop-off people can actually find.",
    },
]

PATTERNS = [
    {
        "id": "guide",
        "name": "guide",
        "label": "Plain guide",
        "scope": 2,
        "difficulty": "Low",
        "portfolio": 47,
        "feasibility": 91,
        "frames": [
            "A one-page public guide explains {detail} in plain language.",
            "One shared screen holds a short public guide to {detail}.",
            "A named crew keeps a plain-language public guide to {detail}.",
        ],
        "considerations": {
            "risk": "A guide that is wrong sends people to the wrong place. Date it and name who updates it.",
            "ethics": "Write for the person who needs the help, in language they can use. Do not collect their story to publish it.",
            "cost": "A printed sheet or a single public page is enough to start.",
            "maintenance": "Recheck the details on a set day, or the guide will drift.",
        },
    },
    {
        "id": "map",
        "name": "map",
        "label": "Public map",
        "scope": 3,
        "difficulty": "Low",
        "portfolio": 66,
        "feasibility": 84,
        "frames": [
            "A posted map shows {detail} so people can find them without asking around.",
            "One public screen maps {detail} for anyone passing by.",
            "A named crew updates a public map of {detail} on a set day.",
        ],
        "considerations": {
            "risk": "A map with a stale mark sends people to a closed door.",
            "ethics": "Mark only places meant for the public. Do not pin a private home.",
            "cost": "Start with a paper map or one shared screen.",
            "maintenance": "Remove a mark the same week it stops being true.",
        },
    },
    {
        "id": "alert",
        "name": "alert",
        "label": "Public alert",
        "scope": 3,
        "difficulty": "Moderate",
        "portfolio": 55,
        "feasibility": 76,
        "frames": [
            "A posted notice is the public alert for {detail}, put where people already gather.",
            "One shared screen is the public alert for {detail}, readable at a glance.",
            "A named crew raises the alert for {detail} and takes it down when it ends.",
        ],
        "considerations": {
            "risk": "An alert left up after the need has passed trains people to ignore the next one.",
            "ethics": "Say what to do and where. Do not name private individuals.",
            "cost": "Paper where people already gather, or one shared screen.",
            "maintenance": "Take the alert down when it ends, and name who has that job.",
        },
    },
    {
        "id": "desk",
        "name": "desk",
        "label": "Help desk",
        "scope": 4,
        "difficulty": "Moderate",
        "portfolio": 78,
        "feasibility": 69,
        "frames": [
            "A posted sheet says where to ask about {detail} and what to bring.",
            "A public help desk on one screen answers common questions about {detail}.",
            "A named crew staffs a help desk for {detail} at posted hours.",
        ],
        "considerations": {
            "risk": "A help desk with no posted hours promises help that nobody is there to give.",
            "ethics": "Answer the question in front of you. Do not keep a file on the person who asked.",
            "cost": "A table, a printed sheet, and a set hour.",
            "maintenance": "Keep the same hours so people know when someone is there.",
        },
    },
    {
        "id": "hub",
        "name": "hub",
        "label": "Care hub",
        "scope": 5,
        "difficulty": "High",
        "portfolio": 83,
        "feasibility": 43,
        "frames": [
            "A posted hub lists only the stuck cases among {detail}.",
            "A public screen shows which {detail} are stuck and who can help.",
            "A named crew runs a small hub for {detail} that need a decision.",
        ],
        "considerations": {
            "risk": "If every case is listed, the urgent ones disappear into the pile.",
            "ethics": "A public hub should not show sensitive personal details.",
            "cost": "A wall, a table, or a single screen.",
            "maintenance": "Clear finished cases so the hub stays small enough to read.",
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
        "note": "Meant to be posted on paper where people already are.",
    },
    {
        "id": "screen",
        "name": "Screen",
        "label": "Screen",
        "frame": 1,
        "feasibility_delta": 0,
        "note": "Meant to run on one shared public screen.",
    },
    {
        "id": "rota",
        "name": "Crew",
        "label": "Crew",
        "frame": 2,
        "feasibility_delta": -6,
        "note": "Meant to be kept up by a named crew.",
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
