# Cours de référence — Algorithmique (entrée fixe du benchmark)

> Ce texte est l'**entrée unique** envoyée à TOUS les modèles du benchmark J2.
> Ne pas le modifier entre deux runs : la reproductibilité dépend d'une entrée
> identique. Il reprend le type de cours uploadé par le beta-testeur de M2.

## 1. Qu'est-ce qu'un algorithme ?

Un algorithme est une suite finie et non ambiguë d'instructions permettant de
résoudre un problème ou d'effectuer un calcul. Un bon algorithme se caractérise
par sa **correction** (il produit le bon résultat), sa **terminaison** (il
s'arrête) et son **efficacité** (en temps et en mémoire).

## 2. Complexité algorithmique

La complexité mesure l'évolution du nombre d'opérations en fonction de la taille
de l'entrée `n`. On utilise la notation de Landau (« grand O ») :

- `O(1)` : temps constant (accès à une case de tableau).
- `O(log n)` : logarithmique (recherche dichotomique).
- `O(n)` : linéaire (parcours d'une liste).
- `O(n log n)` : tri par fusion, tri rapide en moyenne.
- `O(n²)` : quadratique (tri à bulles, double boucle imbriquée).
- `O(2^n)` : exponentielle (force brute sur sous-ensembles).

On distingue la complexité dans le **meilleur cas**, le **cas moyen** et le
**pire cas**. Pour le tri rapide, le pire cas est `O(n²)` mais le cas moyen est
`O(n log n)`.

## 3. Structures de données fondamentales

- **Tableau (array)** : accès indexé en `O(1)`, insertion au milieu en `O(n)`.
- **Liste chaînée** : insertion/suppression en `O(1)` si on a le nœud, mais
  accès en `O(n)`.
- **Pile (stack)** : LIFO (dernier entré, premier sorti) — `push`, `pop`.
- **File (queue)** : FIFO (premier entré, premier sorti) — `enqueue`, `dequeue`.
- **Table de hachage** : accès moyen en `O(1)`, dégradé en `O(n)` en cas de
  collisions.
- **Arbre binaire de recherche** : recherche/insertion en `O(log n)` si
  équilibré, `O(n)` si dégénéré.

## 4. Algorithmes de tri

- **Tri à bulles** : compare et échange les éléments adjacents, `O(n²)`. Simple
  mais inefficace.
- **Tri par insertion** : efficace sur petites listes presque triées, `O(n²)`
  au pire, `O(n)` au meilleur.
- **Tri fusion (merge sort)** : diviser pour régner, `O(n log n)` garanti,
  stable, mais utilise `O(n)` de mémoire supplémentaire.
- **Tri rapide (quicksort)** : diviser pour régner autour d'un pivot,
  `O(n log n)` en moyenne, en place.

## 5. Recherche

- **Recherche linéaire** : parcourt tous les éléments, `O(n)`.
- **Recherche dichotomique** : sur un tableau **trié**, divise l'intervalle par
  deux à chaque étape, `O(log n)`.

## 6. Paradigmes de conception

- **Diviser pour régner** : découper le problème en sous-problèmes (tri fusion).
- **Programmation dynamique** : mémoriser les résultats des sous-problèmes pour
  éviter de les recalculer (suite de Fibonacci, sac à dos).
- **Algorithmes gloutons (greedy)** : choisir l'optimum local à chaque étape
  (rendu de monnaie, Dijkstra).
- **Retour sur trace (backtracking)** : explorer les solutions et revenir en
  arrière en cas d'impasse (problème des 8 reines, sudoku).

## 7. Récursivité

Une fonction récursive s'appelle elle-même sur un sous-problème plus petit. Elle
nécessite un **cas de base** (condition d'arrêt) et un **cas récursif**. Exemple :
la factorielle `n! = n × (n-1)!` avec `0! = 1`. Attention au débordement de pile
(stack overflow) si la profondeur de récursion est trop grande.
