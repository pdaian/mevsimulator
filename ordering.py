import statistics


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
    def order(self, nodes_vs_tx_received):
        assert (len(nodes_vs_tx_received) != 0)
        self.sort_tx_by_timestamp(nodes_vs_tx_received)
        self.extract_content(nodes_vs_tx_received)
        tx_list = self.get_unique_tx_list(nodes_vs_tx_received)
        return self.tx_ordering(nodes_vs_tx_received, tx_list)

    def sort_tx_by_timestamp(self, nodes_vs_tx_received):
        for node in nodes_vs_tx_received:
            assert (len(nodes_vs_tx_received[node]) != 0)
            nodes_vs_tx_received[node].sort(key=lambda tx: tx.timestamp)

    def extract_content(self, nodes_vs_tx_received):
        for node in nodes_vs_tx_received:
            nodes_vs_tx_received[node] = [tx.content for tx in nodes_vs_tx_received[node]]  # rename nodes_vs_tx_times

    def get_unique_tx_list(self, nodes_vs_tx_received):
        nodes_set = set()
        for node in nodes_vs_tx_received:
            for tx in nodes_vs_tx_received[node]:
                nodes_set.add(tx)
        return list(nodes_set)

    def tx_ordering(self, tx_id_ordered_by_timestamp, node_list):
        first_tx = self.first_tx(tx_id_ordered_by_timestamp)
        node_list.pop(node_list.index(first_tx))
        tx_to_connect = first_tx
        tx_list = [first_tx]
        while node_list:
            added = False
            connections = self.get_upcoming_connection_to(tx_to_connect, tx_id_ordered_by_timestamp)
            for connection in connections:
                tx, _ = connection
                if tx not in tx_list:
                    tx_list.append(tx)
                    node_list.remove(tx)
                    tx_to_connect = tx
                    added = True
                    break
            if not added:
                tx_list.append(node_list[0])
                tx = node_list.pop(0)
                tx_to_connect = tx
        return tx_list

    def first_tx(self, tx_id_ordered_by_timestamp):
        first_tx_list = [tx_id_ordered_by_timestamp[tx][0] for tx in tx_id_ordered_by_timestamp]
        return statistics.mode(first_tx_list)

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
        return sorted(list(tx_to_count_dict.items()), key=lambda i: i[1], reverse=True)


class AequitasOrdering:
    def order(self, transaction_sequence):
        pass
