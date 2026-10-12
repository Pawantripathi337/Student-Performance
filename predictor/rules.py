"""Rule-based logic: category, risk level, explanation, recommendations.

Everything here is plain if/else so it is easy to explain in a viva.
NOTE: the risk level is a simple educational indicator - it is NOT a
professionally validated assessment of any student.
"""

# (minimum percentage, label) - checked from the top
CATEGORIES = [(90, "Excellent"), (75, "Good"), (60, "Average"),
              (40, "Needs Improvement"), (0, "Poor")]
CATEGORY_ORDER = [c[1] for c in CATEGORIES]
RISK_ORDER = ["Low", "Medium", "High"]
STUDY_BANDS = {1: "under 2 hours/week", 2: "2-5 hours/week",
               3: "5-10 hours/week", 4: "over 10 hours/week"}


def categorize(score):
    """score is a percentage (0-100)."""
    for minimum, label in CATEGORIES:
        if score >= minimum:
            return label
    return "Poor"


def assess_risk(score, d):
    """Return (level, reasons). Points system: 0-1 Low, 2-4 Medium, 5+ High."""
    points, reasons = 0, []
    if score < 40:
        points += 3; reasons.append("predicted score is below 40%")
    elif score < 60:
        points += 2; reasons.append("predicted score is below 60%")
    elif score < 75:
        points += 1; reasons.append("predicted score is below 75%")
    if d["failures"] >= 2:
        points += 2; reasons.append("two or more previous failures")
    elif d["failures"] == 1:
        points += 1; reasons.append("one previous failure")
    if d["absences"] > 15:
        points += 2; reasons.append("a high number of absences")
    elif d["absences"] > 8:
        points += 1; reasons.append("a moderate number of absences")
    if d["g2"] <= d["g1"] - 2:
        points += 1; reasons.append("marks dropped between the two periods")
    if d["studytime"] == 1:
        points += 1; reasons.append("very low weekly study time")
    level = "High" if points >= 5 else "Medium" if points >= 2 else "Low"
    return level, reasons


def recommendations(score, d):
    tips = []
    if d["absences"] > 8:
        tips.append("Improve class attendance - aim for at least 75% attendance and "
                    "avoid unnecessary absences.")
    if d["studytime"] <= 1:
        tips.append("Increase focused study time gradually, for example by adding "
                    "30 minutes per day.")
    if d["failures"] >= 1:
        tips.append("Revisit topics from subjects you failed earlier and ask teachers "
                    "or classmates for help.")
    if d["g2"] < d["g1"]:
        tips.append("Your marks dropped in the second period - review recent topics "
                    "and practise past questions.")
    if d["g2"] < 10:
        tips.append("Strengthen the basics first: revise fundamental concepts before "
                    "moving to advanced topics.")
    if score < 60 and d["schoolsup"] == "no":
        tips.append("Consider extra classes, tutoring or doubt-clearing sessions.")
    if d["goout"] >= 4 and score < 75:
        tips.append("Balance social time and study time with a weekly timetable.")
    if score >= 75:
        tips.append("Maintain your current study routine and keep revising regularly.")
    if not tips:
        tips.append("Keep up regular study habits and revise a little every day.")
    return tips


def explanation(score, category, d):
    """One or two plain-English sentences about the prediction."""
    drivers = [f"previous period marks ({d['g1']} and {d['g2']} out of 20)",
               f"{d['absences']} absences",
               f"study time ({STUDY_BANDS.get(d['studytime'], 'n/a')})"]
    if d["failures"]:
        drivers.append(f"{d['failures']} previous failure(s)")
    outcome = {"Excellent": "an excellent", "Good": "a good", "Average": "an average",
               "Needs Improvement": "a below-average", "Poor": "a weak"}[category]
    return (f"Based on the student's {', '.join(drivers[:-1])} and {drivers[-1]}, "
            f"the model predicts {outcome} academic outcome ({score:.1f}%).")
