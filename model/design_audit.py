"""Looking for holes in the console's model design, with the data.

Run from the repo root, after model/train_per_fuel.py:  python model/design_audit.py   (about a minute)
Needs: pandas, numpy, scikit-learn. Reads the cleaned table and console/model.js, writes only
model/per_fuel/design_audit.json. Seeded: a re-run gives the same file.

docs/model-design-audit.md says what each number means, which hole it shows, and what was done about it.

Two parts:
  data_facts()    counts straight from NASA's table, no model involved
  fitted_facts()  what refitting, holding out and resampling say about the models the console uses
"""
import importlib.util
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "model" / "per_fuel" / "design_audit.json"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


per_fuel = load("per_fuel_training", ROOT / "model" / "train_per_fuel.py")
train = per_fuel.train
NUM, KEYS, FUELS, SEED, REPEATS = train.NUM, train.KEYS, train.FUELS, train.SEED, train.REPEATS
COL = {KEYS[c]: c for c in NUM}                     # "o2" -> "o2_pct", and so on

# Settings the documents quote. Each: fuel, then the five settings in the order of NUM.
POINTS = {
    "heptane at the starting values": ("heptane", {"o2": 21, "p": 1.0, "co2": 0, "he": 0, "d0": 3.0}),
    "methanol at the starting values": ("methanol", {"o2": 21, "p": 1.0, "co2": 0, "he": 0, "d0": 3.0}),
    "heptane in Moon Base air": ("heptane", {"o2": 30, "p": 0.694, "co2": 0, "he": 0, "d0": 3.0}),
    "methanol in Moon Base air": ("methanol", {"o2": 30, "p": 0.694, "co2": 0, "he": 0, "d0": 3.0}),
    "heptane at 24 % oxygen": ("heptane", {"o2": 24, "p": 1.0, "co2": 0, "he": 0, "d0": 3.0}),
    "heptane at 16 % oxygen": ("heptane", {"o2": 16, "p": 1.0, "co2": 0, "he": 0, "d0": 3.0}),
}


def tally(frame):
    """How the tests in frame ended, as plain counts."""
    counts = frame["test_end"].value_counts()
    return {end: int(counts.get(end, 0)) for end in ("Completion", "Extinction", "Disruption")}


