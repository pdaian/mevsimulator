import networkx as nx
import random
from typing import List
# number of nodes n
# number of byzantine / malicious nodes f
# gamma : order fairness parameter
# g : granularity

class Tx:
    def __init__(self, content, timestamp):
        self.content = content
        self.timestamp = timestamp #Unix timestamp
        self.bucket = None

    def __str__(self):
        return f'Transaction: {self.content} , {self.timestamp}'

    def __repr__(self):
        return f"Tx(content='{self.content}', timestamp={self.timestamp}, bucket = {self.bucket})"    

class Vote:
  nodeID: int
  ordering: List[Tx]

# Node 1: [a,b,c,e,d]
# Node 2: [a,c,b,d,e]
# Node 3: [b,a,c,e,d]
# Node 4: [a,b,d,c,e]
# Node 5: [a,c,b,d,e]

# assume this is already sorted, i.e. an ordering
n_tx_lists = {1: [Tx("a",1326244364), Tx("b",1326244365), Tx("c",1326244366), Tx("e",1326244367), Tx("d",1326244368), Tx("f",1326244369), Tx("g",1326244370)],
              2: [Tx("a",1326244364), Tx("c",1326244365), Tx("b",1326244366), Tx("d",1326244367), Tx("e",1326244368), Tx("f",1326244369), Tx("g",1326244375)],
              3: [Tx("b",1326244364), Tx("a",1326244365), Tx("c",1326244366), Tx("e",1326244367), Tx("d",1326244368), Tx("f",1326244376)],
              4: [Tx("a",1326244364), Tx("b",1326244365), Tx("d",1326244366), Tx("c",1326244367), Tx("e",1326244368)],
              5: [Tx("a",1326244364), Tx("c",1326244365), Tx("b",1326244366), Tx("d",1326244367), Tx("e",1326244368)]
              }

starting_timestamp = 1326244364
granularity = 5
n_granularized_tx_lists = {}

def granularize(tx_ordering, starting_timestamp: int ,granularity : int) -> List[Tx]:
  for tx in tx_ordering:
    quotient = int((tx.timestamp - starting_timestamp)//granularity)
    tx.bucket = quotient
  return tx_ordering

def aequitas():
  for i in n_tx_lists:
    n_granularized_tx_lists[i] = granularize(n_tx_lists.get(i), starting_timestamp, granularity)
  print(n_granularized_tx_lists)
  compute_initial_set_of_edges(n_granularized_tx_lists)
 
  # complete_list_of_edges()
  # finalized_output_(graph, {transactions_present_in_all_lists})
  # return


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

def setup_function(input_transaction_orderings):
  return {transactions_present_in_all_lists}

def finalized_output(graph, transactions_present_in_all_lists):
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

def main():
    aequitas()

if __name__ == "__main__":
    main()