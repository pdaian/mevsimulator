import unittest
from ordering import Tx, CausalOrdering


class CausalOrderingTests(unittest.TestCase):
    def __init__(self):
        self.c = CausalOrdering()
        self.node_list = None
        self.sorted_tx_by_timestamp = None

        self.nodes_vs_tx_times = {
            1: [Tx("b", 5), Tx("c", 6)],
            2: [Tx("a", 2), Tx("c", 3), Tx("b", 1)],
            3: [Tx("a", 1), Tx("c", 2), Tx("b", 3)]
        }

        self.nodes_vs_tx_times2 = {
            1: [Tx("1", 5), Tx("2", 11), Tx("3", 16), Tx("4", 6), Tx("5", 7), Tx("6", 10), Tx("7", 25)],
            2: [Tx("1", 3), Tx("2", 17), Tx("3", 19), Tx("4", 8), Tx("5", 11), Tx("6", 15), Tx("7", 21)],
            3: [Tx("1", 6), Tx("2", 12), Tx("3", 13), Tx("4", 15), Tx("5", 9), Tx("6", 11), Tx("7", 20)],
            4: [Tx("1", 2), Tx("2", 7), Tx("3", 9), Tx("4", 14), Tx("5", 18), Tx("6", 3), Tx("7", 24)],
            5: [Tx("1", 1), Tx("2", 2), Tx("3", 5), Tx("4", 10), Tx("5", 12), Tx("6", 20), Tx("7", 21)],
            6: [Tx("1", 1), Tx("2", 6), Tx("3", 9), Tx("4", 10), Tx("5", 15), Tx("6", 20), Tx("7", 26)],
        }

        self.nodes_vs_tx_times3 = {
            1: [Tx("1", 5), Tx("2", 11), Tx("3", 16), Tx("4", 6), Tx("5", 7), Tx("6", 10), Tx("7", 25)],
            2: [Tx("1", 3), Tx("2", 17), Tx("3", 19), Tx("4", 8), Tx("5", 11), Tx("6", 15), Tx("7", 21)],
            3: [Tx("1", 6), Tx("2", 12), Tx("3", 13), Tx("4", 15), Tx("5", 9), Tx("6", 11), Tx("7", 20)],
            4: [Tx("1", 2), Tx("2", 7), Tx("3", 9), Tx("4", 14), Tx("5", 18), Tx("6", 3), Tx("7", 24)],
            5: [Tx("1", 1), Tx("2", 2), Tx("3", 5), Tx("4", 10), Tx("5", 12), Tx("6", 20), Tx("7", 21)],
            6: [Tx("7", 1), Tx("4", 6), Tx("5", 9), Tx("1", 10), Tx("2", 15), Tx("6", 20), Tx("3", 26)],
        }

    def order_test(self):
        #print(self.c.order(self.nodes_vs_tx_times))
        print(self.c.order(self.nodes_vs_tx_times2))
        print(self.c.order(self.nodes_vs_tx_times3))
    def sort_tx_by_timestamp_test(self):
        expected_nodes_vs_tx_times = {
            1: [Tx("b", 5), Tx("c", 6)],
            2: [Tx("b", 1), Tx("a", 2), Tx("c", 3)],
            3: [Tx("a", 1), Tx("c", 2), Tx("b", 3)]
        }
        self.c.sort_tx_by_timestamp(self.nodes_vs_tx_times)
        self.sorted_tx_by_timestamp = expected_nodes_vs_tx_times
        #print(self.sorted_tx_by_timestamp)

    def extract_content_test(self):
        self.c.extract_content(self.sorted_tx_by_timestamp)
        print(self.sorted_tx_by_timestamp)
    #looks good
    def get_unique_tx_list_test(self):
        self.node_list = self.c.get_unique_tx_list(self.sorted_tx_by_timestamp)
        print(self.node_list)
    def first_tx_test(self):
        print(self.sorted_tx_by_timestamp)
        print(self.c.first_tx(self.sorted_tx_by_timestamp))

    def tx_ordering_test(self):
        print("here it is:")
        print(self.sorted_tx_by_timestamp)
        print("end")
        self.c.tx_ordering(self.sorted_tx_by_timestamp, self.node_list)

if __name__ == "__main__":
    #unittest.main()
    c = CausalOrderingTests()
    c.order_test()
    #c.sort_tx_by_timestamp_test()
    #c.extract_content_test()
    #c.get_unique_tx_list_test()
    #c.tx_ordering_test()
    #c.first_tx_test()