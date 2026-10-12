"""
Train, compare and save the models.

    python ml/train_model.py
    python ml/train_model.py --data path/to/student-mat.csv --source "UCI Student Performance (Math)"

Outputs: ml/model.pkl, ml/metrics.json, docs/MODEL_RESULTS.md
All metrics are computed on the real test split - nothing is hard-coded.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error,
                             mean_squared_error, precision_score, r2_score,
                             recall_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor

ML_DIR = Path(__file__).resolve().parent
ROOT = ML_DIR.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.preprocessing import (FEATURES, PASS_MARK, TARGET, DatasetError,  # noqa: E402
                              load_and_clean, make_preprocessor)

MODEL_PATH = ML_DIR / "model.pkl"
METRICS_PATH = ML_DIR / "metrics.json"
INFO_PATH = ML_DIR / "dataset_info.json"
RESULTS_MD = ROOT / "docs" / "MODEL_RESULTS.md"
RANDOM_STATE = 42


def _models():
    return {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(max_depth=6, min_samples_leaf=5,
                                               random_state=RANDOM_STATE),
        "Random Forest": RandomForestRegressor(n_estimators=200, min_samples_leaf=2,
                                               random_state=RANDOM_STATE, n_jobs=-1),
    }


def _scores(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    return {"mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
            "mse": round(float(mse), 4),
            "rmse": round(float(np.sqrt(mse)), 4),
            "r2": round(float(r2_score(y_true, y_pred)), 4)}


def _compare(X_train, X_test, y_train, y_test, features):
    results, fitted = [], {}
    for name, est in _models().items():
        pipe = Pipeline([("prep", make_preprocessor(features)), ("model", est)])
        pipe.fit(X_train[features], y_train)
        pred = np.clip(pipe.predict(X_test[features]), 0, 20)
        results.append({"name": name, **_scores(y_test, pred)})
        fitted[name] = pipe
    return results, fitted


def train(data_path=None, source=None, save=True):
    df = load_and_clean(data_path)
    X, y = df[FEATURES], df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE)

    results, fitted = _compare(X_train, X_test, y_train, y_test, FEATURES)
    best = min(results, key=lambda r: r["rmse"])["name"]       # lowest RMSE wins

    # Honest extra experiment: the same models WITHOUT the G1/G2 period grades.
    no_grades = [f for f in FEATURES if f not in ("G1", "G2")]
    results_ng, _ = _compare(X_train, X_test, y_train, y_test, no_grades)

    # Classifier: pass (G3 >= 10) vs fail
    yc_train, yc_test = (y_train >= PASS_MARK).astype(int), (y_test >= PASS_MARK).astype(int)
    clf = Pipeline([("prep", make_preprocessor()),
                    ("model", LogisticRegression(max_iter=1000))])
    clf.fit(X_train, yc_train)
    yc_pred = clf.predict(X_test)
    classifier = {"name": "Logistic Regression (pass/fail)",
                  "accuracy": round(float(accuracy_score(yc_test, yc_pred)), 4),
                  "precision": round(float(precision_score(yc_test, yc_pred, zero_division=0)), 4),
                  "recall": round(float(recall_score(yc_test, yc_pred, zero_division=0)), 4),
                  "f1": round(float(f1_score(yc_test, yc_pred, zero_division=0)), 4)}

    # Feature importance from the Random Forest (for explanation / viva)
    rf = fitted["Random Forest"]
    names = rf.named_steps["prep"].get_feature_names_out()
    imps = rf.named_steps["model"].feature_importances_
    top = sorted(zip(names, imps), key=lambda t: -t[1])[:8]
    importance = [{"feature": n.split("__", 1)[-1], "importance": round(float(v), 4)}
                  for n, v in top]

    info = json.loads(INFO_PATH.read_text()) if INFO_PATH.exists() else {}
    dataset = {"source": source or info.get("source") or Path(data_path or "dataset.csv").name,
               "synthetic": bool(info.get("synthetic", False)) and not source,
               "rows": int(len(df)), "columns": int(df.shape[1]),
               "features": FEATURES, "target": TARGET}
    metrics = {"dataset": dataset,
               "split": {"train": int(len(X_train)), "test": int(len(X_test)),
                         "test_size": 0.2, "random_state": RANDOM_STATE},
               "models": results, "best_model": best,
               "without_grades": results_ng, "classifier": classifier,
               "feature_importance": importance,
               "trained_with": {"sklearn": sklearn.__version__,
                                "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M")}}

    bundle = {"regressor": fitted[best], "classifier": clf, "features": FEATURES,
              "best_model": best, "sklearn_version": sklearn.__version__}
    if save:
        if source:
            INFO_PATH.write_text(json.dumps({"source": source, "synthetic": False}, indent=2))
        joblib.dump(bundle, MODEL_PATH)
        METRICS_PATH.write_text(json.dumps(metrics, indent=2))
        RESULTS_MD.parent.mkdir(exist_ok=True)
        RESULTS_MD.write_text(_markdown(metrics))
    return bundle, metrics


def _table(rows):
    out = ["| Model | MAE | MSE | RMSE | R² |", "|---|---|---|---|---|"]
    out += [f"| {r['name']} | {r['mae']} | {r['mse']} | {r['rmse']} | {r['r2']} |" for r in rows]
    return "\n".join(out)


def _markdown(m):
    d, c = m["dataset"], m["classifier"]
    note = ("\n> ⚠️ These numbers come from the **synthetic demo dataset**, not real students."
            "\n> The demo data was generated with mostly linear relationships, so Linear Regression winning here is an artefact of that."
            "\n> Re-run training on the real UCI file and use those numbers in your report.\n"
            if d["synthetic"] else "")
    imp = "\n".join(f"- {i['feature']}: {i['importance']}" for i in m["feature_importance"])
    return f"""# Model Results (auto-generated by `ml/train_model.py`)
{note}
- Dataset: {d['source']} — {d['rows']} rows × {d['columns']} columns (after cleaning)
- Train/test split: {m['split']['train']} / {m['split']['test']} (random_state={m['split']['random_state']})
- Errors are in grade points on the 0–20 scale (multiply by 5 for percentage points)
- Trained {m['trained_with']['trained_at']} with scikit-learn {m['trained_with']['sklearn']}

## Regression model comparison (all features)
{_table(m['models'])}

**Selected model (lowest RMSE): {m['best_model']}**

## Same models WITHOUT G1/G2 (harder, more honest problem)
{_table(m['without_grades'])}

## Classifier ({c['name']})
Accuracy {c['accuracy']} · Precision {c['precision']} · Recall {c['recall']} · F1 {c['f1']}

## Top Random Forest feature importances
{imp}
"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", help="path to a CSV (UCI format is fine)")
    ap.add_argument("--source", help="human-readable dataset source name")
    args = ap.parse_args()
    try:
        _, mt = train(args.data, args.source)
    except DatasetError as exc:
        sys.exit(f"ERROR: {exc}")
    print(f"Dataset: {mt['dataset']['rows']} rows | best model: {mt['best_model']}")
    for r in mt["models"]:
        print(f"  {r['name']:<18} MAE={r['mae']} RMSE={r['rmse']} R2={r['r2']}")
    print("Saved ml/model.pkl, ml/metrics.json, docs/MODEL_RESULTS.md")
