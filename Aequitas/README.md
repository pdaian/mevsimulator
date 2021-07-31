## Test Instructions

```sh
python3 aequitas.py
```

e.g. In Example 3, Aequitas should output: `[{'a', 'e', 'c', 'b'}, {'d'}]`, 

which means the Aequitas algorithm treats transactions `{'a', 'e', 'c', 'b'}` as being of the same order, and this set as a whole(they are a strongly connected component in the graph) should be ordered in front of `'d'`
