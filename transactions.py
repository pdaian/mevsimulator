class Transaction:
    """ A transaction on the Ethereum network """
    def __init__(self, sender, fee):
        self.sender = sender
        self.fee = fee


class UniswapTransaction(Transaction):
    def __init__(self, first_token, second_token, first_amount, second_amount, sender, fee):
        super().__init__(sender, fee)
        # tokens involved in transaction
        self.first_token = first_token
        self.second_token = second_token
        # amounts involved in transaction
        self.first_amount = first_amount
        self.second_amount = second_amount


class ETHState:
    def __init__(self):
        self.first_token_amount = 0
        self.second_token_amount = 0

class SwapTransaction(UniswapTransaction):

    def execute(ETHState):
        pass


class AddLiquidityTransaction(UniswapTransaction):

    def execute(ETHState):
        pass

