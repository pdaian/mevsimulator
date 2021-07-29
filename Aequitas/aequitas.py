import networkx as nx
import random
import itertools
from typing import Dict, List
# number of nodes n
# number of byzantine / malicious nodes f
# gamma : order fairness parameter
# g : granularity

class Tx:
    def __init__(self, content, timestamp, bucket = None):
        self.content = content
        self.timestamp = timestamp #Unix timestamp
        self.bucket = bucket

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
  """Puts txs into buckets
  line 10-12
  All transactions with timestamps [0,g-1] are in the same bucket, [g, 2g-1] are in the same bucket etc.
  """
  for tx in tx_ordering:
    quotient = int((tx.timestamp - starting_timestamp)//granularity)
    tx.bucket = quotient
  return tx_ordering

def get_all_tx_in_batch(tx_list: Dict[int, Tx]) -> Dict[int, Tx]:
 # TODO 
  return

def compute_initial_set_of_edges(tx_dict: Dict) -> nx.DiGraph:
  """
  line 15-25

  Args:

  Returns:
    need not be complete. Graph need not be acyclic
  """
  nodes = set()
  print(type(tx_dict))
  for key in tx_dict:
    for tx in tx_dict[key]:
      if tx.content not in nodes:
        nodes.add(tx.content)
  print(sorted(nodes))

  # Look at all possible combinations, i.e the edges
  undirected_edge_candidates = (list(itertools.combinations(nodes, 2)))
  n = len(nodes)
  assert(len(undirected_edge_candidates) == ((n**2-n)/2))
  print(sorted(undirected_edge_candidates, key = lambda x: (x[0],x[1])))

  # TODO: for each possible undirected_edge_candidates:

  G = nx.DiGraph()
  return G
# compute_initial_set_of_edges returns: 
# (a->b), (a->c), (a->d), (a->e)
#                (b->d), (b->e)
#                (c->d), (c->e)

def complete_list_of_edges(G: nx.DiGraph) -> nx.DiGraph:
  """
  line 28-48:
  builds graph and for every pair of vertices that are not
  connected, look at common descendants
  If there is a common descendant, 
    add (a,b) edge if a has more descendants
    (b,a) if b has more descendants
  deterministically (say alphabetically) if equal

  If there is no common descendant, then there is currently not enough information to order both a,b
  (one of them could still be ordered).
  Args:

  Returns: H, a fully connected graph
  """
  H = nx.DiGraph()
  return H

def finalize_output(H) -> List:
  """
  line 49-52:
  Compute the condensation graph of H(collapse the strongly connected components into a single vertex)
  Then topologically sort this graph and then output the sorting (Here, every index is a set of vertices)
  
  Returns: A list of final output ordering
  """
  condensed_DAG = nx.condensation(H)
  # TODO: need to keep track of which nodes gets condensed into one single node, because we need to output an ordering eventually
  output = list(nx.topological_sort(condensed_DAG))
  return output
# Final output ordering: [a,b,c]

def aequitas():
  for i in n_tx_lists:
    n_granularized_tx_lists[i] = granularize(n_tx_lists.get(i), starting_timestamp, granularity)
  print(n_granularized_tx_lists)
  
  cheating_dict = {
    1: [Tx(content='a', timestamp=1326244364, bucket = 0), Tx(content='b', timestamp=1326244365, bucket = 0), Tx(content='c', timestamp=1326244366, bucket = 0), Tx(content='e', timestamp=1326244367, bucket = 0), Tx(content='d', timestamp=1326244368, bucket = 0)],
    2: [Tx(content='a', timestamp=1326244364, bucket = 0), Tx(content='c', timestamp=1326244365, bucket = 0), Tx(content='b', timestamp=1326244366, bucket = 0), Tx(content='d', timestamp=1326244367, bucket = 0), Tx(content='e', timestamp=1326244368, bucket = 0)],
    3: [Tx(content='b', timestamp=1326244364, bucket = 0), Tx(content='a', timestamp=1326244365, bucket = 0), Tx(content='c', timestamp=1326244366, bucket = 0), Tx(content='e', timestamp=1326244367, bucket = 0), Tx(content='d', timestamp=1326244368, bucket = 0)], 
    4: [Tx(content='a', timestamp=1326244364, bucket = 0), Tx(content='b', timestamp=1326244365, bucket = 0), Tx(content='d', timestamp=1326244366, bucket = 0), Tx(content='c', timestamp=1326244367, bucket = 0), Tx(content='e', timestamp=1326244368, bucket = 0)], 
    5: [Tx(content='a', timestamp=1326244364, bucket = 0), Tx(content='c', timestamp=1326244365, bucket = 0), Tx(content='b', timestamp=1326244366, bucket = 0), Tx(content='d', timestamp=1326244367, bucket = 0), Tx(content='e', timestamp=1326244368, bucket = 0)]}

  G = compute_initial_set_of_edges(cheating_dict)
  # H = complete_list_of_edges(G)
  # finalize_output(H)
  # return


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