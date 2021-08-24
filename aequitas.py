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
        if hasattr(tx, 'timestamp'):
            quotient = int((tx.timestamp - starting_timestamp) // granularity)
            tx.bucket = quotient
    return tx_ordering


def get_all_tx_in_batch(tx_list: Dict[int, Tx]) -> Dict[int, Tx]:
    # TODO
    return

def get_empty_edges(H: nx.DiGraph) -> List:
    # used undirected edges for easier computing
    empty_edges = []
    edge_candidates = sorted(list(itertools.permutations(H.nodes, 2)), key=lambda x: (x[0], x[1]))
    unsorted_edges = H.edges
    sorted_edges = sorted(unsorted_edges, key=lambda x: (x[0], x[1]))
    value = list(set(edge_candidates) - set(sorted_edges))
    for x, y in value:
        if (y,x) in empty_edges:
            continue
        if (y,x) in value:
            empty_edges.append((x,y))
    print("empty_edges", empty_edges)
    return empty_edges

def GetMaxLengthValue(d):
    maks=max(d, key=lambda k: len(d[k]))
    return len(d[maks])

def compute_initial_set_of_edges(tx_dict: Dict, gamma, f: int) -> Tuple[nx.DiGraph, Dict]:
    """
    line 15-25

    Args:

    Returns:
      need not be complete. Graph need not be acyclic
    """    
    print("\n============== Aequitas: compute_initial_set_of_edges ==============")
    
    n = len(tx_dict)
    print("n = %s, gamma = %s, f = %s" % (n, gamma, f))
    if gamma <=1/2 or gamma >1:
        print("gamma = %s" % gamma)
        sys.exit("Order-Fairness Parameter Out of Bounds, Exit")

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
    longest_ordering = GetMaxLengthValue(tx_dict)
    print("longest_ordering: ", longest_ordering)
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
            if i in row:
                idx.append(row.index(i))
            else:
                idx.append(99999) # Hacky: if we can't find this tx, assume it has an extremely large index(i.e. arrive late eventually)
        indices[i] = np.array(idx)
    print("indices:")
    pp.pprint(indices)

    # Compute the differences between all pairs of txs, a negative value in this matrix means key[0] is in front of key[1]
    pairs_dict = {}
    for key in edge_candidates:
        lst = np.array(indices[key[0]] - indices[key[1]])
        # print("debugging: list before", lst)
        lst[lst < -9999] = 0            # Hacky
        lst[lst > 9999] = 0             # Hacky
        # print("debugging: list after", lst)
        pairs_dict[key] = lst
    print("pairs_dict:")
    pp.pprint(pairs_dict)

    # Count number of negative elements
    counting_dict_neg = {}
    counting_dict_pos = {}
    for key in pairs_dict:
        counting_dict_neg[key] = np.sum(np.array((pairs_dict[key])) < 0, axis=0)
        counting_dict_pos[key] = np.sum(np.array((pairs_dict[key])) > 0, axis=0)
    print("counting_dict_neg:")
    pp.pprint(counting_dict_neg)

    print("counting_dict_pos:")
    pp.pprint(counting_dict_pos)

    # Filter using gamma - the fairness parameter as the thereshold
    edge_dict = {}
    
    for i in counting_dict_neg:
        if counting_dict_neg[i] >= n * gamma - f:
            print("neg adding " , i)
            edge_dict[i] = counting_dict_neg[i]

    for j in counting_dict_pos:
        print("j", j)
        i = j[::-1]
        if counting_dict_pos[j] >= n * gamma - f:
            print("pos adding " , i)
            edge_dict[i] = counting_dict_pos[j]

    print("edge_dict: ")
    pp.pprint(edge_dict)

    # Add edges to the graph
    G = nx.DiGraph()
    for i in edge_dict:
        G.add_edge(str(i[0]), str(i[1]))
    print("G.graph: ", G.edges)

    no_edge_dict = get_empty_edges(G)

    return G, no_edge_dict
# returns a graph, and the empty edges

def get_list_of_descendants(H: nx.DiGraph, key) ->  List:
    lst = []
    if key in H.nodes:
        lst = list(H.successors(key))
    return lst

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
        descendants_0 = get_list_of_descendants(H, key[0])
        descendants_1 = get_list_of_descendants(H, key[1])
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
    """
    remove an edge (x,y) from the condensed DAG if they are 
    (1) in diferent SCC and 
    (2) no edge between them and
    (3) no common descendants
    """
    print("****** before pruning ****** : ", H.edges)
    empty_edges = get_empty_edges(H)
    if len(empty_edges) != 0:   # no edge between them and
         for x, y in empty_edges:
            print("pruning x, y: %s, %s " %(x,y))
            SCC = list(nx.strongly_connected_components(H))
            print("SCC:", SCC)
            SCC_idx_1 = [i for i, lst in enumerate(SCC) if x in lst]
            SCC_idx_2 = [i for i, lst in enumerate(SCC) if y in lst]
            print("SCC_idx_1:", SCC_idx_1)
            print("SCC_idx_2:", SCC_idx_2)
            SCC_intersection = (list(set(SCC_idx_1) & set(SCC_idx_2))) # The index of the SCC in which both x and y are part of
            if len(SCC_intersection) == 0 : # is empty, x, y is in different SCC
                common_descendants = (list(set(get_list_of_descendants(H, x)) & set(get_list_of_descendants(H, y))))
                print("common_descendants", common_descendants)
                if len(common_descendants) == 0 : # is empty, x, y has no common descendants
                    if(x in H.nodes): 
                        H.remove_node(x)
                        print("Pruned vertex %s successfully"% x)
                    if(y in H.nodes): 
                        H.remove_node(y)
                        print("Pruned vertex %s successfully"% y)


    print("****** after pruning ****** : ", H.edges)
    return H

def finalize_output(H: nx.DiGraph, no_edge_dict: Dict) -> List:
    """
    line 49-52:
    Compute the condensation graph of H(collapse the strongly connected components into a single vertex)
    Then topologically sort this graph and then output the sorting (Here, every index is a set of vertices)

    Returns: A list of final output ordering
    """
    print("\n============== Aequitas: finalize_output ==============")
    print("H.graph: ", H.edges)
    condensed_DAG = nx.condensation(H)
    SCC =nx.strongly_connected_components(H)
    mapping =  condensed_DAG.graph['mapping']
    print("SCC: ", SCC)
    print("mapping: ", mapping)
    print("condensed_DAG: ", condensed_DAG.edges)

    assert(nx.is_directed_acyclic_graph(condensed_DAG) is True)

    # for v in condensed_DAG.nodes:
    #     print(condensed_DAG.in_degree(v))

    removed_DAG = prune(condensed_DAG)
    # remove an edge (x,y) from the condensed DAG if they are 
    # (1) in diferent SCC and 
    # (2) no edge between them and
    # (3) no common descendants

    print("removed_DAG: ", removed_DAG.edges)
    int_output = list(nx.topological_sort(removed_DAG))
    print("int_output: ", int_output)
    node_output_ordered = [set() for _ in range(len(mapping.keys()))]
    node_output_topo = [set() for _ in range(len(int_output))]
    for k,v in mapping.items():
        node_output_ordered[v].add(k)
    
    for i, index in enumerate(int_output):
        node_output_topo[i] = node_output_ordered[index]
    return node_output_topo
# Final output ordering of Example 2: [a,b,c]

def prettyprint(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         prettyprint(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

# Calling aequitas once means processing this bucket/epoch/batch of Txs according to Aequitas ordering
def aequitas(tx_dict: Dict, gamma, f: int):


    # Setup
    for node in tx_dict:
        # ToDo: any granularization
        tx_dict[node] = [str(tx.content) for tx in tx_dict[node]]



    (G, no_edge_dict) = compute_initial_set_of_edges(tx_dict, gamma, f)
    H = complete_list_of_edges(G, no_edge_dict)
    Out = finalize_output(H, no_edge_dict)
    print("\n============== Aequitas: done ==============")
    return Out


def main():

    starting_timestamp = 1326244364
    granularity = 5

    # This is a sample input to the aequitas main algorithm, we assume this is already sorted upon being passed, i.e. an ordering
    tx_dict = {
                1: [Tx("a",1326244364), Tx("b",1326244365), Tx("c",1326244366), Tx("e",1326244367), Tx("d",1326244368), Tx("f",1326244369), Tx("g",1326244370)],
                2: [Tx("a",1326244364), Tx("c",1326244365), Tx("b",1326244366), Tx("d",1326244367), Tx("e",1326244368), Tx("f",1326244369), Tx("g",1326244375)],
                3: [Tx("b",1326244364), Tx("a",1326244365), Tx("c",1326244366), Tx("e",1326244367), Tx("d",1326244368), Tx("f",1326244376)],
                4: [Tx("a",1326244364), Tx("b",1326244365), Tx("d",1326244366), Tx("c",1326244367), Tx("e",1326244368)],
                5: [Tx("a",1326244364), Tx("c",1326244365), Tx("b",1326244366), Tx("d",1326244367), Tx("e",1326244368)]
                }
    
    # The function granularize figures txs into buckets/epochs/batches
    granularized_tx_dict = {}
    for i in tx_dict:
        granularized_tx_dict[i] = granularize(
            tx_dict.get(i), starting_timestamp, granularity
        )
    # print("granularized_tx_dict: ")
    # pp.pprint(granularized_tx_dict)

    # TODO: Some data processing and cleaning to get the following granularized_tx_dict

    granularized_tx_dict_expected = {
        1: [Tx(content ='a', timestamp = 1326244364, bucket = 0), Tx(content ='b', timestamp = 1326244365, bucket = 0), Tx(content ='c', timestamp = 1326244366, bucket = 0), Tx(content ='e', timestamp = 1326244367, bucket = 0), Tx(content ='d', timestamp = 1326244368, bucket = 0), Tx(content ='f', timestamp = 1326244369, bucket = 1), Tx(content ='g', timestamp = 1326244370, bucket = 1)],
        2: [Tx(content ='a', timestamp = 1326244364, bucket = 0), Tx(content ='c', timestamp = 1326244365, bucket = 0), Tx(content ='b', timestamp = 1326244366, bucket = 0), Tx(content ='d', timestamp = 1326244367, bucket = 0), Tx(content ='e', timestamp = 1326244368, bucket = 0), Tx(content ='f', timestamp = 1326244369, bucket = 1), Tx(content ='g', timestamp = 1326244375, bucket = 2)],
        3: [Tx(content ='b', timestamp = 1326244364, bucket = 0), Tx(content ='a', timestamp = 1326244365, bucket = 0), Tx(content ='c', timestamp = 1326244366, bucket = 0), Tx(content ='e', timestamp = 1326244367, bucket = 0), Tx(content ='d', timestamp = 1326244368, bucket = 0), Tx(content ='f', timestamp = 1326244376, bucket = 2)],
        4: [Tx(content ='a', timestamp = 1326244364, bucket = 0), Tx(content ='b', timestamp = 1326244365, bucket = 0), Tx(content ='d', timestamp = 1326244366, bucket = 0), Tx(content ='c', timestamp = 1326244367, bucket = 0), Tx(content ='e', timestamp = 1326244368, bucket = 0)],
        5: [Tx(content ='a', timestamp = 1326244364, bucket = 0), Tx(content ='c', timestamp = 1326244365, bucket = 0), Tx(content ='b', timestamp = 1326244366, bucket = 0), Tx(content ='d', timestamp = 1326244367, bucket = 0), Tx(content ='e', timestamp = 1326244368, bucket = 0)]
        }

    # TODO: Some data processing and cleaning to get the following simplified tx_dict for the 0th bucket/epoch/batch to be processed

    # example_1 = {
    #     1: ["a", "b", "c", "d", "e"],
    #     2: ["a", "b", "c", "e", "d"],
    #     3: ["a", "b", "c", "d", "e"],
    # }
    # result_1 = aequitas(example_1, 1, 1)
    # print("Example 1: ", result_1)

    # example_2 = {
    #     1: ["a", "b", "c", "e", "d"],
    #     2: ["a", "c", "b", "d", "e"],
    #     3: ["b", "a", "c", "e", "d"],
    #     4: ["a", "b", "d", "c", "e"],
    #     5: ["a", "c", "b", "d", "e"],
    # }
    # result_2 = aequitas(example_2, 1, 1)
    # print("Example 2: ", result_2)

    # example_2_prime = {
    #     1: ["a", "b", "c", "e", "d"],
    #     2: ["a", "c", "b", "d", "e"],
    #     3: ["b", "a", "c", "e", "d"],
    #     4: ["a", "b", "d", "c", "e"],
    #     5: ["a", "c", "b", "d", "e"],
    # }
    # result_2_prime = aequitas(example_2_prime, 0.8, 1)
    # print("Example 2_prime: ", result_2_prime)

    # The following test case contains cycles(Strongly-Connected-Components)
    # and the expected output is {'a', 'e', 'c', 'b'} -> {'d'}
    # which means the Aequitas treats {'a', 'e', 'c', 'b'} as being of the same order, and this set is ordered in front of 'd'
    #     1: ["b", "c", "e", "a", "d"],
    #     2: ["b", "c", "e", "a", "d"],
    #     3: ["a", "c", "b", "d", "e"],
    #     4: ["a", "c", "b", "d", "e"],
    #     5: ["e", "a", "b", "c", "d"],
    example_3 = {
        1: [
        Tx(content ='b', timestamp = 1326244364, bucket = 0), 
        Tx(content ='c', timestamp = 1326244365, bucket = 0), 
        Tx(content ='e', timestamp = 1326244366, bucket = 0), 
        Tx(content ='a', timestamp = 1326244367, bucket = 0), 
        Tx(content ='d', timestamp = 1326244368, bucket = 0)
        ],
        2: [
        Tx(content ='b', timestamp = 1326244364, bucket = 0), 
        Tx(content ='c', timestamp = 1326244365, bucket = 0), 
        Tx(content ='e', timestamp = 1326244366, bucket = 0), 
        Tx(content ='a', timestamp = 1326244367, bucket = 0), 
        Tx(content ='d', timestamp = 1326244368, bucket = 0)
        ],
        3: [
        Tx(content ='a', timestamp = 1326244364, bucket = 0), 
        Tx(content ='c', timestamp = 1326244365, bucket = 0), 
        Tx(content ='b', timestamp = 1326244366, bucket = 0), 
        Tx(content ='d', timestamp = 1326244367, bucket = 0), 
        Tx(content ='e', timestamp = 1326244368, bucket = 0)
        ],
        4: [
        Tx(content ='a', timestamp = 1326244364, bucket = 0), 
        Tx(content ='c', timestamp = 1326244365, bucket = 0), 
        Tx(content ='b', timestamp = 1326244366, bucket = 0), 
        Tx(content ='d', timestamp = 1326244367, bucket = 0), 
        Tx(content ='e', timestamp = 1326244368, bucket = 0)
        ],
        5: [
        Tx(content ='e', timestamp = 1326244364, bucket = 0), 
        Tx(content ='a', timestamp = 1326244365, bucket = 0), 
        Tx(content ='b', timestamp = 1326244366, bucket = 0), 
        Tx(content ='c', timestamp = 1326244367, bucket = 0), 
        Tx(content ='d', timestamp = 1326244368, bucket = 0)
        ],
    }
    result_3 = aequitas(example_3, 0.8, 1)
    print("Example 3: ", result_3)


    # # The following test case SHOULD FAIL, due to corruption bound checks
    # example_4 = {
    #     1: ["a", "b", "c", "d", "e"],
    #     2: ["a", "b", "c", "e", "d"],
    #     3: ["a", "b", "c", "d", "e"],
    # }
    # result_4 = aequitas(example_4, 0.8, 1)
    # print("Example 4: ", result_4)

    # # The following test case SHOULD FAIL, due to missing d
    # example_5 = {
    #     1: ["a", "b", "c", "e", "d"],
    #     2: ["a", "b", "c", "e", "e"],
    #     3: ["a", "b", "c", "e", "e"],
    # }
    # result_5 = aequitas(example_5, 1, 1)
    # print("Example 5: ", result_5)
    
    # # The following test case SHOULD FAIL, due to corruption bound checks (Float error)
    # example_6 = {
    #     1: ["a", "b", "c", "e", "d"],
    #     2: ["a", "b", "c", "d", "e"],
    #     3: ["a", "b", "c", "d", "e"],
    #     4: ["a", "b", "c", "d", "e"],
    #     5: ["a", "b", "c", "d", "e"],
    # }
    # result_6 = aequitas(example_6, 0.5, 1)
    # print("Example 6: ", result_6)
    
    # # The following test case SHOULD FAIL, due to corruption bound checks ("a" node not present)  
    # example_7 = {
    #     1: ["a", "b", "c", "e", "d"],
    #     2: ["a", "b", "c", "d", "e"],
    #     3: ["a", "b", "c", "d", "e"],
    #     4: ["a", "b", "c", "d", "e"],
    #     5: ["a", "b", "c", "d", "e"],
    # }
    # result_7 = aequitas(example_7, 2.0, 1)
    # print("Example 7: ", result_7)
    
    # example_8 = {
    #     1: ["a", "b", "c", "e", "d"],
    #     2: ["a", "b", "c", "d", "e"],
    #     3: ["a", "b", "c", "d", "e"],
    #     4: ["a", "b", "c", "d", "e"],
    #     5: ["a", "b", "c", "d", "e"],
    # }
    # result_8 = aequitas(example_8, 0.0, 1)
    # print("Example 8: ", result_8)

if __name__ == "__main__":
    main()