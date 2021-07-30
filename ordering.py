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
        assert (len(nodes_vs_transaction_times) != 0)
        tx_sorted_by_timestamp = self.sort_tx_by_timestamp(nodes_vs_transaction_times)
        tx_list = self.get_tx_list(nodes_vs_transaction_times)
        return self.tx_ordering(tx_sorted_by_timestamp, tx_list)

    def sort_tx_by_timestamp(self, nodes_vs_tx_times):
        for node in nodes_vs_tx_times:
            assert (len(nodes_vs_tx_times[node]) != 0)
            nodes_vs_tx_times[node].sort(key=lambda tx: tx.timestamp)

    def get_tx_list(self, nodes_vs_tx_times):
        for node in nodes_vs_tx_times:
            return [tx.content for tx in nodes_vs_tx_times[node]]

    def tx_ordering(self, tx_id_ordered_by_timestamp, node_list):
        first_tx = self.first_tx(tx_id_ordered_by_timestamp)
        node_list.pop(node_list.index(first_tx))
        tx_to_connect = first_tx
        tx_list = [first_tx]
        while node_list:
            added = False
            connections = self.get_most_popular_connection_to(tx_to_connect, tx_id_ordered_by_timestamp)
            for connection in connections:
                tx, _ = connection
                if tx not in tx_list:
                    tx_list.append(tx)
                    node_list.pop(node_list.index(first_tx))
                    tx_to_connect = tx
                    added = True
                    break
            if not added:
                tx_list.append(node_list[0])
                tx = node_list.pop(0)
                tx_to_connect = tx

        return first_tx.content

    def first_tx(self, tx_id_ordered_by_timestamp):
        first_tx_list = [tx_id_ordered_by_timestamp[tx][0].content for tx in tx_id_ordered_by_timestamp]
        return mode(first_tx_list)

    def get_upcoming_connection_to(self, from_tx, ordered_tx_lists):
        # what if all connections are to one at end and the one at the end doesn't have any other connections?
        tx_to_count_dict = {}
        tx_count = None
        for node in ordered_tx_lists:
            tx_list = ordered_tx_lists[node]
            if not tx_count:
                tx_count = len(tx_list)
            tx_index = tx_list.index(from_tx)
            if tx_index < tx_count - 1:
                next_elem = tx_list[tx_index + 1]
                if next_elem not in tx_to_count_dict:
                    tx_to_count_dict[next_elem] = 1
                else:
                    tx_to_count_dict[next_elem] += 1
        return tx_count.items().sort(key=lambda i, j: j, reverse=True)


class AequitasOrdering:
    def order(self, transaction_sequence):
        pass
