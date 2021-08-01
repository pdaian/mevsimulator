from functools import total_ordering

class Transaction:
    """ A transaction on the Ethereum network """
    def __init__(self, sender, fee,txid="",block=""):
        self.sender = sender
        self.fee = fee
        self.metrics = {}
        self.txid = txid
        self.block = block


@total_ordering
class UniswapTransaction(Transaction):
    def __init__(self, x_token, y_token, x_amount, y_amount, sender, fee,txid="",block=""):
        super().__init__(sender, fee,txid,block)
        # tokens involved in transaction
        self.x_token = x_token
        self.y_token = y_token
        # amounts involved in transaction
        self.x_amount = x_amount
        self.y_amount = y_amount


    def __eq__(self, other):
        return ((self.x_token, self.y_token, self.x_amount, self.y_amount) == (other.x_token, other.y_token, other.x_amount, other.y_amount))

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return ((self.x_token, self.y_token, self.x_amount, self.y_amount) < (other.x_token, other.y_token, other.x_amount, other.y_amount))

    def __str__(self):
        return "".join([str(x) for x in [self.x_token, self.y_token, self.x_amount, self.y_amount]])

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
     return "".join([str(self.x_token),str(self.y_token), str(self.x_amount), str(self.y_amount), str(self.sender), str(self.fee), str(self.txid),str(self.block)])

class ETHState:
    def __init__(self):
        self.x = 0
        self.y = 0


class SwapTransaction(UniswapTransaction):

    def _swapquote(self,A, A_reserves, B_reserves): # Computes how much is swaped given the reserves
        k = A_reserves * B_reserves
        return B_reserves - k / (A_reserves + A)

    def execute(self, state):
        if (self.x_amount + self.y_amount == 0):
            pass
        elif self.x_amount == 0:
            # swap for x token
            amountX = self._swapquote(self.y_amount,state.y, state.x)
            state.x -= amountX # we use price as the relevant metric
            state.y += self.y_amount
            return amountX
        elif self.y_amount == 0:
            # swap for y token
            amountY = self._swapquote(self.x_amount,state.x, state.y)
            state.y -= amountY
            state.x += self.x_amount
            return amountY # we use price as the relevant metric

class AddLiquidityTransaction(UniswapTransaction):

    def execute(self, state):
        state.x += self.x_amount
        state.y += self.y_amount

class RemoveLiquidityTransaction(UniswapTransaction):

    def execute(self, state):
        #state.x -= self.x_amount
        #state.y -= self.y_amount
        pass
