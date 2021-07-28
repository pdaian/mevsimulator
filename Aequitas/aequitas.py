
import numpy as np
import networkx as nx
import random
from matplotlib import pyplot as plt

# number of nodes n
# number of byzantine / malicious nodes f
# gamma : order fairness parameter
# g : granularity

def aequitas():
  n_transaction_lists = []
  for _ in n_transaction_lists:
    granularize(each_transaction_list)
  compute_initial_set_of_edges(n_granularized_list_of_transactions)
  complete_list_of_edges()
  finalized_output_(graph, {transactions_present_in_all_lists})
  return

def granularize(transaction_ordering):
  # takes in transaction_ordering
  # with transaction and timestamp
  # output transactions eg to 0 to g, g+1 to 2g in 2nd slot
  return [{transactions}]

def compute_initial_set_of_edges():
  return [(a,b)] # returns a list of edges

def complete_list_of_edges():
  # builds graph and for every pair of vertices that are not
  # connected, look at common descendants
  # If there is a common descendant,
  # add (a,b) edge if a has more descendants
  # (b,a) if b has more descendants
  # deterministically (say alphabetically) if equal
  return dissected_graph

def setup_function(input_transaction_orderings)
  return {transactions_present_in_all_lists}

def finalized_output(graph, {transactions_present_in_all_lists}):
  # if they do, add an edge and then remove those that are not
  # fully connected
  return list


## TESTS
# // Example 1 : simple
# Node 1: [a,b,c,d,e]
# Node 2: [a,b,c,e,d]
# Node 3: [a,b,c,d,e]

# (a->b), (a->c), (a->d), (a->e)
#         (b->c), (b->d), (b->e)
#                 (c->d), (c->e)
#                         (d->e)
# // simple scenario, the graph is complete
# Final output ordering: a->b->c->d->e

# // Example 2: common descendant, and no common descendant
# Node 1: [a,b,c,e,d]
# Node 2: [a,c,b,d,e]
# Node 3: [b,a,c,e,d]
# Node 4: [a,b,d,c,e]
# Node 5: [a,c,b,d,e]

# gamma = 4/5 (to add an edge, you need x<y in 4 nodes)

# (a->b), (a->c), (a->d), (a->e)
#                 (b->d), (b->e)
#                 (c->d), (c->e)

# // b and e dont have an edge but they have a common descendant
# // Lets say, we add (b,c) as the edge deterministically
# // d and e dont have an edge but they dont have a common descendant either, i.e. they wont be output yet
# Final output ordering: :a->b->c

