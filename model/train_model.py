# ==============================
# NSL-KDD Intrusion Detection System
# ==============================

# 1. IMPORT LIBRARIES
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

import torch
from sklearn import preprocessing
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_selection import mutual_info_classif, SelectKBest
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import (confusion_matrix, classification_report,
                             accuracy_score, recall_score,
                             precision_score, f1_score, roc_auc_score)
import joblib
import pickle

# ==============================
# 2. READ DATASET
# ==============================
df = pd.read_csv("KDDTrain+.txt")

# Assign column names
columns = ['duration','protocol_type','service','flag','src_bytes','dst_bytes',
           'land','wrong_fragment','urgent','hot','num_failed_logins','logged_in',
           'num_compromised','root_shell','su_attempted','num_root',
           'num_file_creations','num_shells','num_access_files',
           'num_outbound_cmds','is_host_login','is_guest_login','count',
           'srv_count','serror_rate','srv_serror_rate','rerror_rate',
           'srv_rerror_rate','same_srv_rate','diff_srv_rate',
           'srv_diff_host_rate','dst_host_count','dst_host_srv_count',
           'dst_host_same_srv_rate','dst_host_diff_srv_rate',
           'dst_host_same_src_port_rate','dst_host_srv_diff_host_rate',
           'dst_host_serror_rate','dst_host_srv_serror_rate',
           'dst_host_rerror_rate','dst_host_srv_rerror_rate',
           'attack','level']

df.columns = columns

# ==============================
# 3. DATA CLEANING
# ==============================

# Convert attack labels to binary
df['attack'] = df['attack'].apply(lambda x: 'normal' if x == 'normal' else 'attack')

# ==============================
# 4. ENCODING
# ==============================
le = preprocessing.LabelEncoder()
cat_cols = ['protocol_type', 'service', 'flag', 'attack']

for col in cat_cols:
    df[col] = le.fit_transform(df[col])

# ==============================
# 5. TRAIN TEST SPLIT
# ==============================
X = df.drop(["attack"], axis=1)
y = df["attack"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=43
)

# ==============================
# 6. FEATURE SELECTION
# ==============================
mutual_info = mutual_info_classif(X_train, y_train)
mutual_info = pd.Series(mutual_info, index=X_train.columns)

# Select top 15 features
columns_selected = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes',
                    'dst_bytes', 'wrong_fragment', 'hot', 'logged_in',
                    'num_compromised', 'count', 'srv_count',
                    'serror_rate', 'srv_serror_rate', 'rerror_rate']

X_train = X_train[columns_selected]
X_test = X_test[columns_selected]

# ==============================
# 7. SCALING
# ==============================
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ==============================
# 8. MODEL TRAINING
# ==============================

# Logistic Regression
log_model = LogisticRegression(random_state=42)
log_model.fit(X_train, y_train)

# XGBoost
xgb_model = XGBClassifier(
    random_state=42,
    tree_method='hist',
    device='cuda'
)
xgb_model.fit(X_train, y_train)

# ==============================
# 9. EVALUATION FUNCTION
# ==============================
def evaluate_model(model, X_train, y_train, X_test, y_test):
    print("\n===== TEST SET =====")
    y_pred = model.predict(X_test)
    print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    print("\n===== TRAIN SET =====")
    y_train_pred = model.predict(X_train)
    print(confusion_matrix(y_train, y_train_pred))
    print(classification_report(y_train, y_train_pred))

# Evaluate models
evaluate_model(log_model, X_train, y_train, X_test, y_test)
evaluate_model(xgb_model, X_train, y_train, X_test, y_test)

# ==============================
# 10. HYPERPARAMETER TUNING
# ==============================
param_grid = {
    "n_estimators": [50, 100],
    "max_depth": [3, 6],
    "learning_rate": [0.05, 0.1],
    "subsample": [0.8],
    "colsample_bytree": [0.8]
}

grid = GridSearchCV(
    XGBClassifier(tree_method='hist', device='cuda'),
    param_grid,
    scoring="f1",
    n_jobs=1
)

grid.fit(X_train, y_train)

print("Best Params:", grid.best_params_)

# ==============================
# 11. FINAL MODEL
# ==============================
final_model = XGBClassifier(
    tree_method='hist',
    device='cuda',
    **grid.best_params_
)

final_model.fit(X_train, y_train)

# ==============================
# 12. FINAL EVALUATION
# ==============================
y_pred = final_model.predict(X_test)
y_prob = final_model.predict_proba(X_test)

print("\nFinal Model Performance:")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("F1 Score:", f1_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("AUC:", roc_auc_score(y_test, y_prob[:, 1]))

# ==============================
# 13. SAVE MODEL
# ==============================
joblib.dump(final_model, 'ids_model.pkl')

# with open('columns.pkl', 'wb') as f:
#     pickle.dump(columns_selected, f)

# Use ALL features
columns_selected = X.columns.tolist()

# Save ALL columns
with open('columns.pkl', 'wb') as f:
    pickle.dump(columns_selected, f)

print("\nModel and columns saved successfully!")
joblib.dump(scaler, 'scaler.pkl')
