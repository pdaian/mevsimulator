from transactions import *
from sequence import *
from util import *
import numpy as np
import matplotlib.pyplot as plt
from ordering import *

def get_change(current, previous):
    if current == previous:
        return 0.0
    try:
        diff = (abs(current - previous) / previous) * 100.0
        if diff > 10.0:
            return 10.0
        return diff
    except ZeroDivisionError:
        return 0.0

def LimitedRandDoubles(lim):
    return np.random.uniform(low=0,high=lim,size=(1, 1000000))


rand_timing_doubles = LimitedRandDoubles(5.0)
rand_network_doubles = LimitedRandDoubles(10.0)
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


    # Very messy parser of transactions in plaintext into objects
    transactions = []
    nodes_seen = {}
    for transaction in open(data_file).read().splitlines():
        transaction = transaction.split()
        tx = None
        if '//' in transaction:
            # comment
            continue
        elif 'swaps' in transaction:
            tokens = sorted([[int(transaction[7]), int(transaction[6])], [int(transaction[10]), int(transaction[9])]])
            fee = 0
            if len(transaction) == 17:
                fee = int(transaction[15])
            tx = SwapTransaction(tokens[0][0], tokens[1][0], tokens[0][1], tokens[1][1], int(transaction[0]), fee)
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
                tx = AddLiquidityTransaction(tokens[0][0], tokens[1][0], tokens[0][1], tokens[1][1], int(transaction[0]), fee)
            elif 'removes' in transaction:
                tx = RemoveLiquidityTransaction(tokens[0][0], tokens[1][0], tokens[0][1], tokens[1][1], int(transaction[0]), fee)
        if tx is not None:
            transactions.append(tx)


    transactions = transactions[:100]

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
    print(nodes_seen)

    transactions = order_function(transactions)
    print("Transactions", transactions)
    baseline_sequence = TransactionSequence(transactions)
    baseline_sequence = baseline_sequence.get_output_with_tagged_metrics("baseline")
    for node in nodes_seen:
        node_order_sequence = TransactionSequence([x[0] for x in nodes_seen[node]])
        node_order = node_order_sequence.get_output_with_tagged_metrics(node)


    differences = {}
    for tx in transactions:
        if len(tx.metrics) > 0:
            for node in nodes_seen:
                if not node in differences:
                    differences[node] = []
                differences[node].append(get_change(tx.metrics['baseline'], tx.metrics[node]))
    #plt.hist(differences.values(), alpha=0.5, bins=20)
    #plt.yscale('log')
    #plt.show()

    # set up input for causal order (same as aequitas)
    for node in nodes_seen:
        nodes_seen[node] = [Tx(x[0], x[1]) for x in nodes_seen[node]]
    causal_order = CausalOrdering()
    order = causal_order.order(nodes_seen)
    print(order)
    output = TransactionSequence(order).get_output_with_tagged_metrics('causal')


if __name__ == '__main__':
    process_example_uniswap_transactions('data/0x05f04f112a286c4c551897fb19ed2300272656c8.csv', same_order)
