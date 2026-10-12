"""Dataset analytics used by the home page and dashboard (Plotly figure dicts)."""
import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

from ml.preprocessing import DATASET_PATH, TARGET, DatasetError, load_and_clean

from .rules import CATEGORY_ORDER, RISK_ORDER, assess_risk, categorize

METRICS_PATH = Path(DATASET_PATH).parent / "metrics.json"
COLORS = {"primary": "#4f46e5", "teal": "#0d9488", "amber": "#f59e0b",
          "red": "#ef4444", "green": "#22c55e", "grey": "#94a3b8"}
CAT_COLORS = ["#22c55e", "#0d9488", "#4f46e5", "#f59e0b", "#ef4444"]
RISK_COLORS = {"Low": "#22c55e", "Medium": "#f59e0b", "High": "#ef4444"}


def base_layout(title="", **extra):
    layout = {"title": {"text": title, "font": {"size": 15}},
              "margin": {"l": 45, "r": 15, "t": 45, "b": 45},
              "paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)",
              "font": {"family": "Inter, sans-serif", "size": 12}}
    layout.update(extra)
    return layout


def load_metrics():
    try:
        return json.loads(METRICS_PATH.read_text())
    except (OSError, ValueError):
        return None


@lru_cache(maxsize=1)
def _dataset():
    return load_and_clean()


def home_stats():
    """Real numbers from metrics.json - or None if unavailable."""
    m = load_metrics()
    if not m:
        return None
    best = next(r for r in m["models"] if r["name"] == m["best_model"])
    return {"rows": m["dataset"]["rows"], "features": len(m["dataset"]["features"]),
            "models": len(m["models"]), "best_model": m["best_model"],
            "best_r2": best["r2"], "synthetic": m["dataset"]["synthetic"]}


def _risk_for_row(row):
    d = {"failures": row.failures, "absences": row.absences, "g1": row.G1,
         "g2": row.G2, "studytime": row.studytime}
    return assess_risk(row.G3 * 5, d)[0]


def build_dashboard():
    """Return (stats, charts, metrics). Raises DatasetError if the data is missing."""
    df = _dataset()
    score = df[TARGET] * 5                                  # percentage
    cats = score.map(categorize)
    risks = pd.Series([_risk_for_row(r) for r in df.itertuples()])
    risk_counts = {k: int((risks == k).sum()) for k in RISK_ORDER}
    cat_counts = {k: int((cats == k).sum()) for k in CATEGORY_ORDER}

    stats = {"total": int(len(df)), "average": round(float(score.mean()), 1),
             "highest": round(float(score.max()), 1), "lowest": round(float(score.min()), 1),
             "avg_absences": round(float(df["absences"].mean()), 1),
             "high": risk_counts["High"], "medium": risk_counts["Medium"],
             "low": risk_counts["Low"]}

    sample = df.sample(min(len(df), 400), random_state=1)
    by_study = (df.assign(score=score).groupby("studytime")["score"].mean().round(1))
    charts = {
        "marks_hist": {"data": [{"type": "histogram", "x": score.tolist(), "nbinsx": 12,
                                 "marker": {"color": COLORS["primary"]}}],
                       "layout": base_layout("Marks distribution (%)",
                                             xaxis={"title": "Final marks (%)"},
                                             yaxis={"title": "Students"})},
        "absences_scatter": {"data": [{"type": "scatter", "mode": "markers",
                                       "x": sample["absences"].tolist(),
                                       "y": (sample[TARGET] * 5).tolist(),
                                       "marker": {"color": COLORS["teal"], "opacity": .6}}],
                             "layout": base_layout("Absences vs marks",
                                                   xaxis={"title": "Absences"},
                                                   yaxis={"title": "Final marks (%)"})},
        "study_bar": {"data": [{"type": "bar",
                                "x": [f"Band {k}" for k in by_study.index],
                                "y": by_study.tolist(),
                                "marker": {"color": COLORS["amber"]}}],
                      "layout": base_layout("Study time band vs average marks",
                                            yaxis={"title": "Average marks (%)"})},
        "category_bar": {"data": [{"type": "bar", "x": CATEGORY_ORDER,
                                   "y": [cat_counts[c] for c in CATEGORY_ORDER],
                                   "marker": {"color": CAT_COLORS}}],
                         "layout": base_layout("Performance categories")},
        "risk_pie": {"data": [{"type": "pie", "hole": .55, "labels": RISK_ORDER,
                               "values": [risk_counts[k] for k in RISK_ORDER],
                               "marker": {"colors": [RISK_COLORS[k] for k in RISK_ORDER]}}],
                     "layout": base_layout("Risk levels")},
    }
    metrics = load_metrics()
    if metrics:
        names = [r["name"] for r in metrics["models"]]
        charts["model_bar"] = {"data": [{"type": "bar", "x": names,
                                         "y": [r["r2"] for r in metrics["models"]],
                                         "marker": {"color": COLORS["primary"]}}],
                               "layout": base_layout("Model comparison (R² score)",
                                                     yaxis={"title": "R²", "range": [0, 1]})}
    return stats, charts, metrics


def class_average():
    """Average G1, G2, G3 as percentages (for the detail page chart)."""
    df = _dataset()
    return {"g1": round(float(df["G1"].mean()) * 5, 1),
            "g2": round(float(df["G2"].mean()) * 5, 1),
            "g3": round(float(df[TARGET].mean()) * 5, 1)}
