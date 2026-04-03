import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import pickle

# -------------------------------
# 1. LOAD DATA
# -------------------------------
df = pd.read_csv('../data/KDDTrain+_20Percent.txt', header=None)

# Remove last column (difficulty)
df = df.iloc[:, :-1]

# -------------------------------
# 2. SPLIT FEATURES & LABEL
# -------------------------------
X = df.iloc[:, :-1]
y = df.iloc[:, -1]

# Convert labels: normal = 0, attack = 1
y = y.apply(lambda x: 0 if x == "normal" else 1)

# -------------------------------
# 3. ENCODING
# -------------------------------
X = pd.get_dummies(X)

# ✅ Save columns BEFORE converting to numpy
columns = X.columns.astype(str)

# -------------------------------
# 4. CONVERT TO NUMPY
# -------------------------------
X = X.values
y = y.values

# -------------------------------
# 5. TRAIN-TEST SPLIT
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------
# 6. TRAIN MODEL (BALANCED)
# -------------------------------
model = RandomForestClassifier(
    n_estimators=100,
    class_weight='balanced',
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------------
# 7. EVALUATE MODEL
# -------------------------------
y_pred = model.predict(X_test)

# ✅ Accuracy
accuracy = accuracy_score(y_test, y_pred)
print("\n🎯 Accuracy:", accuracy)

# ✅ Classification Report
print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

# ✅ Confusion Matrix
print("\n📌 Confusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

# -------------------------------
# 8. SAVE MODEL
# -------------------------------
joblib.dump(model, 'ids_model.pkl')

# -------------------------------
# 9. SAVE COLUMNS
# -------------------------------
with open('columns.pkl', 'wb') as f:
    pickle.dump(list(columns), f)

print("\n✅ Model + columns saved successfully!")