from transactions import *
from sequence import *

def process_example_uniswap_transactions(data_file):
    for transaction in open(data_file).read().splitlines():
        if '//' in transaction:
            # comment
            continue
        elif 'swaps' in transaction:
            transaction = transaction.split()
            print(transaction)
            for i in range(len(transaction)):
                print(i, transaction[i])
            exit(1)

if __name__ == '__main__':
    process_example_uniswap_transactions('data/0x05f04f112a286c4c551897fb19ed2300272656c8.csv')
