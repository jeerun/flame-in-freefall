"""Translate English BASS-II questions to finite predicates over the original NASA CSV."""

import csv
import json
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "raw" / "psi_tables" / "PSI-25_Experimental table_BASS-II.csv"
GAS_COLUMNS = {
    "o2": ("Calibrated initial O2 % by vol", "Calibrated final O2 % by vol"),
    "co": ("Initial CO (ppm)", "Final CO (ppm)"),
    "co2": ("Initial CO2 % by vol", "Final CO2 % by vol"),
}
EXAMPLES = {
    "Which tests recorded unchanged oxygen and rising CO?": (
        None, [("o2", "same"), ("co", "up")]),
    "Which tests recorded falling oxygen and rising carbon dioxide?": (
        None, [("o2", "down"), ("co2", "up")]),
    "Show all readings for test B1.": ("B1", []),
}

FILTER_SCHEMA = {
    "type": "object",
    "properties": {
        "gas": {"type": "string", "enum": list(GAS_COLUMNS)},
        "change": {"type": "string", "enum": ["up", "down", "same"]},
    },
    "required": ["gas", "change"],
    "additionalProperties": False,
}
PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "supported": {"type": "boolean"},
        "test_id": {"type": ["string", "null"]},
        "filters": {"type": "array", "maxItems": 3, "items": FILTER_SCHEMA},
    },
    "required": ["supported", "test_id", "filters"],
    "additionalProperties": False,
}
SYSTEM = (
    "Interpret an English question about the NASA BASS-II test table. Return only the supplied "
    "JSON schema. Supported: look up a single test ID, or find tests in which a gas reading "
    "increased, decreased, or stayed the same from initial to final. Combine conditions by AND. "
    "O2 is oxygen, CO is carbon monoxide, CO2 is carbon dioxide. Use only explicit conditions "
    "and IDs. Your job is translation, so accept valid questions even though you cannot see "
    "the table or know the answer. A separate program executes the filters. For 'Which runs "
    "had falling oxygen?' return {\"supported\":true,\"test_id\":null,\"filters\":[{\"gas\":"
    "\"o2\",\"change\":\"down\"}]}. For 'CO climbed while oxygen remained flat' use two filters, "
    "co/up and o2/same, and supported true. Without a specific test return test_id null. A named test can be returned with "
    "no filters to inspect all of its readings. Mark supported false for every other request, "
    "including continuous trends, timing, numeric thresholds, rankings, predictions, explanations, different datasets, "
    "OR, comparisons between tests, or questions you cannot translate fully. Never answer the "
    "question or invent measurements."
)

GAS_WORDS = re.compile(r"\b(oxygen|o2|carbon monoxide|co|carbon dioxide|co2)\b")
GAS_NAMES = dict(zip(("oxygen", "o2", "carbon monoxide", "co", "carbon dioxide", "co2"),
                     ("o2", "o2", "co", "co", "co2", "co2")))
ID = r"[a-z]\d+[a-z]?"
TEST_WORDS = re.compile(rf"\b(?:test|run|trial|row|record)\s+#?\s*({ID})\b")
ID_WORDS = re.compile(rf"\b({ID})\b")
UNSUPPORTED = re.compile(
    r"\b(or|not|never|except|either|without|why|cause\w*|predict\w*|mean|average|"
    r"median|sum|total amount|percent\w*|ratio|twice|half|below|above|than|threshold|least|most|"
    r"how much|how far|greater|less|exactly|maximum|minimum|largest|smallest|highest|lowest|"
    r"biggest|steepest|peak|only|material|temperature|pressure|before ignition|between tests|"
    r"throughout|all (?:the )?time|at (?:all|any) times?|from start to finish|what time|"
    r"when (?:did|was|were|does)|initially)\b"
)
DIRECTION = {
    "up": r"up|ris(e|es|ing)|rose|risen|rais(e|ed)|increas(e|ed|es|ing)|higher|grew|gain(s|ed)?|climb(s|ed|ing)?",
    "down": r"down|fall(s|en|ing)?|fell|decreas(e|ed|es|ing)|lower(ed)?|lessened|declin(e|ed|es)|drop(s|ped|ping)?|reduc(e|ed|tion)",
    "same": r"same|unchanged|steady|stable|constant|flat|equal|identical|no change|no difference|did not change|didn't change",
}
DIRECTION_PATTERNS = {name: re.compile(r"\b(?:" + pattern + r")\b")
                      for name, pattern in DIRECTION.items()}
