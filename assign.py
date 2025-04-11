import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Generate Hypothetical Dataset
data_size = 500
np.random.seed(42)

data = {
    'Engine_Size': np.random.uniform(1.0, 5.0, data_size),  # in liters
    'Horsepower': np.random.randint(70, 400, data_size),
    'Weight': np.random.randint(800, 2500, data_size),  # in kg
    'Aerodynamic_Drag': np.random.uniform(0.2, 0.4, data_size),
    'Fuel_Efficiency': np.random.uniform(8, 30, data_size) - np.random.normal(0, 2, data_size)  # mpg
}

df = pd.DataFrame(data)

# Step 2: Data Preprocessing
# Handling missing values (if any)
df.fillna(df.mean(), inplace=True)

# Feature Scaling
scaler = StandardScaler()
X = df.drop(columns=['Fuel_Efficiency'])
y = df['Fuel_Efficiency']
X_scaled = scaler.fit_transform(X)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Step 3: Model Selection and Training
models = {
    'Linear Regression': LinearRegression(),
    'Decision Tree': DecisionTreeRegressor()
}

results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    results[name] = {'MAE': mae, 'RMSE': rmse}

# Step 4: Visualization
results_df = pd.DataFrame(results).T
print(results_df)

# Plot feature importance for Decision Tree
feature_importance = models['Decision Tree'].feature_importances_
plt.figure(figsize=(8, 5))
sns.barplot(x=feature_importance, y=X.columns)
plt.xlabel('Feature Importance')
plt.title('Feature Importance in Decision Tree Model')
plt.show()

# Step 5: Reporting
results_df.to_csv("model_performance.csv", index=True)
print("Report generated successfully!")
