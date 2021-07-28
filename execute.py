from transactions import *
from sequence import *
from util import *

def same_order(txs):
    return txs

def process_example_uniswap_transactions(data_file, order_function):


    # Very messy parser of transactions in plaintext into objects
    transactions = []
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

            # TODO simulate timing data
            # TODO simulate network data
    transactions = order_function(transactions)
    print("Transactions", transactions)
    sequence = TransactionSequence(transactions)
    return sequence.get_output()

if __name__ == '__main__':
    process_example_uniswap_transactions('data/0x05f04f112a286c4c551897fb19ed2300272656c8.csv', same_order)
