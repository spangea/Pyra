import torch

a = torch.save({}, "path") # NoneRet
print(a)
# FINAL: a -> NoneRet