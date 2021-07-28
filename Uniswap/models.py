import numpy as np
import networkx as nx
import random
from matplotlib import pyplot as plt




class Pool: # Uniswap pool of tokenX and tokenY
    def __init__(self,X,Y, X_ID, Y_ID,creator_ID, fee = 0):
        self.X_ID = X_ID # X_ID simulates the token address
        self.Y_ID = Y_ID # Y_Id simulates the token address
        
        self.k = X*Y     # k of the constant product formula
        
        self.X_reserves = X # X reserves in the pool
        self.Y_reserves = Y # Y reserves in the pool
         
        self.liquidity = {} # Dictionary of liquidity balances of the liquidity providers
        self.total_supply = 1 # Total supply of liquidit tokens
        self.liquidity[creator_ID] = 1 # The creator has all the liquidity tokens
    def _quote(self,amountA, reserveA, reserveB): # This formula is used to compute how to add liquidity
        assert amountA > 0, "Invalid quote"
        assert reserveA > 0 and reserveB > 0, "Invalid quote"
        amountB = amountA*reserveB/reserveA
        return amountB
    def AddLiquidity(self,x,y,x_min,y_min, trader_ID): # Simulates addLiquidity of Uniswap protocol
        if self.X_reserves == 0 and self.Y_reserves == 0:
            self.X_reserves = x
            self.Y_reserves = y
            return 0,0,0
        
        amountYOptimal = self._quote(x,self.X_reserves, self.Y_reserves)
        amountXOptimal = self._quote(y,self.Y_reserves, self.X_reserves)
        
        if amountYOptimal <= y:
            if (amountYOptimal>=y_min):
                self.positions[trader_ID] += self.total_supply * x/self.X_reserves
                self.total_supply += self.total_supply * x/self.X_reserves
                self.X_reserves += x
                self.Y_reserves += amountYOptimal
                
                return x, amountYOptimal, x/self.X_reserves
            else:
                return 0, 0, 0
        else:
            if(amountXOptimal >= x_min):
                self.positions[trader_ID] += self.total_supply * x/self.X_reserves
                self.total_supply += self.total_supply * x/self.X_reserves
                self.X_reserves += amountXOptimal
                self.Y_reserves += y
                return amountXOptimal, y, amountXOptimal / self.X_reserves
            else:
                return 0,0,0
    def RemoveLiquidity(self,position, trader_ID): # Removes liquidity of a trader.
        assert 0 < position and position <= self.liquidity[trader_ID], "Invalid_position"
        x = self.X_reserves * position
        y = self.Y_reserves * position
        
        self.X_reserves -= x
        self.Y_reserves -= y
        self.total_supply -= position
        self.liquidity[trader_ID] -= position 
        
        return x,y
        
    def _swapquote(self,A, A_reserves, B_reserves): # Computes how much is swaped given the reserves
        k = A_reserves * B_reserves
        return B_reserves - k / (A_reserves + A)
    def SwapXForY(self,x,y_min):
        amountY = self._swapquote(x,self.X_reserves, self.Y_reserves)
        assert(y_min <= amountY)
        self.X_reserves += x
        self.Y_reserves -= amountY
        return amountY
    def SwapYForX(self,y,x_min):
        amountX = self._swapquote(y,self.Y_reserves, self.X_reserves)
        assert(x_min <= amountX)
        self.X_reserves -= amountX
        self.Y_reserves += y
        return amountX



class AMM:
    def __init__(self):
        self.pools      = {}          # Pair_pools dictionary, contains pool created.
        self.tokens     = []          # Tokens that have a pool
        self.pools_graph = nx.Graph() # Vertices = tokens, edges = Pools, this graph is useful for modelling 
                                      # Dex arbitragers
    def create_pool(self,tokenA,tokenB, A_reserves, B_reserves,creator_ID): # Simulates the creation of a pool
        if ((tokenA, tokenB) in self.pools.keys() or (tokenB, tokenA) in self.pools.keys()):
            return "Already exists the pool"
        else:
            self.pools[(tokenA,tokenB)] = Pool(A_reserves,B_reserves, tokenA, tokenB, creator_ID)
            if tokenA not in self.tokens:
                self.tokens.append(tokenA)
                self.pools_graph.add_node(tokenA, pos =[random.uniform(0, 10),random.uniform(0, 10)])
            if tokenB not in self.tokens:
                self.tokens.append(tokenB)
                self.pools_graph.add_node(tokenA, pos =[random.uniform(0, 10),random.uniform(0, 10)])
            self.pools_graph.add_edge(tokenA,tokenB)
            return "pool created" 
        
#Geometric Brownian motion
# Simulation of Centralized exchange with different stochastic process.
# Will include random walks,...
class reference_market:
    def __init__(self,tokens_list_ID, center_ID):
        self.tokens_list  = tokens_list_ID
        self.center_token = center_ID 
        self.token_prices = {}
        self.tokens_sigma = {}
        self.tokens_mu    = {}
        self.tokens_tau   = {}
        self.time         = 0
        self._init_stochastic_proces()
    def _init_stochastic_proces(self):
        for token_ID in self.tokens_list:
            self.tokens_sigma[token_ID] = random.uniform(0, 1)
            self.tokens_mu[token_ID]    = random.uniform(0, 1)
            self.tokens_tau[token_ID]   = random.uniform(0, 1)
            self.token_prices[token_ID] = 1
    def update_prices(self):
        self.time  +=1
        t = self.time
        for token_ID in self.tokens_list:
            mu = self.tokens_mu[token_ID]
            sigma = self.tokens_sigma[token_ID]
            x = np.random.normal(mu, sigma, 1)
            self.token_prices[token_ID] = np.exp((mu - sigma**2/2) * t + sigma * x)
        self.token_prices[self.center_token] = 1    
    def update_prieces_Langevin(self): # Langevin stochastic process
        dt = 0.01  # Time step.
        T = 10  # Total time.
        n = int(T / dt)  # Number of time steps.
        t = np.linspace(0., T, n)  # Vector of times.
        
        sqrtdt = np.sqrt(dt)
        for token_ID in self.tokens_list:
            x = np.zeros(n)
            mu = self.tokens_mu[token_ID]
            sigma = self.tokens_sigma[token_ID] 
            tau  = self.tokens_tau[token_ID]
            sigma_bis = sigma * np.sqrt(2. / tau)
            for i in range(n - 1):
                x[i + 1] = abs(x[i] + dt * (-(x[i] - mu) / tau) + sigma_bis * sqrtdt * np.random.randn())
            self.token_prices[token_ID] = x
        