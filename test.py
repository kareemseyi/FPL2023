import numpy as np
np.random.seed(66)  # Set seed for replication
# Simulate Data Generating Process
n = 1000  # 1000 observations
x1 = np.random.uniform(-2,2,n)  # x_1 & x_2 between -2 and 2
x2 = np.random.uniform(-2,2,n)
p = 1 / (1 + np.exp( -1*(.75 + 1.5*x1 - .5*x2) ))  # Implement DGP
y = np.random.binomial(1, p, n)  # Draw outcomes
# Create dataset and print first few lines:
data = np.column_stack((x1,x2,y))
print(data[:10])