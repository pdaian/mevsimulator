from transactions import *

class TransactionSequence:
    def __init__(self, transactions):
        # linaerly sorted transactions involved in a sequence
        self.transactions = transactions

    def get_output(self):
        current_state = ETHState()
        for transaction in self.transactions:
            current_state = transaction.execute(current_state)
        return current_state


