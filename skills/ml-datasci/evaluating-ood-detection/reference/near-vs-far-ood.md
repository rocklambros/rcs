# Near-OOD vs far-OOD

The single biggest mistake in OOD evaluation is reporting only far-OOD AUROC. Far-OOD is easy — almost any detector hits 0.95+. Near-OOD is what matters in deployment.

## Definitions

- **Near-OOD**: same domain as training, novel class or novel style. The model has seen "things like this" but not "this thing".
- **Far-OOD**: different domain entirely. The model has never seen anything from this distribution.

## Worked examples by domain

### Vision

- Train: 10 ImageNet classes (e.g., dogs, cats, cars, ...)
- Near-OOD: 10 OTHER ImageNet classes (e.g., birds, planes, boats) — same image style, novel class
- Far-OOD: CIFAR-100 resized to ImageNet resolution — different resolution, different style, different distribution

- Train: chest X-rays (positive vs negative for pneumonia)
- Near-OOD: chest X-rays from a different scanner / hospital with subtle distribution shift
- Far-OOD: abdominal X-rays, or photographs of cats

### NLP

- Train: news articles in 5 topics (politics, sports, business, tech, entertainment)
- Near-OOD: news articles in OTHER topics (science, weather, lifestyle)
- Far-OOD: Twitter posts, or song lyrics, or code comments

### Tabular

- Train: credit card transactions from US customers in 2024
- Near-OOD: credit card transactions from US customers in 2026 (mild temporal drift)
- Far-OOD: bank-wire transactions (different schema, different population)

### Audio

- Train: speech in English
- Near-OOD: speech in a different English dialect with different acoustic conditions
- Far-OOD: instrumental music, or industrial noise

## Why near-OOD is harder

The model's learned features generalize within the training domain. A novel-class image from the same domain will activate the same low-level features as in-distribution inputs and may produce a confident wrong prediction with high softmax probability. Near-OOD detection requires the detector to be sensitive to fine-grained distinctions the classifier was not trained to make.

Far-OOD inputs typically activate very different low-level features (different texture statistics, different lexical distributions, different sensor characteristics) and are caught by even weak detectors.

## Curation guidance

- Build the near-OOD set from the SAME upstream source as training, just with novel classes held out
- Build the far-OOD set from a CLEARLY different source
- If you cannot find a natural near-OOD set, construct one by holding out k training classes; this is a common evaluation pattern (k-way leave-out)
- Document the curation procedure in the report — different near-OOD sets can yield different verdicts

## Reporting

Report metrics SEPARATELY for near-OOD and far-OOD. Do not average. The averaged number hides the near-OOD weakness behind the far-OOD strength.

If far-OOD AUROC = 0.99 and near-OOD AUROC = 0.65, the detector is near-useless for the realistic threat. Reporting the average (~0.82) misleads.
