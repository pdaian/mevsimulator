class Message:
    def __init__(self, msg_vector_clock, receiver):
        self.vector_clock = msg_vector_clock
        self.receiver = receiver

class CausalOrdering:
    def order(self, sender_and_time_sent, transaction_receiving_times):
        # try to understand case in which transaction not received by one node but received by others and the node that has not received it sends a message
        # returns a random transaction_sequence in the order the algorithm would have output

        # Transaction sequence (sender_and_time_sent) looks something like this for 2 nodes: (0 indexed Tx #)
        #     {Tx #: [Process # That Sent Tx, Time Sent]}
        #     {0: (2,2)}
        #     {1: (1,5)}

        # Received Times (transaction_receiving_times):
        #     {Tx #: [Time each Process Received Tx}
        #     {0: [0,3,4]}
        #     {1: [6,0,8]}

        # Buffer:
        #   {Process #: [List of waiting txs]}

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

        vector_clocks = self.get_vector_clock(process_num)
        buffer = {process_id: [] for process_id in range(process_num)}

        for tx_id in sender_and_time_sent:
            sender, time_sent = sender_and_time_sent[tx_id]
            if self.message_can_be_sent(vector_clocks):
                for receiver in transaction_receiving_times[tx_id]:
                    if receiver != sender:
                        if self.message_can_be_received(vector_clocks[sender], vector_clocks[receiver], sender):  # do we buffer for everyone or just one person?
                            vector_clocks[sender][sender] += 1
                            vector_clocks[receiver] = vector_clocks[sender]
                        else:
                            buffer[receiver].append(Message(vector_clocks[sender], receiver))
            while True:
                added = False
                for msg in buffer[receiver]:
                    if self.message_can_be_sent(msg.vector_clock, vector_clocks[msg.receiver]):
                        vector_clocks[msg.receiver] = msg.vector_clock[:]
                        added = True
                if not added:
                    break

    def message_can_be_sent(self, vector_clocks):
        for i in range(len(vector_clocks) - 1):
            if vector_clocks[i] != vector_clocks[i + 1]:
                return False
        return True
    def message_can_be_received(self, sender_vector_clock, receiver_vector_clock, sender):
        if sender_vector_clock[sender] != receiver_vector_clock[sender] + 1:
            return False
        for index, s, r in enumerate(zip(sender_vector_clock, receiver_vector_clock)):
            if s != r and index != sender:
                return False
        return True

    def get_vector_clock(self, num_processes):
        vector_clock = {}
        for i in range(num_processes):
            vector_clock.update({i: [0] * num_processes})
        return vector_clock



class AequitasOrdering:
    def order(self, transaction_sequence):
        pass