def data_facts(df=None):
    """Counts straight from the cleaned NASA table. No model, no randomness."""
    df = pd.read_csv(per_fuel.CLEAN) if df is None else df
    scope = per_fuel.scope_of(df)
    clear = scope[scope["test_end"].isin(["Extinction", "Completion"])]
    facts = {"tests_in_source": int(len(df)), "tests_in_scope": int(len(scope)), "endings_in_scope": tally(scope)}

    # 1. The tests the outcome model leaves out are not scattered at random.
    bands = [("up to 15 %", 0, 15), ("above 15 to 18 %", 15, 18), ("above 18 to 21.5 %", 18, 21.5),
             ("above 21.5 to below 25 %", 21.5, 24.999), ("25 % or more", 24.999, 100)]
    facts["endings_by_oxygen"] = {
        fuel: {name: tally(g[(g["o2_pct"] > lo) & (g["o2_pct"] <= hi)]) for name, lo, hi in bands}
        for fuel, g in scope.groupby("fuel")}
    moon = scope[(scope["fuel"] == "heptane") & scope["o2_pct"].between(29, 31) & (scope["pressure_atm"] < 0.75)]
    facts["heptane_at_29_to_31_pct_oxygen_near_0_7_atm"] = tally(moon)

    # 2. "The visible flame went out" says little about how much had burned by then.
    out = clear[(clear["test_end"] == "Extinction") & clear["ext_diameter_mm"].notna() & (clear["ext_diameter_mm"] <= clear["d0_mm"])]
    gone = 1 - (out["ext_diameter_mm"] / out["d0_mm"]) ** 3      # share of the droplet's volume gone when the flame went out
    facts["droplet_volume_gone_when_the_flame_went_out"] = {
        "what": "1 - (end diameter / start diameter) cubed, for tests that ended in Extinction and have both diameters",
        "tests_without_a_usable_end_diameter": int((clear["test_end"] == "Extinction").sum() - len(out)),
        **{fuel: {"tests": int(len(g)), "median": round(float(g.median()), 2),
                  "middle_half": [round(float(v), 2) for v in g.quantile([0.25, 0.75])],
                  "tests_with_90_pct_or_more_gone": int((g >= 0.9).sum()), "tests_with_less_than_half_gone": int((g < 0.5).sum())}
           for fuel, g in gone.groupby(out["fuel"])}}

    # 3. Few completions for the number of parameters.
    n_params = 1 + len(NUM)                              # a fuel's own offset and its own slope for every setting
    facts["completions_per_parameter"] = {
        fuel: {"clear_outcomes": int(len(g)), "completions": int((g["test_end"] == "Completion").sum()), "own_parameters": n_params,
               "completions_per_parameter": round(float((g["test_end"] == "Completion").sum() / n_params), 1)}
        for fuel, g in clear.groupby("fuel")}
    done = clear[(clear["fuel"] == "methanol") & (clear["test_end"] == "Completion")]
    facts["methanol_completions"] = [
        {"test": int(r.test), **{KEYS[c]: round(float(getattr(r, c)), 3) for c in NUM}} for r in done.itertuples()]

    # 4. Pressure sits at two levels, and the lower one almost always comes with a diluent.
    level = np.where(clear["pressure_atm"] < 0.85, "about 0.7 atm", "about 1.0 atm")
    mix = np.where(clear["co2_pct"] > 0, "with carbon dioxide", np.where(clear["he_pct"] > 0, "with helium", "oxygen and nitrogen only"))
    facts["clear_outcomes_by_pressure_and_gas_mix"] = {
        fuel: {lv: {m: int(((clear["fuel"] == fuel) & (level == lv) & (mix == m)).sum())
                    for m in ("oxygen and nitrogen only", "with carbon dioxide", "with helium")}
               for lv in ("about 0.7 atm", "about 1.0 atm")}
        for fuel, _ in FUELS}
    above = df[(df["pressure_atm"] > train.MAX_PRESSURE_ATM) & df["d0_mm"].notna()]
    facts["tests_above_the_pressure_limit"] = {"limit_atm": train.MAX_PRESSURE_ATM, "tests": int(len(above)),
                                               "pressures_atm": sorted({round(float(v), 2) for v in above["pressure_atm"]}),
                                               **{fuel: tally(g) for fuel, g in above.groupby("fuel")}}

    # 5. Most tests have a twin: same fuel, gas mix and pressure level.
    key = clear[["fuel", "o2_pct", "co2_pct", "he_pct"]].astype(str).agg("|".join, axis=1) + "|" + clear["pressure_atm"].round(1).astype(str)
    sizes = key.map(key.value_counts())
    mixed = clear.assign(key=key).groupby("key")["test_end"].nunique()
    facts["twins"] = {"clear_outcomes": int(len(clear)), "tests_with_a_twin": int((sizes > 1).sum()), "groups": int(key.nunique()),
                      "groups_with_both_outcomes": int((mixed > 1).sum())}

    # 6. The rule behind "time to consume the droplet", with NASA's own measured rate: start diameter squared over
    #    the burning rate, against the recorded burn time, for the tests that burned to completion.
    timed = scope[(scope["test_end"] == "Completion") & scope["burn_time_s"].notna() & (scope["burn_rate_mm2_s"] > 0)]
    ratio = (timed["d0_mm"] ** 2 / timed["burn_rate_mm2_s"]) / timed["burn_time_s"]
    facts["d_squared_rule_with_nasa_rate_against_burn_time"] = {
        "completions": int(len(timed)), "median_ratio": round(float(ratio.median()), 2),
        "middle_half": [round(float(v), 2) for v in ratio.quantile([0.25, 0.75])]}

    # 7. The page's "tested range" pools both fuels.
    facts["tested_range_by_fuel"] = {
        key: {"both": [round(float(scope[col].min()), 3), round(float(scope[col].max()), 3)],
              **{fuel: [round(float(g[col].min()), 3), round(float(g[col].max()), 3)] for fuel, g in scope.groupby("fuel")}}
        for key, col in COL.items()}
    return facts


def read_export():
    text = per_fuel.OUT_JS.read_text(encoding="utf-8")
    return json.loads(text[text.index("{"):text.rindex("}") + 1])


def score(part, fuel, values):
    """The export's formula, by hand."""
    return part["intercept"] + part["fuel"][fuel] + sum((part["coef"][k] + part["fuel_coef"][fuel][k]) * v for k, v in values.items())


