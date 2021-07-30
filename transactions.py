class Transaction:
    """ A transaction on the Ethereum network """
    def __init__(self, sender, fee):
        self.sender = sender
        self.fee = fee


class UniswapTransaction(Transaction):
    def __init__(self, x_token, y_token, x_amount, y_amount, sender, fee):
        super().__init__(sender, fee)
        # tokens involved in transaction
        self.x_token = x_token
        self.y_token = y_token
        # amounts involved in transaction
        self.x_amount = x_amount
        self.y_amount = y_amount


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
            state.x -= amountX
            state.y += self.y_amount
        elif self.y_amount == 0:
            # swap for y token
            amountY = self._swapquote(self.x_amount,state.x, state.y)
            state.y -= amountY
            state.x += self.x_amount

class AddLiquidityTransaction(UniswapTransaction):

    def execute(self, state):
        state.x += self.x_amount
        state.y += self.y_amount

class RemoveLiquidityTransaction(UniswapTransaction):

    def execute(self, state):
        #state.x -= self.x_amount
        #state.y -= self.y_amount
        pass