# After consuming gas names, IDs and changes, only ordinary linking/query words
# may remain. An unrecognised material, unit or condition must never silently
# turn a narrower question into a table-wide filter.
QUERY_WORDS = set("""
a all an and any are as at both but by can could data did display do does end ended ending
entries entry even experiment experiments fetch final find first for from give go goes going
got had has have held holding identify in initial initially is it kept last level levels
how list look looking many me measurement measurements number numbers of on or please provide read
reading readings record recorded records remained remaining return round rounds row rows run
runs saw see sensor sensors set show showed showing shows signal signals since start started
starting stayed stays staying table tell test tested tests that the their them there these
this those though time to trial trials up use value values want was went were what
when where whereas which while with within would yet you your concentration concentrations
""".split())


@lru_cache(maxsize=1)
def source_rows():
    """Keep all original cells, including over-range flags and displayed precision."""
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        normalized = {" ".join(k.split()): k for k in reader.fieldnames}
        rows = []
        for raw in reader:
            row = {"id": raw["Test #"].strip(), "line": reader.line_num,
                   "material": raw["Fuel Sample Material"].strip(), "source": list(raw.items())}
            for gas, pair in GAS_COLUMNS.items():
                row[gas] = [raw[normalized[column]] for column in pair]
            rows.append(row)
    return rows


def decimal_pair(cells):
    try:
        pair = tuple(Decimal(cell.strip()) for cell in cells)
    except InvalidOperation:
        return None
    return pair if all(value.is_finite() for value in pair) else None


def execute(test_id, filters):
    rows = source_rows()
    matches = []
    excluded = 0
    for row in rows:
        if test_id and row["id"].upper() != test_id:
            continue
        pairs = [(change, decimal_pair(row[gas])) for gas, change in filters]
        if any(pair is None for _, pair in pairs):
            excluded += 1
            continue
        for change, (initial, final) in pairs:
            observed = "up" if final > initial else "down" if final < initial else "same"
            if observed != change:
                break
        else:
            matches.append(row)
    return {
        "status": "ok", "test_id": test_id, "total": len(rows), "excluded": excluded,
        "filters": [{"gas": gas, "change": change} for gas, change in filters],
        "matched": len(matches), "rows": matches,
    }


def normalize(question):
    return " ".join(unicodedata.normalize("NFKC", question).lower().replace("’", "'").split())


def requested_terms(text):
    # O2 is both a gas and an actual BASS-II test ID. Only an explicit test label
    # makes it an ID. Other IDs can appear alone, as in "readings for B1".
    text = re.sub(r"\b(?:bass[- ]ii|psi-25)\b", " ", text)
    named = set(TEST_WORDS.findall(text))
    text = TEST_WORDS.sub(" ", text)
    named.update(i for i in ID_WORDS.findall(text) if i != "o2")
    if len(named) > 1:
        return None
    text = ID_WORDS.sub(lambda m: m[0] if m[0] == "o2" else " ", text)
    gases = {GAS_NAMES[m[0]] for m in GAS_WORDS.finditer(text)}
    changes = {key for key, pattern in DIRECTION_PATTERNS.items() if pattern.search(text)}
    guard_text = DIRECTION_PATTERNS["same"].sub(" ", text)
    if (UNSUPPORTED.search(guard_text) or "n't" in guard_text
            or re.search(r"\d|[=<>%]", GAS_WORDS.sub(" ", text))):
        return None
    remainder = GAS_WORDS.sub(" ", text)
    for pattern in DIRECTION_PATTERNS.values():
        remainder = pattern.sub(" ", remainder)
    if set(re.findall(r"[^\W\d_]+", remainder)) - QUERY_WORDS:
        return None
    bindings = {}
    for clause in re.split(r"\b(?:and|while|but|with|whereas|yet)\b|[,;]", text):
        channels = {GAS_NAMES[m[0]] for m in GAS_WORDS.finditer(clause)}
        trends = {key for key, pattern in DIRECTION_PATTERNS.items() if pattern.search(clause)}
        if len(channels) == len(trends) == 1:
            channel, trend = channels.pop(), trends.pop()
            if channel in bindings and bindings[channel] != trend:
                return None
            bindings[channel] = trend
    return {"id": next(iter(named)).upper() if named else None, "gases": gases,
            "changes": changes, "bindings": bindings}