def reading(model, fuel, values):
    """What the page shows for these settings, worked out from the export alone."""
    keep = 1 - 1 / (1 + np.exp(-score(model["extinction"], fuel, values)))
    dis = 1 / (1 + np.exp(-score(model["disruption"], fuel, values)))
    n, fi = len(model["features"]), [f["key"] for f in model["fuels"]].index(fuel)
    own = 1 + n + (fi - 1) * (n + 1)
    x = [values[f["key"]] for f in model["features"]]
    keeps = []
    for d in model["extinction_draws"]:
        z = d[0] + (d[own] if fi else 0) + sum((d[1 + j] + (d[own + 1 + j] if fi else 0)) * x[j] for j in range(n))
        keeps.append(1 - 1 / (1 + np.exp(-z)))
    lo, hi = np.percentile(keeps, model["meta"]["range"]["percentiles"])
    pct = lambda v: round(float(100 * v), 1)
    return {"burns_all_its_fuel_among_clear_outcomes_pct": pct(keep), "range_pct": [pct(lo), pct(hi)], "disruption_pct": pct(dis),
            "all_three_pct": {"disruption": pct(dis), "burns_all_its_fuel": pct((1 - dis) * keep), "goes_out": pct((1 - dis) * (1 - keep))}}


def fitted_facts(df=None):
    """What refitting, holding out and resampling say. Seeded."""
    warnings.filterwarnings("ignore")
    df = pd.read_csv(per_fuel.CLEAN) if df is None else df
    scope = per_fuel.scope_of(df)
    clear = scope[scope["test_end"].isin(["Extinction", "Completion"])]
    X, y = per_fuel.design(clear), (clear["test_end"] == "Extinction").to_numpy(int)
    fuel = clear["fuel"].to_numpy()
    facts = {}

    # The readings the documents quote, from the export.
    model = read_export()
    facts["readings"] = {name: reading(model, f, v) for name, (f, v) in POINTS.items()}

    # Could one table of variances stand in for the refits? Compare the two ranges, from all the refits.
    c_fit = float(read_metrics()["extinction"]["penalty_c_chosen"])
    refits = per_fuel.slope_stability(clear, c_fit)[1]
    b0, coef0 = train.raw_coefficients(make_pipeline(StandardScaler(), LogisticRegression(C=c_fit, max_iter=20000)).fit(X, y))
    centre = np.concatenate([[b0], coef0])
    cov = np.cov(refits.T)
    table = {}
    for name, (f, v) in POINTS.items():
        row = pd.DataFrame([{"fuel": f, **{COL[k]: val for k, val in v.items()}}])
        a = np.concatenate([[1.0], per_fuel.design(row)[0]])
        z, se = float(centre @ a), float(np.sqrt(a @ cov @ a))
        keep = lambda zz: round(float(100 * (1 - 1 / (1 + np.exp(-zz)))), 1)
        lo, hi = np.percentile(100 * (1 - 1 / (1 + np.exp(-(refits @ a)))), per_fuel.RANGE)
        table[name] = {"from_the_refits_pct": [round(float(lo), 1), round(float(hi), 1)], "from_a_variance_table_pct": [keep(z + 1.645 * se), keep(z - 1.645 * se)]}
    facts["range_from_the_refits_against_a_variance_table"] = {"refits": int(len(refits)), "ranges": table}

    # Is the outcome separable? If it were, the fit would run away without a penalty.
    def no_penalty(Xa, ya):
        m = make_pipeline(StandardScaler(), LogisticRegression(C=1e6, max_iter=200000)).fit(Xa, ya)
        return round(float(roc_auc_score(ya, m.predict_proba(Xa)[:, 1])), 3)

    facts["training_auc_without_a_penalty"] = {
        "what": "1.000 would mean the two outcomes can be split perfectly and the coefficients have no finite answer",
        "both fuels, own slopes": no_penalty(X, y),
        **{k: no_penalty(clear.loc[fuel == k, NUM].to_numpy(float), y[fuel == k]) for k, _ in FUELS}}

    # Held out: what happened when the model was nearly certain?
    held = np.array([cross_val_predict(per_fuel.classifier(), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=SEED + r),
                                       method="predict_proba")[:, 1] for r in range(REPEATS)])
    keep, done = 1 - held, y == 0
    facts["held_out_near_certain_readings"] = {
        name: {"tests_per_repeat": round(float(sel.sum() / REPEATS), 1),
               "burned_to_completion_pct": round(float(100 * (sel & done).sum() / sel.sum()), 1) if sel.any() else None}
        for name, sel in (("model said under 1 %", keep < 0.01), ("model said over 99 %", keep > 0.99))}

    # Would a smaller methanol part do better? Same folds for every candidate, penalty fixed at the console's.
    c = float(read_metrics()["extinction"]["penalty_c_chosen"])
    base, n = train.design(clear), len(NUM)
    flag = base[:, n:]

    def own_slopes(keys):
        cols = [base[:, [i]] * flag for i, col in enumerate(NUM) if KEYS[col] in keys]
        return np.hstack([base] + cols)

    def shrunk(s):
        """Every own slope kept, but methanol's part penalised 1 / s squared times more (scaled after standardizing)."""
        w = np.concatenate([np.ones(n + 1), np.full(n, s)])
        return make_pipeline(StandardScaler(), FunctionTransformer(lambda Z: Z * w), LogisticRegression(C=c, max_iter=20000))

    plain = lambda: make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=20000))
    candidates = {
        "console model: own slope for every setting": (X, plain),
        "methanol's own slopes penalised 4 times more": (X, lambda: shrunk(0.5)),
        "methanol's own slopes penalised 16 times more": (X, lambda: shrunk(0.25)),
        "own slopes for oxygen and droplet size only": (own_slopes({"o2", "d0"}), plain),
        "own slope for oxygen only": (own_slopes({"o2"}), plain),
        "one set of slopes (the earlier model's shape)": (base, plain),
    }
    meth = fuel == "methanol"
    table = {}
    for name, (Xc, make) in candidates.items():
        aucs, briers, m_aucs, m_briers, preds = [], [], [], [], []
        for r in range(REPEATS):
            p = cross_val_predict(make(), Xc, y, cv=StratifiedKFold(5, shuffle=True, random_state=SEED + r), method="predict_proba")[:, 1]
            aucs.append(roc_auc_score(y, p)); briers.append(brier_score_loss(y, p))
            m_aucs.append(roc_auc_score(y[meth], p[meth])); m_briers.append(brier_score_loss(y[meth], p[meth])); preds.append(p)
        mk = 1 - np.array(preds)[:, meth]
        mid = (mk >= 0.3) & (mk < 0.65)
        table[name] = {"auc": round(float(np.mean(aucs)), 3), "brier": round(float(np.mean(briers)), 4),
                       "methanol_auc": round(float(np.mean(m_aucs)), 3), "methanol_brier": round(float(np.mean(m_briers)), 4),
                       "methanol_30_to_65_pct_band": {"tests_per_repeat": round(float(mid.sum() / REPEATS), 1),
                                                      "model_said_pct": round(float(100 * mk[mid].mean()), 1) if mid.any() else None,
                                                      "happened_pct": round(float(100 * (mid & (y[meth] == 0)).sum() / mid.sum()), 1) if mid.any() else None}}
    facts["smaller_methanol_models_held_out"] = {"penalty_c": c, "candidates": table}

    # Pressure: does adding the tests above the limit settle which way it pushes?
    wide = df[df["pressure_atm"].notna() & df["d0_mm"].notna() & df["test_end"].isin(["Extinction", "Completion"])]
    ip = NUM.index(COL["p"])
    slopes = {}
    for name, frame in (("tests in scope", clear), ("with the tests above the pressure limit", wide)):
        Xp, yp = per_fuel.design(frame), (frame["test_end"] == "Extinction").to_numpy(int)
        rng, values = np.random.default_rng(SEED), {k: [] for k, _ in FUELS}
        while len(values["heptane"]) < 400:
            s = rng.integers(0, len(yp), len(yp))
            if yp[s].min() == yp[s].max():
                continue
            coef = train.raw_coefficients(make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=20000)).fit(Xp[s], yp[s]))[1]
            values["heptane"].append(coef[ip]); values["methanol"].append(coef[ip] + coef[n + 1 + ip])
        slopes[name] = {k: {"share_of_refits_where_more_pressure_means_more_likely_to_go_out": round(float(np.mean(np.array(v) > 0)), 2),
                            "middle_slope_per_atm": round(float(np.median(v)), 2)} for k, v in values.items()}
    facts["pressure_slope"] = slopes
    return facts


def read_metrics():
    return json.loads(per_fuel.OUT_METRICS.read_text(encoding="utf-8"))


def main():
    df = pd.read_csv(per_fuel.CLEAN)
    audit = {"made_by": "model/design_audit.py", "data": data_facts(df), "fitted": fitted_facts(df)}
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(audit["fitted"]["readings"], indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
