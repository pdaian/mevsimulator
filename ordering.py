class CausalOrdering:
    def order(self, sender_and_time_sent, transaction_receiving_times):
        # try to understand case in which transaction not received by one node but received by others and the node that has not received it sends a message
        # returns a random transaction_sequence in the order the algorithm would have output

        # Transaction sequence looks something like this for 2 nodes: (0 indexed Tx #)
        #     {Tx #: [Process # That Sent Tx, Time Sent]}
        #     {0: (2,2)}
        #     {1: (1,5)}

        # Received Times:
        #     {Tx #: [Time each Process Received Tx}
        #     {0: [5,3,4]}
        #     {1: [6,7,8]}

        # 1. iterate through all the sending times and make sure that a transaction sent before another is received before another

        # update vector clock for each sending_time
        sender_tx_num = len(sender_and_time_sent)
        receiving_tx_num = len(transaction_receiving_times)
        process_num = len(transaction_receiving_times[0])

        assert (sender_tx_num != 0)
        assert (receiving_tx_num != 0)
        assert (sender_tx_num == sender_tx_num)
        assert (process_num != 0)
        error_process_num = [tx_id for tx_id in transaction_receiving_times if
                             transaction_receiving_times[tx_id] != process_num]
        assert (len(error_process_num) == 0)

        vector_clock = self.get_vector_clock(process_num)
        buffer = {process_id: [] for process_id in range(process_num)}

        for tx_id in sender_and_time_sent:
            sender, time_sent = sender_and_time_sent[tx_id]
            vector_clock[sender][sender] = time_sent
            for index, value in enumerate(time_sent):
                if index != sender:
                    vector_clock[sender][index] = value

    def get_vector_clock(self, num_processes):
        vector_clock = {}
        for i in range(num_processes):
            vector_clock.update({i: [0] * num_processes})
        return vector_clock


class AequitasOrdering:
    def order(self, transaction_sequence):
        pass