def valid_plan(plan, requested):
    if not isinstance(plan, dict) or plan.get("supported") is not True:
        return False
    if set(plan) != {"supported", "test_id", "filters"}:
        return False
    if plan["test_id"] != requested["id"] or not isinstance(plan["filters"], list):
        return False
    filters = plan["filters"]
    if len(filters) > len(GAS_COLUMNS):
        return False
    for item in filters:
        if not isinstance(item, dict) or set(item) != {"gas", "change"}:
            return False
        if not isinstance(item["gas"], str) or not isinstance(item["change"], str):
            return False
        if item["gas"] not in GAS_COLUMNS or item["change"] not in DIRECTION:
            return False
        if item["gas"] in requested["bindings"] and requested["bindings"][item["gas"]] != item["change"]:
            return False
    gases = {f["gas"] for f in filters}
    changes = {f["change"] for f in filters}
    if len(gases) != len(filters) or changes != requested["changes"]:
        return False
    # A direct lookup may name the channels to inspect (CO for B1).
    if (filters and gases != requested["gases"]) or (not filters and not plan["test_id"]):
        return False
    return True


def model_plan(question, translate):
    """Parse/validate a query without accessing any table rows."""
    unsupported = {"supported": False, "test_id": None, "filters": []}
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= 320:
        return unsupported
    text = normalize(question)
    for sample, (test_id, filters) in EXAMPLES.items():
        if text.rstrip("?.!") == normalize(sample).rstrip("?.!"):
            return {"supported": True, "test_id": test_id,
                    "filters": [{"gas": gas, "change": change} for gas, change in filters]}
    requested = requested_terms(text)
    if requested is None or not (requested["id"] or (requested["gases"] and requested["changes"])):
        return unsupported
    if translate is None:
        return None
    plan = translate([{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}],
                     PLAN_SCHEMA)
    if isinstance(plan, dict) and isinstance(plan.get("test_id"), str):
        plan = dict(plan, test_id=plan["test_id"].upper())
    return plan if valid_plan(plan, requested) else unsupported


def answer_question(question, translate=None):
    """translate(messages, schema) returns a decoded local-model JSON object."""
    plan = model_plan(question, translate)
    if plan is None:
        return {"status": "unavailable"}
    if not plan["supported"]:
        return {"status": "unsupported"}
    return execute(plan["test_id"], [(item["gas"], item["change"]) for item in plan["filters"]])


def build_examples():
    return [{"question": question, "result": answer_question(question)} for question in EXAMPLES]


if __name__ == "__main__":
    output = ROOT / "console" / "lab-table-examples.js"
    samples = json.dumps(build_examples(), ensure_ascii=False, separators=(",", ":"))
    output.write_text("// Generated by server/table_questions.py from NASA BASS-II.\n"
                      + "window.LAB_TABLE_EXAMPLES = " + samples + ";\n",
                      encoding="utf-8", newline="\n")
    print(f"Wrote {len(EXAMPLES)} example results from {len(source_rows())} BASS-II rows.")
