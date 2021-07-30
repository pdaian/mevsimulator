from statistics import mode

class Tx:
    def __init__(self, content, timestamp, bucket=None):
        self.content = content
        self.timestamp = timestamp  # Unix timestamp
        self.bucket = bucket

    def __str__(self):
        return "Transaction: {0} , {1}".format(self.content, self.timestamp)

    def __repr__(self):
        return "Tx(content ='{0}', timestamp = {1}, bucket = {2})".format(self.content, self.timestamp, self.bucket)


class CausalOrdering:
    def order(self, nodes_vs_transaction_times):
        assert(len(nodes_vs_transaction_times) != 0)
        tx_sorted_by_timestamp = self.sort_tx_by_timestamp(nodes_vs_transaction_times)
        tx_list = self.get_tx_list(nodes_vs_transaction_times)
        return self.tx_ordering(tx_sorted_by_timestamp, tx_list)

    def sort_tx_by_timestamp(self, nodes_vs_tx_times):
        for node in nodes_vs_tx_times:
            assert(len(nodes_vs_tx_times[node]) != 0)
            nodes_vs_tx_times[node].sort(key=lambda tx: tx.timestamp)

    def get_tx_list(self, nodes_vs_tx_times):
        for node in nodes_vs_tx_times:
            return [tx.content for tx in nodes_vs_tx_times[node]]

    def tx_ordering(self, tx_id_ordered_by_timestamp, node_list):
        first_tx = self.first_tx(tx_id_ordered_by_timestamp)
        return first_tx.content

    def first_tx(self, tx_id_ordered_by_timestamp):
        first_tx_list = [tx_id_ordered_by_timestamp[tx][0].content for tx in tx_id_ordered_by_timestamp]
        return mode(first_tx_list)

class AequitasOrdering:
    def order(self, transaction_sequence):
        pass
