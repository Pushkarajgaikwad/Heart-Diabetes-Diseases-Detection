# 🤖 Public Health AI: Heart Disease & Diabetes Prediction

This repository is a showcase of machine learning projects focused on the early detection of non-communicable diseases (NCDs), specifically heart disease and diabetes. This project was developed as part of my portfolio for the **Bharat Fellowship application**.

## 🎯 Problem Statement

In India, NCDs like heart disease and diabetes are a significant public health challenge, often leading to high mortality rates due to late diagnosis. This project aims to build reliable, low-cost, and scalable machine learning models that can serve as an **early warning system** using common clinical and demographic data. The goal is to make preliminary screening more accessible, especially in resource-limited areas.

## 🛠️ Tech Stack

* **Core:** Python, Pandas, NumPy, Scikit-learn
* **Ensemble Models:** XGBoost, LightGBM, CatBoost, StackingClassifier, VotingClassifier
* **Data Handling:** Imblearn (RandomOverSampler, SMOTETomek), KNNImputer
* **Visualization:** Matplotlib, Seaborn
* **Prototyping:** Jupyter Notebook, Pickle

---

## 🚀 Projects in this Repository

This repository contains two primary projects:

### 1. Heart Disease Prediction

This project uses data from the Framingham and Cleveland heart disease studies (sourced from Kaggle) to predict the 10-year risk of coronary heart disease (CHD).

* **Associated Files:**
    * `framingham_code.ipynb`
    * `combined_dataset code.ipynb`
* **Process:**
    1.  **Data Preprocessing:** Handled missing values using KNN Imputation.
    2.  **Balancing:** Addressed severe class imbalance using `SMOTETomek` and `RandomOverSampler`.
    3.  **Modeling:** Trained and evaluated multiple classifiers, including Logistic Regression, RandomForest, and XGBoost.
* **Results:**
    * A baseline **Logistic Regression** model achieved a solid **Accuracy of 88%** and an **F1
