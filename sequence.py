from transactions import *

class TransactionSequence:
    def __init__(self, transactions):
        # linaerly sorted transactions involved in a sequence
        self.transactions = transactions

    def get_output_with_tagged_metrics(self, metrics_tag):
        current_state = ETHState()
        for transaction in self.transactions:
            metric = transaction.execute(current_state)
            transaction.metrics[metrics_tag] = metric
        print("x: %d, y: %d" % (current_state.x, current_state.y))
        return current_state


