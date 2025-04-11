# Pyra - A High-level Linter for Data Science Software

<p align="center">
  <img src ="https://raw.githubusercontent.com/caterinaurban/Lyra/master/lyra.png" width="25%"/>
</p>

Pyra is a high-level linter static analyzer for data science applications written in Python, that helps developers identify potential issues in their data science code written in Python.

Pyra is based on the peer-reviewed publication:
> Greta Dolcetti, Agostino Cortesi, Caterina Urban, Enea Zaffanella. _**"Towards a High Level Linter for Data Science"**_. In Proceedings of the 10th ACM SIGPLAN International Workshop on Numerical and Symbolic Abstract Domains (NSAD 2024), co-located with SPLASH 2024.


### Abstract datatype analysis

Let us consider the following fragment. The code represents a simple data science pipeline that reads a CSV file, drops duplicates, plots the data, scales it, splits it into training and testing sets, and fits a logistic regression model.
```
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("data.csv")
# Columns: ['Fruit', 'Amount', 'Label']
result = df.drop_duplicates(inplace=True)

plt.plot(df["Fruit"], df["Amount"])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[["Amount"]])

X_train, X_test, y_train, y_test =
    train_test_split(X_scaled, df["Label"])

model = LogisticRegression()
model.fit(X_train, y_train)
```

The code fragment contains several issues that could lead to misleading results and challenges in reproducibility:

- The `drop_duplicates` method is called with `inplace=True`, which modifies the DataFrame in place and returns `None`. This can lead to confusion, as the variable `result` will be assigned `None`.
- The `plot` method is used to create a line plot with a categorical *x*-axis. This is inappropriate, as line plots are typically used for continuous data. A bar plot would be more suitable in this case.
- The `train_test_split` method is called without setting the `random_state` parameter, meaning the split will differ each time the code is run. This can result in non-reproducible outcomes.
- The data is scaled before the train-test split. This can cause data leakage, as the scaling parameters are computed using the entire dataset, including the test set. The scaling should be performed **after** the split to avoid this issue.

Pyra detects these issues and raises warnings, and raises the following warnings:

![warnings](https://github.com/user-attachments/assets/6c11faed-2bdb-4648-94a3-2f8e33295d69)

## Getting Started 


### Prerequisites

* Install **Git**

* Install [**Python 3.6**](http://www.python.org/)

* Install ``virtualenv``:

    | Linux or Mac OS X                     |
    | ------------------------------------- |
    | `python3.6 -m pip install virtualenv` |


### Installation

* Create a virtual Python environment:

    | Linux or Mac OS X                     |
    | ------------------------------------- |
    | `virtualenv --python=python3.6 <env>` |

* Install Lyra in the virtual environment:

    | Linux or Mac OS X                                                       |
    | ----------------------------------------------------------------------- |
    | `./<env>/bin/pip install git+https://github.com/caterinaurban/Lyra.git` | 
    
### Command Line Usage

To analyze a specific Python program run:

   | Linux or Mac OS X                            |
   | ---------------------------------------------|
   | `./<env>/bin/lyra [OPTIONS] path-to-file.py` | 
   
The following command line options are recognized:

    --analysis [ANALYSIS]   
    
                Sets the static analysis to be performed. Possible analysis options are:
                * ``usage`` (input data usage analysis based on syntactic variable dependencies)
                * ``liveness`` (input data usage analysis based on strongly live variable analysis)
                * ``interval`` (interval analysis)
                Default: ``usage``.

After the analysis, Lyra generates a PDF file showing the control flow graph of the program
annotated with the result of the analysis before and after each statement in the program.

## Documentation

Lyra's documentation is available online: http://caterinaurban.github.io/Lyra/

## Authors

* **Caterina Urban**, ETH Zurich, Switzerland

## Contributors

* **Simon Wehrli**, ETH Zurich, Switzerland
* **Madelin Schumacher**, ETH Zurich, Switzerland
* **Jérôme Dohrau**, ETH Zurich, Switzerland
* **Lowis Engel**, ETH Zurich, Switzerland
