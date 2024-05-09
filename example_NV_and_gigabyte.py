import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Input stock tickers
gigabyte = "2376.TW"  # Gigabyte
nvidia = "NVDA"  # Nvidia

# Download historical data for both stocks
df_gigabyte = yf.download(gigabyte, period="5y")
df_nvidia = yf.download(nvidia, period="5y")

# Combine the closing prices of both stocks into a single DataFrame
df = pd.DataFrame(index=df_gigabyte.index)
df['Gigabyte'] = df_gigabyte['Close']
df['Nvidia_USD'] = df_nvidia['Close']  # Nvidia prices in USD

# Create lagged features for Nvidia closing prices
N = 2  # Number of lagged days to consider
for i in range(1, N+1):
    df[f'Nvidia_Lagged_{i}'] = df['Nvidia_USD'].shift(i)

# Drop rows with NaN values (due to the lag)
df.dropna(inplace=True)

# Define features and target variable
X = df.drop(columns=['Gigabyte', 'Nvidia_USD'])  # Features
y = df['Gigabyte']  # Target variable

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a random forest regressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions on the testing set
predictions = model.predict(X_test)

# Calculate RMSE (Root Mean Squared Error)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
print("Root Mean Squared Error:", rmse)

# Make predictions for the entire dataset
df['Predictions'] = np.nan
df.loc[df.index[-len(predictions):], 'Predictions'] = predictions

# Plotting the results
plt.figure(figsize=(14, 7))

# Plot Nvidia closing prices in USD
nvidia_line, = plt.plot(df.index, df['Nvidia_USD'], label='Nvidia (USD)', color='green')

# Create a twin Axes sharing the xaxis
ax2 = plt.gca().twinx()

# Plot Gigabyte closing prices in TWD
gigabyte_line, = ax2.plot(df.index, df['Gigabyte'], label='Gigabyte (TWD)', color='blue')

# Plot predicted Gigabyte prices in TWD
prediction_line, = ax2.plot(df.index, df['Predictions'], label='Predicted Gigabyte (TWD)', color='red', linestyle='--')

# Combine legends
lines = [nvidia_line, gigabyte_line, prediction_line]
labels = [line.get_label() for line in lines]

# Show single legend
plt.legend(lines, labels, loc='upper left')

# Set labels
plt.title('Nvidia (USD) and Gigabyte (TWD) Stock Prices')
plt.xlabel('Date')
plt.ylabel('Price')
plt.grid(True)
plt.show()
