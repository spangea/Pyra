from sklearn.cluster import KMeans
import numpy as np

# STATE: X -> Top; kmeans -> Top
X = np.array([[1, 2], [1, 4], [1, 0], [10, 2], [10, 4], [10, 0]])
# STATE: X -> Array; kmeans -> Top
kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto")
# FINAL: X -> Array; kmeans -> Top