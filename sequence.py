from transactions import *

class TransactionSequence:
    def __init__(self, transactions):
        # linaerly sorted transactions involved in a sequence
        self.transactions = transactions

    def get_output(self):
        current_state = ETHState()
        for transaction in self.transactions:
            transaction.execute(current_state)
        print("x: %d, y: %d" % (current_state.x, current_state.y))
        return current_state


