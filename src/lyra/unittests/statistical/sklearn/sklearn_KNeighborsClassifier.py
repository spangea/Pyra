from sklearn.neighbors import KNeighborsClassifier
# STATE:  X -> Top; neigh -> Top; neigh_fit -> Top; y -> Top
X = [[0], [1], [2], [3]]
# STATE: X -> List; neigh -> Top; neigh_fit -> Top; y -> Top
y = [0, 0, 1, 1]
# STATE: X -> List; neigh -> Top; neigh_fit -> Top; y -> NumericList
neigh = KNeighborsClassifier(n_neighbors=3)
# STATE: X -> List; neigh -> Top; neigh_fit -> Top; y -> NumericList
neigh_fit = neigh.fit(X, y)
# FINAL: X -> List; neigh -> Top; neigh_fit -> Top; y -> NumericList
