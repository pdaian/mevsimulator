import networkx as nx
import random
import itertools
import numpy as np
import pprint as pp
import sys
from typing import Dict, List, Tuple

# number of nodes n
# number of byzantine / malicious nodes f
# gamma : order fairness parameter
# g : granularity



class Tx:
    def __init__(self, content, timestamp, bucket=None):
        self.content = content
        self.timestamp = timestamp  # Unix timestamp
        self.bucket = bucket

    def __str__(self):
        return f"Transaction: {self.content} , {self.timestamp}"

    def __repr__(self):
        return f"Tx(content ='{self.content}', timestamp = {self.timestamp}, bucket = {self.bucket})"



def granularize(tx_ordering, starting_timestamp: int, granularity: int) -> List[Tx]:
    """Puts txs into buckets
    line 10-12
    All transactions with timestamps [0,g-1] are in the same bucket, [g, 2g-1] are in the same bucket etc.
    """
    for tx in tx_ordering:
        quotient = int((tx.timestamp - starting_timestamp) // granularity)
        tx.bucket = quotient
    return tx_ordering


def get_all_tx_in_batch(tx_list: Dict[int, Tx]) -> Dict[int, Tx]:
    # TODO
    return


def compute_initial_set_of_edges(tx_dict: Dict, gamma: int, f: int) -> Tuple[nx.DiGraph, Dict]:
    """
    line 15-25

    Args:

    Returns:
      need not be complete. Graph need not be acyclic
    """    
    print("\n============== Aequitas: compute_initial_set_of_edges ==============")
    
    n = len(tx_dict)
    print("n = %s, gamma = %s, f = %s" % (n, gamma, f))
    if not (n > 2 * f/(2 * gamma - 1)):
        print("2 * f/(2 * gamma - 1) = %s" %(2 * f/(2 * gamma - 1)))
        sys.exit("Corruption Bound Check Failed, Exit")

    nodes = set()
    for key in tx_dict:
        for tx in tx_dict[key]:
            if tx not in nodes:
                nodes.add(tx)
    nodes = sorted(nodes)
    print("nodes:", nodes)
    m = len(nodes)

    tx_list = list(tx_dict.values())

    edge_candidates = list(itertools.combinations(nodes, 2))
    edge_candidates = sorted(edge_candidates, key=lambda x: (x[0], x[1]))
    assert len(edge_candidates) == ((m ** 2 - m) / 2)  # O(n^2) combinations
    print("edge_candidates: ", edge_candidates)

    # Get the indices of each tx in every nodes's vote
    indices = {}
    for i in nodes:
        idx = []
        for row in tx_list:
            idx.append(row.index(i))
        indices[i] = np.array(idx)
    print("indices:")
    pp.pprint(indices)

    # Compute the differences between all pairs of txs, a negative value in this matrix means key[0] is in front of key[1]
    pairs_dict = {}
    for key in edge_candidates:
        pairs_dict[key] = indices[key[0]] - indices[key[1]]
    print("pairs_dict:")
    pp.pprint(pairs_dict)

    # Count number of negative elements
    counting_dict = {}
    for key in pairs_dict:
        counting_dict[key] = np.sum(np.array((pairs_dict[key])) < 0, axis=0)
    print("counting_dict:")
    pp.pprint(counting_dict)

    # Filter using gamma - the fairness parameter as the thereshold
    edge_dict = {}
    no_edge_dict = {}
    
    for i in counting_dict:
        if counting_dict[i] >= n * gamma - f:
            edge_dict[i] = counting_dict[i]
        else:
            no_edge_dict[i] = counting_dict[i]
    print("no_edge_dict:")
    pp.pprint(no_edge_dict)
    print("edge_dict: ")
    pp.pprint(edge_dict)
    assert len(edge_dict) + len(no_edge_dict) == (m ** 2 - m) / 2

    # Add edges to the graph
    G = nx.DiGraph()
    for i in edge_dict:
        G.add_edge(str(i[0]), str(i[1]))
    print("G.graph: ", G.edges)
    return G, no_edge_dict
# returns a graph, and the empty edges

def complete_list_of_edges(H: nx.DiGraph, no_edge_dict: Dict) -> nx.DiGraph:
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
    print("\n============== Aequitas: complete_list_of_edges ==============")
    descendants_0 = iter([])
    descendants_1 = iter([])
    if len(no_edge_dict) == 0:
        n = len(H.nodes)
        assert(len(H.edges) == (n ** 2 - n) / 2)
        print("The graph is already fully connected")
    for key in no_edge_dict:
        assert H.has_edge(key[0], key[1]) is False
        print(
            "(%s, %s) does NOT have an edge, looking at common descendants: "
            % (key[0], key[1])
        )
        # TODO: If they are in the same SCC, pass
        descendants_0 = list(H.successors(key[0]))
        descendants_1 = list(H.successors(key[1]))
        print("%s's descendants: " % key[0], descendants_0)
        print("%s's descendants: " % key[1], descendants_1)
        if len(list(set(descendants_0) & set(descendants_1))) == 0:
            has_common_descendants = False
            print(
                "node %s and node %s have no common descendant, not enough info \n"
                % (key[0], key[1])
            )
        else:
            has_common_descendants = True
            if len(descendants_0) >= len(descendants_1):
                H.add_edge(key[0], key[1])
                print(
                    "node %s has more or equal descendants than %s, adding edge  %s -> %s \n"
                    % (key[0], key[1], key[0], key[1])
                )
            else:
                H.add_edge(key[1], key[0])
                print(
                    "node %s has more descendants than %s, adding edge  %s -> %s \n"
                    % (key[1], key[0], key[1], key[0])
                )
    n = len(H.nodes)
    # assert (len(H.edges)==(n**2-n)/2), "H is NOT a fully connected graph"
    return H

# TODO: e.g. in Example 2: remove d(0) and (1)
def prune(H: nx.DiGraph):
    return H

def finalize_output(H) -> List:
    """
    line 49-52:
    Compute the condensation graph of H(collapse the strongly connected components into a single vertex)
    Then topologically sort this graph and then output the sorting (Here, every index is a set of vertices)

    Returns: A list of final output ordering
    """
    print("\n============== Aequitas: finalize_output ==============")
    print("H.graph: ", H.edges)
    condensed_DAG = nx.condensation(H)
    d =  condensed_DAG.graph['mapping']
    print("mapping: ", d)
    print("condensed_DAG: ", condensed_DAG.edges)

    assert(nx.is_directed_acyclic_graph(condensed_DAG) is True)

    removed_DAG = prune(condensed_DAG)
    int_output = list(nx.topological_sort(removed_DAG))
    print("int_output: ", int_output)
    node_output = [None]*len(int_output)
    for k,v in d.items():
      if v in int_output:
        node_output[int_output.index(v)]=k
    print("node_output: ", node_output)
    return node_output
# Final output ordering of Example 2: [a,b,c]

def prettyprint(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         prettyprint(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

# Calling aequitas once means processing this bucket/epoch/batch of Txs according to Aequitas ordering
def aequitas(tx_dict: Dict, gamma: int, f: int):
    (G, no_edge_dict) = compute_initial_set_of_edges(tx_dict, gamma, f)
    H = complete_list_of_edges(G, no_edge_dict)
    Out = finalize_output(H)
    print("\n============== Aequitas: done ==============")
    return Out


def main():
    # Example 2
    # Node 1: [a,b,c,e,d]
    # Node 2: [a,c,b,d,e]
    # Node 3: [b,a,c,e,d]
    # Node 4: [a,b,d,c,e]
    # Node 5: [a,c,b,d,e]

    starting_timestamp = 1326244364
    granularity = 5

    # This is a sample input to the aequitas main algorithm, we assume this is already sorted upon being passed, i.e. an ordering
    tx_dict = {
                1: [Tx("a",1326244364), Tx("b",1326244365), Tx("c",1326244366), Tx("e",1326244367), Tx("d",1326244368), Tx("f",1326244369), Tx("g",1326244370)],
                2: [Tx("a",1326244364), Tx("c",1326244365), Tx("b",1326244366), Tx("d",1326244367), Tx("e",1326244368), Tx("f",1326244369), Tx("g",1326244375)],
                3: [Tx("b",1326244364), Tx("a",1326244365), Tx("c",1326244366), Tx("e",1326244367), Tx("d",1326244368), Tx("f",1326244376)],
                4: [Tx("a",1326244364), Tx("b",1326244365), Tx("d",1326244366), Tx("c",1326244367), Tx("e",1326244368)],
                5: [Tx("a",1326244364), Tx("c",1326244365), Tx("b",1326244366), Tx("d",1326244367), Tx("e",1326244368)]}
    
    # The function granularize figures txs into buckets/epochs/batches
    granularized_tx_dict = {}
    for i in tx_dict:
        granularized_tx_dict[i] = granularize(
            tx_dict.get(i), starting_timestamp, granularity
        )
    print("granularized_tx_dict: ")
    pp.pprint(granularized_tx_dict)

    # TODO: Some data processing and cleaning to get the following granularized_tx_dict

    granularized_tx_dict_expected = {
        1: [Tx(content ='a', timestamp = 1326244364, bucket = 0), Tx(content ='b', timestamp = 1326244365, bucket = 0), Tx(content ='c', timestamp = 1326244366, bucket = 0), Tx(content ='e', timestamp = 1326244367, bucket = 0), Tx(content ='d', timestamp = 1326244368, bucket = 0), Tx(content ='f', timestamp = 1326244369, bucket = 1), Tx(content ='g', timestamp = 1326244370, bucket = 1)],
        2: [Tx(content ='a', timestamp = 1326244364, bucket = 0), Tx(content ='c', timestamp = 1326244365, bucket = 0), Tx(content ='b', timestamp = 1326244366, bucket = 0), Tx(content ='d', timestamp = 1326244367, bucket = 0), Tx(content ='e', timestamp = 1326244368, bucket = 0), Tx(content ='f', timestamp = 1326244369, bucket = 1), Tx(content ='g', timestamp = 1326244375, bucket = 2)],
        3: [Tx(content ='b', timestamp = 1326244364, bucket = 0), Tx(content ='a', timestamp = 1326244365, bucket = 0), Tx(content ='c', timestamp = 1326244366, bucket = 0), Tx(content ='e', timestamp = 1326244367, bucket = 0), Tx(content ='d', timestamp = 1326244368, bucket = 0), Tx(content ='f', timestamp = 1326244376, bucket = 2)],
        4: [Tx(content ='a', timestamp = 1326244364, bucket = 0), Tx(content ='b', timestamp = 1326244365, bucket = 0), Tx(content ='d', timestamp = 1326244366, bucket = 0), Tx(content ='c', timestamp = 1326244367, bucket = 0), Tx(content ='e', timestamp = 1326244368, bucket = 0)],
        5: [Tx(content ='a', timestamp = 1326244364, bucket = 0), Tx(content ='c', timestamp = 1326244365, bucket = 0), Tx(content ='b', timestamp = 1326244366, bucket = 0), Tx(content ='d', timestamp = 1326244367, bucket = 0), Tx(content ='e', timestamp = 1326244368, bucket = 0)]}

    # TODO: Some data processing and cleaning to get the following simplified tx_dict for the 0th bucket/epoch/batch to be processed

    example_2 = {
        1: ["a", "b", "c", "e", "d"],
        2: ["a", "c", "b", "d", "e"],
        3: ["b", "a", "c", "e", "d"],
        4: ["a", "b", "d", "c", "e"],
        5: ["a", "c", "b", "d", "e"],
    }
    result_2 = aequitas(example_2, 1, 1)
    print("Example 2: ", result_2)

    example_2_prime = {
        1: ["a", "b", "c", "e", "d"],
        2: ["a", "c", "b", "d", "e"],
        3: ["b", "a", "c", "e", "d"],
        4: ["a", "b", "d", "c", "e"],
        5: ["a", "c", "b", "d", "e"],
    }
    result_2_prime = aequitas(example_2_prime, 0.8, 1)
    print("Example 2_prime: ", result_2_prime)

    example_3 = {
        1: ["b", "c", "e", "a", "d"],
        2: ["b", "c", "e", "a", "d"],
        3: ["a", "c", "b", "d", "e"],
        4: ["a", "c", "b", "d", "e"],
        5: ["e", "a", "b", "c", "d"],
    }
    result_3 = aequitas(example_3, 0.8, 1)
    print("Example 3: ", result_3)

    example_1 = {
        1: ["a", "b", "c", "d", "e"],
        2: ["a", "b", "c", "e", "d"],
        3: ["a", "b", "c", "d", "e"],
    }
    result_1 = aequitas(example_1, 1, 1)
    print("Example 1: ", result_1)

    # The following test case SHOULD FAIL, due to corruption bound checks
    example_4 = {
        1: ["a", "b", "c", "d", "e"],
        2: ["a", "b", "c", "e", "d"],
        3: ["a", "b", "c", "d", "e"],
    }
    result_4 = aequitas(example_4, 0.8, 1)
    print("Example 4: ", result_4)


if __name__ == "__main__":
    main()


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

# // b and c dont have an edge but they have a common descendant: e
# // Lets say, we add (b,c) as the edge deterministically
# // d and e dont have an edge but they dont have a common descendant either, i.e. they wont be output yet
# TODO How is d, e output?
# Final output ordering: :a->b->c

# // Example 3: have cycles, look at condensation graph
# Node 1: [b,c,e,a,d]
# Node 2: [b,c,e,a,d]
# Node 3: [a,c,b,d,e]
# Node 4: [a,c,b,d,e]
# Node 5: [e,a,b,c,d]

# gamma = 3/5 (to add an edge, you need x<y in 3 nodes)

# (a->b), (a->c), (a->d),
#         (b->c), (b->d), (b->e)
#                 (c->d), (c->e)
#                                (e->a)

# // The graph contains two cycles: a,b,e and a,c,e
# // [a,b,c,e] is the strongly connected component(SCC), they are assumed to be output at the same time
# // we leave the specification up to the implementation (because we don’t consider unfairness within such an SCC)
# Final output ordering:  [a,b,c,e] -> d


