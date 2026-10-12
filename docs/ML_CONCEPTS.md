# Machine Learning Concepts (viva-friendly)

**Machine Learning (ML):** programs that learn patterns from data instead of being given fixed rules.

**Supervised learning:** learning from examples that already have the correct answer (label). Here, each student has known features and a known final grade.

**Regression:** predicting a number (final score). **Classification:** predicting a class (pass/fail, or a category).

**Feature:** an input column (absences, G1, studytime…). **Target:** the output we predict (`G3`, the final grade).

**Linear Regression:** fits a straight-line (weighted sum) relationship: `score = w1·x1 + w2·x2 + … + b`. Fast and easy to explain; assumes roughly linear relationships.

**Decision Tree:** a flowchart of yes/no questions on features (e.g. "G2 > 12?") ending in a predicted value. Easy to visualise but can overfit if too deep.

**Random Forest:** many decision trees trained on random samples of data/features; predictions are averaged. Usually more stable and accurate than one tree, but harder to explain.

**Logistic Regression:** a classification model that outputs a probability (used here for pass/fail).

**Train-test split:** the data is divided (80% / 20%). The model learns on the training part and is judged on the unseen test part, so we measure real generalisation.

**Overfitting:** the model memorises training data and does badly on new data. **Underfitting:** the model is too simple to capture the pattern.

**MAE** (Mean Absolute Error): average size of the errors, `mean(|actual − predicted|)`. Easy to read (grade points).
**MSE** (Mean Squared Error): average of squared errors; punishes big errors more.
**RMSE:** square root of MSE; same unit as the target, so it is easy to interpret.
**R² score:** share of the variation in the target explained by the model. 1 = perfect, 0 = no better than predicting the average.

**Preprocessing:** cleaning data, scaling numbers (`StandardScaler`) and converting text categories to numbers (one-hot encoding).

**Why the final model was selected:** the app trains all three models on the same split and automatically picks the one with the lowest RMSE on the test set (ties can be checked with R²). The winner is stored in `ml/model.pkl` and named on the dashboard. On the bundled synthetic data, Linear Regression wins because that data was generated with mostly linear relationships; on real data the winner may differ, so quote your own results.
