# Viva Questions & Answers

## A. 20 Basic Questions
1. **What is your project about?** A Django web app that predicts a student's final score, performance category and academic risk using machine learning, with a dashboard and stored records.
2. **What is machine learning?** Computers learning patterns from data to make predictions without explicit rules.
3. **What is supervised learning?** Learning from labelled examples (features + known target).
4. **What is regression?** Predicting a continuous number, e.g. final score.
5. **What is classification?** Predicting a class label, e.g. pass/fail.
6. **Which problem type is the main task here?** Regression (final grade); pass/fail is a small classification extra.
7. **What is a feature?** An input variable such as absences or Period 2 marks.
8. **What is the target?** The value to predict: `G3`, the final grade (0–20).
9. **Which dataset did you use?** The UCI Student Performance dataset format; the bundled demo uses synthetic data in that format (state which one you used and its row count).
10. **Why not deep learning?** Not needed for small tabular data; simple models are faster and explainable.
11. **Which algorithms did you compare?** Linear Regression, Decision Tree, Random Forest (and Logistic Regression for pass/fail).
12. **What is train-test split?** Dividing data into a training part (80%) to learn and a test part (20%) to evaluate.
13. **Which metrics did you use?** MAE, MSE, RMSE and R².
14. **How was the best model chosen?** Lowest RMSE on the test set.
15. **What are the performance categories?** 90+ Excellent, 75–89 Good, 60–74 Average, 40–59 Needs Improvement, below 40 Poor.
16. **How is risk calculated?** A transparent points system using predicted score, failures, absences, mark trend and study time.
17. **Is the risk level scientifically validated?** No, it is a simple educational indicator.
18. **Where are predictions stored?** In an SQLite database through the `PredictionRecord` Django model.
19. **Which web framework did you use?** Django (Python).
20. **What are the limitations?** Limited, school-specific data; no attendance % or assignment data; estimates only.

## B. 20 Technical Questions
1. **Explain Linear Regression.** It fits `y = w·x + b` by minimising squared error; each weight shows a feature's effect.
2. **Explain a Decision Tree.** It splits data by feature thresholds that reduce error (variance) the most; leaves hold predicted values.
3. **Explain Random Forest.** An ensemble of trees trained on bootstrap samples with random feature subsets; the output is the average (bagging).
4. **Why can a Random Forest beat a single tree?** Averaging reduces variance and overfitting.
5. **What is overfitting? How do you reduce it?** Memorising training data. Use a test set, limit tree depth (`max_depth`), `min_samples_leaf`, more data, ensembles.
6. **What is underfitting?** A model too simple to capture patterns, giving high error on both train and test data.
7. **Define MAE.** Mean of absolute errors; average error in grade points.
8. **Define MSE and RMSE.** MSE is the mean squared error; RMSE is its square root, in the target's unit.
9. **Define R².** `1 − SSres/SStot`; the proportion of variance explained. Can be negative for very poor models.
10. **Why RMSE for selection?** It penalises large errors and is in grade points; R² is checked as well.
11. **What preprocessing did you do?** Cleaning (duplicates, missing, ranges), scaling numeric columns, one-hot encoding categorical columns.
12. **What is one-hot encoding?** Turning a category into 0/1 columns, e.g. `sex_F`, `sex_M`.
13. **Why scale features?** Linear models work better when features are on similar scales; trees do not need it but it is harmless.
14. **What is a scikit-learn Pipeline?** It chains preprocessing and model so the same steps run in training and prediction.
15. **What is feature engineering? Any in your project?** Creating/transforming features to help the model. Here we mainly select and encode features; the mark trend (G2 − G1) is used in the risk rules.
16. **How does Django use the model?** `ml_model.py` loads `model.pkl` once with joblib; the view sends form data as a DataFrame to `predict()`.
17. **What happens if the model file is missing or incompatible?** The app tries to retrain once; if that fails the user sees a friendly error message.
18. **How is form validation done?** Django `Form` fields with min/max values and custom error messages, plus server-side checks before prediction.
19. **Why do G1 and G2 dominate?** Past marks are strongly related to the final grade; so we also report results without them.
20. **What is `random_state`?** A seed that makes the split and the random forest reproducible.
