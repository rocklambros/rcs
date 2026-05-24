# Adversarial-Attack Library Cheatsheet

When to use which Python library. All are open-source; pick by ecosystem.

## torchattacks (PyTorch only)

- **Use when:** model is in PyTorch and you want the broadest attack catalog with a unified API
- **Includes:** FGSM, PGD, CW, AutoAttack (wrapper), DeepFool, Square, etc.
- **Install:** `pip install torchattacks==3.5.1`
- **Pattern:** `atk = torchattacks.PGD(model, eps=8/255, alpha=2/255, steps=20)` → `x_adv = atk(x, y)`

## foolbox (PyTorch / TF / JAX)

- **Use when:** model is in TF or JAX, OR you need framework-agnostic attacks
- **Includes:** FGSM, PGD, CW, DeepFool, Boundary Attack, Hop Skip Jump
- **Install:** `pip install foolbox==3.3.4`
- **Pattern:** `fmodel = fb.PyTorchModel(model, bounds=(0,1))` → `_, x_adv, success = atk(fmodel, x, y, epsilons=8/255)`

## autoattack (the original)

- **Use when:** you want the canonical AutoAttack implementation for benchmark-comparable numbers
- **Includes:** APGD-CE, APGD-DLR, FAB, Square (the four-component "standard" version)
- **Install:** `pip install git+https://github.com/fra31/auto-attack@v0.1`
- **Pattern:** `adversary = AutoAttack(model, norm='Linf', eps=8/255, version='standard')` → `x_adv = adversary.run_standard_evaluation(x, y, bs=128)`
- **Note:** This is the implementation RobustBench uses; numbers here are directly comparable to the leaderboard

## CleverHans (TF / PyTorch / JAX, maintained by Google / OpenAI alumni)

- **Use when:** you want a research-historical implementation; less actively maintained than the others
- **Includes:** FGSM, PGD, CW, MIM, JSMA
- **Install:** `pip install cleverhans==4.0.0`
- **Pattern:** functional API; `x_adv = projected_gradient_descent(model_fn, x, eps, alpha, steps, norm)`

## Recommendation order

1. PyTorch model? → torchattacks for FGSM / PGD; autoattack for the AutoAttack number
2. TF or JAX model? → foolbox
3. Tabular model (XGBoost, sklearn)? → CleverHans gradient-free attacks (Square Attack), OR write a custom PGD using JAX's grad transformations on a surrogate differentiable model

## Common cross-library pitfalls

- **Input scaling:** torchattacks expects inputs in `[0, 1]`. If your model takes ImageNet-normalized inputs, wrap the model so attacks operate on `[0, 1]` and the normalization happens inside the forward pass.
- **Label types:** different libraries expect int64 vs int32 vs one-hot. Check the docs.
- **Eval mode:** `model.eval()` BEFORE calling the attack. BatchNorm / Dropout in train mode silently degrade attack strength.
- **Device:** attacks must run on the same device as the model. Mixing CPU + GPU silently fails on some libraries.
