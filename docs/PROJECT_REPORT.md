# Project Report: Smart Student Performance Prediction & Academic Analytics System

## 1. Abstract
Academic institutions often identify struggling students only after final exams. This project builds a web-based system that applies supervised machine learning (Linear Regression, Decision Tree, Random Forest) to student academic and background data to predict the final grade, classify performance into five categories and flag academic risk with explainable rules. A Django application provides a prediction form, a dashboard and a record store, and every model metric shown is computed from the data.

## 2. Introduction
Machine learning lets computers learn patterns from past data. Student records contain information such as earlier marks, absences and study habits that are related to final results. Using this data to give an early estimate can help teachers and students plan improvements.

## 3. Problem Statement
Teachers usually rely on manual observation to spot weak students, which is slow and subjective. There is a need for a simple tool that predicts the expected final score from available academic data and highlights students who may need support.

## 4. Objectives
- Predict a student's final score using regression models.
- Compare Linear Regression, Decision Tree and Random Forest using MAE, MSE, RMSE and R².
- Map predicted scores to performance categories and an explainable risk level.
- Provide rule-based recommendations and an analytics dashboard.
- Store predictions in a database and make them searchable.

## 5. Existing System
Manual analysis of mark sheets, spreadsheets and teacher judgement. Limitations: time-consuming, no prediction before results, inconsistent decisions, no visual analytics.

## 6. Proposed System
A Django web application with a trained ML model. The user enters student details; the model predicts the final score; rules produce category, risk and advice; results are saved in SQLite and shown on a dashboard.

## 7. Scope
Prediction and analytics for secondary-school style data with the features listed in section 11. Not covered: real-time data feeds, big-data processing, professional/psychological assessment.

## 8. Methodology
Dataset → loading → cleaning → EDA → feature selection → preprocessing → train/test split (80/20, random_state 42) → model training → evaluation → model selection (lowest RMSE) → save model (`model.pkl`) → Django prediction → result display.

## 9. System Architecture
Presentation layer (HTML/CSS/JS, Bootstrap, Plotly) → Application layer (Django views, forms, rules) → ML layer (`ml_model.py` loading a scikit-learn pipeline) → Data layer (SQLite + CSV dataset).

## 10. Data Flow
User form → validation → `ml_model.predict()` → score → `rules.py` (category, risk, tips) → saved as `PredictionRecord` → result page; dashboard reads the dataset and `metrics.json`.

## 11. Dataset Description
- Source used for the bundled run: Synthetic demo data (UCI-style columns); recommended real source: UCI *Student Performance* dataset (Cortez & Silva, 2008).
- Rows (after cleaning): 600; columns: 14.
- Features (13): age, studytime, failures, absences, G1, G2, freetime, goout, sex, schoolsup, famsup, activities, internet. Target: `G3` (final grade 0–20).
- Meaning of each column: see README → Dataset.

## 12. Data Preprocessing
Remove duplicates and missing values, convert columns to numeric types, drop out-of-range rows, scale numeric features with `StandardScaler`, one-hot encode categorical features (`sex`, `schoolsup`, `famsup`, `activities`, `internet`). All steps are inside a scikit-learn `Pipeline`, so the same transformation is applied at prediction time.

## 13. Exploratory Data Analysis
Shown on the dashboard: marks distribution, absences vs marks, study-time band vs average marks, category distribution and risk distribution. Typical findings to discuss: higher earlier marks and lower absences relate to higher final marks.

## 14. Algorithms
Linear Regression, Decision Tree Regressor (max_depth 6), Random Forest Regressor (200 trees) for the score; Logistic Regression for pass/fail. See `docs/ML_CONCEPTS.md`.

## 15. Model Evaluation
80/20 split: 480 training and 120 test rows. Metrics are in grade points (0–20).

> **Note:** the numbers below were produced on the bundled **synthetic demo dataset**. After switching to the real UCI file and re-running `ml/train_model.py`, replace this section with the new values from `docs/MODEL_RESULTS.md`.

| Model | MAE | MSE | RMSE | R² |
|---|---|---|---|---|
| Linear Regression | 0.9436 | 1.373 | 1.1717 | 0.9045 |
| Decision Tree | 1.0727 | 1.7074 | 1.3067 | 0.8812 |
| Random Forest | 1.0389 | 1.6213 | 1.2733 | 0.8872 |

Selected model (lowest RMSE): **Linear Regression**.

Same models without G1/G2:

| Model | MAE | MSE | RMSE | R² |
|---|---|---|---|---|
| Linear Regression | 2.8607 | 12.629 | 3.5537 | 0.1216 |
| Decision Tree | 3.0994 | 14.7862 | 3.8453 | -0.0284 |
| Random Forest | 3.008 | 13.5846 | 3.6857 | 0.0551 |

## 16. Results
Pass/fail classifier (Logistic Regression (pass/fail)): accuracy 0.9083, precision 0.9565, recall 0.8919, F1 0.9231.

Top Random Forest feature importances:
- G2: 0.8758
- G1: 0.042
- absences: 0.0189
- studytime: 0.0113
- goout: 0.0112
- age: 0.011
- freetime: 0.0096
- failures: 0.0041

## 17. Modules
1. Data & ML module (`ml/`) 2. Prediction module (`ml_model.py`) 3. Rules module (`rules.py`) 4. Web module (views, forms, templates) 5. Analytics module (`analytics.py`) 6. Records/database module (`models.py`, admin).

## 18. Hardware Requirements
Any computer with 4 GB RAM (8 GB recommended), dual-core CPU, 500 MB free disk space.

## 19. Software Requirements
Windows/macOS/Linux, Python 3.10+, Django, pandas, NumPy, scikit-learn, joblib, a modern web browser, internet access for CDN libraries.

## 20. Advantages
Simple and explainable models; early identification of struggling students; interactive dashboard; rule-based advice; easy to run locally.

## 21. Limitations
Predictions depend on dataset quality and size; the dataset comes from specific schools; no attendance percentage or assignment data; G1/G2 dominate the prediction; risk rules are simple and not professionally validated; CDN libraries need internet.

## 22. Future Scope
More data and features, cross-validation and tuning, student history tracking, PDF reports, teacher login, explainability tools such as SHAP, cloud deployment.

## 23. Conclusion
The system shows a complete supervised-learning workflow, from data cleaning to a deployed Django prediction service, and presents the results in an understandable way for teachers and students.

## 24. References
1. P. Cortez and A. Silva, "Using Data Mining to Predict Secondary School Student Performance," in Proc. 5th FUBUTEC Conference, 2008, pp. 5–12.
2. F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," Journal of Machine Learning Research, vol. 12, 2011.
3. Django Documentation, https://docs.djangoproject.com
4. scikit-learn User Guide, https://scikit-learn.org
5. UCI Machine Learning Repository – Student Performance dataset, https://archive.ics.uci.edu
