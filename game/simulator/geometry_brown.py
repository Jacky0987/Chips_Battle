import datetime
import numpy as np
import matplotlib.pyplot as plt

class AdvancedStockSimulation:
    def __init__(self, initial_price, drift, volatility, time_period, num_simulations):
        self.initial_price = initial_price
        self.drift = drift
        self.volatility = volatility
        self.time_period = time_period
        self.num_simulations = num_simulations
        self.price_paths = []

    def simulate_price_path(self):
        dt = 1/252  # Daily time step
        num_steps = int(self.time_period * 252)  # Number of days in the simulation period

        # Generate random increments based on a normal distribution
        increments = np.random.normal((self.drift - 0.5 * self.volatility**2) * dt, self.volatility * np.sqrt(dt), (self.num_simulations, num_steps))

        # Calculate cumulative increments
        cumulative_increments = np.cumsum(increments, axis=1)

        # Initialize price paths with the initial price
        price_paths = np.ones((self.num_simulations, num_steps + 1)) * self.initial_price

        # Calculate the price paths
        for i in range(self.num_simulations):
            price_paths[i, 1:] = self.initial_price * np.exp(cumulative_increments[i])

        self.price_paths = price_paths

    def plot_price_paths(self):
        plt.figure(figsize=(10, 6))
        for price_path in self.price_paths:
            plt.plot(range(self.time_period * 252 + 1), price_path)
        plt.xlabel('Days')
        plt.ylabel('Stock Price')
        plt.title('Stock Price Simulation')
        plt.show()

# Example usage
simulation = AdvancedStockSimulation(100, 0.1, 0.2, 1, 100)
simulation.simulate_price_path()
simulation.plot_price_paths()