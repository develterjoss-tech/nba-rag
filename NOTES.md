50 pages
1487 sections
longueur (mots) : min 1, médiane 245, max 2047


## Étape 4 — Embeddings

- Modèle : all-MiniLM-L6-v2, vecteurs de dimension 384, fenêtre de 256 tokens (les sections plus
  longues sont tronquées). Index : matrice (1487, 384) en cache dans data/interim/embeddings.npy
  (à supprimer si sections.json change).
- Règle de sélection : on garde le meilleur recall@5 sur dev ; si l'écart est inférieur à 0,1,
  on garde BM25 (plus simple, plus rapide).

### Comparaison sur dev (10 questions)

| Moteur | recall@5 | MRR | lexical | paraphrase | multi |
|---|---|---|---|---|---|
| random | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| BM25 | 0,62 | 0,49 | 0,79 | 0,50 | 0,50 |
| embeddings | 0,63 | 0,50 | 0,83 | 0,50 | 0,50 |
| hybrid (piste, hors règle) | 0,67 | 0,65 | 0,92 | 0,50 | 0,50 |

Écart BM25 / embeddings = 0,01 < 0,1 → moteur retenu : BM25. Dev n'a que 10 questions : les
écarts sont indicatifs.

### Analyse d'erreurs
(recopie ici les 4 exemples)

### Résultat test (BM25, une seule évaluation)
recall@5 = … / MRR = …