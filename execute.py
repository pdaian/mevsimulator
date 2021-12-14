from transactions import *
from sequence import *
from util import *
import numpy as np
import matplotlib.pyplot as plt
from ordering import *
from aequitas import *
import copy
import json
from web3 import Web3

tx_mapping = {}

def get_percent_difference(current, previous):
    if current == previous:
        return 0.0
    try:
        diff = (abs(current - previous) / previous) * 100.0
        if diff > 100.0:
            return 100.0
        return diff
    except ZeroDivisionError:
        return 100

def get_sequence_difference(txs, tag1, tag2):
    differences = []
    for tx in txs:
       if len(tx.metrics) > 0 and tag1 in tx.metrics and tag2 in tx.metrics:
            print(tx.metrics)
            diff = get_percent_difference(tx.metrics[tag1], tx.metrics[tag2])
            if diff != -1:
                differences.append(diff)
    return differences

def LimitedRandDoubles(lim):
    return np.random.uniform(low=0,high=lim,size=(1, 1000000))


rand_timing_doubles = LimitedRandDoubles(30)
rand_network_doubles = LimitedRandDoubles(10)
last_timing_double = 0
last_network_double = 0

def get_timestep():
    global last_timing_double, rand_timing_doubles
    last_timing_double += 1
    return rand_timing_doubles[0][last_timing_double]

def get_network_delay():
    global last_network_double
    last_network_double += 1
    return rand_network_doubles[0][last_network_double]

def same_order(txs):
    return txs

def process_example_uniswap_transactions(data_file, order_function):
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/af1d3ad9016c423282f5875d6e2dc6a7"))

    # Very messy parser of transactions in plaintext into objects
    transactions = []
    num_tx = 200
    curr_num = 0
    nodes_seen = {}
    for transaction in open(data_file).read().splitlines()[0:]:
        transaction = transaction.split()
        tx = None
        if curr_num >= num_tx:
            break
        if '//' in transaction:
            # comment
            next_tx_id = transaction[2]
            next_tx_block = transaction[4]
            continue
        elif 'swaps' in transaction:
            tokens = sorted([[int(transaction[7]), int(transaction[6])], [int(transaction[10]), int(transaction[9])]])
            fee = 0
            if len(transaction) == 17:
                fee = int(transaction[15])
            tx = SwapTransaction(tokens[0][0], tokens[1][0], tokens[0][1], tokens[1][1], int(transaction[0]), fee, next_tx_id, next_tx_block)
        elif 'liquidity;' in transaction:
            print("first_token, second_token, first_amount, second_amount, sender, fee")
            print(transaction)
            for i in range(len(transaction)):
                print(i, transaction[i])
            tokens = sorted([[int(transaction[3]), int(transaction[2])], [int(transaction[6]), int(transaction[5])]])
            fee = 0
            #if len(transaction) == 17:
            #    fee = int(transaction[15])
            if 'adds' in transaction:
                tx = AddLiquidityTransaction(tokens[0][0], tokens[1][0], tokens[0][1], tokens[1][1], int(transaction[0]), fee, next_tx_id, next_tx_block)
            elif 'removes' in transaction:
                tx = RemoveLiquidityTransaction(tokens[0][0], tokens[1][0], tokens[0][1], tokens[1][1], int(transaction[0]), fee, next_tx_id, next_tx_block)
        if tx is not None:
            transactions.append(tx)
            curr_num += 1

    assert(len(transactions) >= num_tx)
    # transactions = transactions[:100]

    # simulate timing data
    curr_time = 0.0
    for tx in transactions:
        tx.time_sent = curr_time
        curr_time += get_timestep()
        # simulate network data
        for node in range(0, 5):
            if not node in nodes_seen:
                nodes_seen[node] = []
            nodes_seen[node].append((tx, tx.time_sent + get_network_delay()))
    for node in range(0, 5):
        nodes_seen[node] = sorted(nodes_seen[node], key = lambda x : x[1])
    print(nodes_seen[0])

    transactions = order_function(transactions)
    print("Transactions", transactions)
    baseline_sequence = TransactionSequence(transactions)
    baseline_sequence = baseline_sequence.get_output_with_tagged_metrics("baseline")

    for node in nodes_seen:
        node_order_sequence = TransactionSequence([x[0] for x in nodes_seen[node]])
        node_order = node_order_sequence.get_output_with_tagged_metrics(node)


    differences = {}

    for node in nodes_seen:
        differences[node] = get_sequence_difference(transactions, "baseline", node)
    plt.hist(differences.values(), alpha=0.5, bins=20)
    plt.yscale('log')
    plt.show()


    max_differences = {}
    curr_max_diff = 0
    for i in range(1):
        # Leader maliciously shuffling
        for node in nodes_seen:
            seq = []
            for x in nodes_seen[node]:
                # get txn data
                txn_data = json.loads(Web3.toJSON(w3.eth.get_transaction(x[0].txid)))
                # append to seq as a tuple, first element is the txn and second is the nonce
                seq.append((x[0], txn_data["nonce"]))
            # sort by non-decreasing nonce
            seq.sort(key=lambda s: s[1])
            # remove the nonce so seq is just a list of txn with non-decreasing nonce
            seq = [x[0] for x in seq]
            node_order_sequence = TransactionSequence(seq)
            node_order = node_order_sequence.get_output_with_tagged_metrics(node)

        differences = {}

        for node in nodes_seen:
            differences[node] = get_sequence_difference(transactions, "baseline", node)
        max_diff = sum([sum(val > 95 for val in differences[node]) for node in nodes_seen])
        
        if max_diff >= curr_max_diff:
            max_differences = differences
            curr_max_diff = max_diff

   
    plt.hist(max_differences.values(), alpha=0.5, bins=20)
    plt.yscale('log')
    plt.show()

    print(nodes_seen[0])

    # set up input for causal order (same as aequitas)
    for node in nodes_seen:
        nodes_seen[node] = [Tx(x[0], x[1]) for x in nodes_seen[node]]

    # TODO: Need to fix this part given new tx format
    # causal_order = CausalOrdering()
    # causal_order = causal_order.order(copy.deepcopy(nodes_seen))
    # #print(causal_order)
    # output = TransactionSequence(causal_order).get_output_with_tagged_metrics('causal')
    # difference_causal = get_sequence_difference(transactions, "baseline", "causal")

    # plt.hist(difference_causal, alpha=0.5, bins=20)
    # plt.yscale('log')
    # plt.show()

    for tx in transactions:
        tx_mapping[str(tx)] = tx

    print(nodes_seen[0])
    aequitas_order = aequitas(copy.deepcopy(nodes_seen), 1, 1)
    final_order = []
    for output_set in aequitas_order:
        y = [tx_mapping[x] for x in output_set]
        final_order += y
    print(final_order)

    output = TransactionSequence(final_order).get_output_with_tagged_metrics('aequitas')
    difference_aequitas = get_sequence_difference(transactions, "baseline", "aequitas")

    plt.hist(difference_aequitas, alpha=0.5, bins=20)
    plt.yscale('log')
    plt.title("Aequitas")
    plt.show()

if __name__ == '__main__':
    process_example_uniswap_transactions('data/0x05f04f112a286c4c551897fb19ed2300272656c8.csv', same_order)
