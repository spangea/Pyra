import torch
import pandas as pd
import numpy as np

a = torch.tensor([1, 2, 3])
b = torch.tensor([[1., -1.], [1., -1.]])
c = torch.tensor(np.array([[1, 2, 3], [4, 5, 6]]))
d = torch.zeros([2, 4], dtype=torch.int32)
e = torch.empty((2,3), dtype=torch.int64)
f = torch.absolute(torch.tensor([-1, -2, 3]))
g = torch.acos(f)
h = torch.arccos(f)
i = torch.acosh(f)
l = torch.arccosh(f)
m = torch.add(a, b)
#FINAL: a -> Tensor; b -> Tensor; c -> Tensor; d -> Tensor; e -> Tensor; f -> Tensor; g -> Tensor; h -> Tensor; i -> Tensor; l -> Tensor; m -> Tensor