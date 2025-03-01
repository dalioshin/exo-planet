import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load the CSV file
csv_file = '/media/desmond/d0cae9df-51c1-4e29-a35d-4f4dcfb25958/home/desmond/projects/exo-planet/scaled_cart_data.csv' 
df = pd.read_csv(csv_file)

# Assuming the last three columns are the 5th, 6th, and 7th columns (index 4, 5, 6)
x = df.iloc[:, 4]
y = df.iloc[:, 5]
z = df.iloc[:, 6]

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the data
ax.scatter(x, y, z, c='b', marker='o')

ax.view_init(elev=0, azim=0)

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

plt.show()