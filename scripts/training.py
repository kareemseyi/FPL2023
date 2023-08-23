
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

import pandas as pd
import numpy as np







df = pd.read_csv('../Ballers.csv')
df.head()

x = df[['goals', 'assists', 'goal_contributions', 'points', 'minutes_played', 'clean_sheets']]
y = df[['goal_contributions_pgw', 'points_pgw']]




x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.2, random_state=10)

clf = LinearRegression()
clf.fit(x_train, y_train)
print((x_train))
