## Test Instructions

```sh
python3 aequitas.py
```
`aequitas.py` implements an one-shot Aequitas simulator in the synchronous setting, the parameters of the algorithm are:
1. Number of nodes: `n`
2. Number of byzantine nodes: `f`
3. Order fairness parameter: `γ`

   *Receive-Order-Fairness*: If sufficiently many (at least γ-fraction) nodes receive a transaction tx before another transaction tx', then all honest nodes must output tx before tx'. 1/2 < γ ≤ 1


### Example
In Example 3, Aequitas should output: `[{'a', 'e', 'c', 'b'}, {'d'}]`, 

which means the Aequitas algorithm treats transactions `{'a', 'e', 'c', 'b'}` as being of the same order, and this set as a whole(they are a strongly connected component in the graph) should be ordered in front of `'d'`
