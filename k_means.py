from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np 
import pandas as pd



features = ["trips_per_month", "pct_airport", "pct_wait_save",
            "pct_booked", "avg_km", "pct_rush_hour"]
skewed = ["trips_per_month", "avg_km"]


# 1. standardization 

X_input = riders[features].copy()
X_input[skewed] = np.log1p(X_input[skewed])         # log transform the count variables
X_input = X_input.fillna(X_input.median())          # fill in the NULL cells with median value 



