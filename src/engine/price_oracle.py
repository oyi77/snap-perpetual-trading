"""
Price Oracle simulation with mock data generation.
"""
import random
import math
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timedelta

from src.models.data_models import MarketData


class PriceOracle:
    """Simulates price oracle with mock data generation."""
    
    def __init__(self, initial_price: Decimal = Decimal('60000')):
        self.current_price = initial_price
        self.price_history: List[Decimal] = [initial_price]
        self.timestamps: List[datetime] = [datetime.now()]
        self.market_data = MarketData(
            symbol="BTC/USD",
            mark_price=initial_price,
            index_price=initial_price
        )
    
    def generate_price_series(
        self, 
        hours: int = 48, 
        volatility: float = 0.02,
        trend: float = 0.0
    ) -> List[Decimal]:
        """Generate a series of prices using geometric Brownian motion."""
        prices = [self.current_price]
        dt = Decimal('1') / Decimal('24')  # 1 hour = 1/24 day
        
        for i in range(hours):
            # Geometric Brownian motion: dS = S * (μ*dt + σ*√dt*Z)
            # where μ is drift (trend), σ is volatility, Z is standard normal
            
            # Random shock
            z = Decimal(str(random.gauss(0, 1)))
            
            # Price change
            drift = Decimal(str(trend)) * dt
            diffusion = Decimal(str(volatility)) * Decimal(str(math.sqrt(float(dt)))) * z
            
            price_change = prices[-1] * (drift + diffusion)
            new_price = prices[-1] + price_change
            
            # Ensure price stays positive
            new_price = max(new_price, Decimal('1000'))
            
            prices.append(new_price)
        
        return prices[1:]  # Exclude initial price
    
    def update_price(self, new_price: Decimal) -> None:
        """Update the current price and market data."""
        self.current_price = new_price
        self.price_history.append(new_price)
        self.timestamps.append(datetime.now())
        
        # Update market data
        self.market_data.mark_price = new_price
        self.market_data.index_price = new_price  # Simplified: index = mark
        self.market_data.timestamp = datetime.now()
        self.market_data.update_funding_rate()
    
    def get_current_price(self) -> Decimal:
        """Get the current price."""
        return self.current_price
    
    def get_market_data(self) -> MarketData:
        """Get current market data."""
        return self.market_data
    
    def get_price_history(self) -> List[Decimal]:
        """Get price history."""
        return self.price_history.copy()
    
    def simulate_price_movement(
        self, 
        volatility: float = 0.02,
        trend: float = 0.0
    ) -> Decimal:
        """Simulate a single price movement."""
        dt = Decimal('1') / Decimal('24')  # 1 hour
        
        # Random shock
        z = Decimal(str(random.gauss(0, 1)))
        
        # Price change
        drift = Decimal(str(trend)) * dt
        diffusion = Decimal(str(volatility)) * Decimal(str(math.sqrt(float(dt)))) * z
        
        price_change = self.current_price * (drift + diffusion)
        new_price = self.current_price + price_change
        
        # Ensure price stays positive and reasonable
        new_price = max(new_price, Decimal('1000'))
        new_price = min(new_price, Decimal('200000'))  # Cap at $200k
        
        self.update_price(new_price)
        return new_price
    
    def simulate_price_spike(self, spike_percentage: float = 0.1) -> Decimal:
        """Simulate a sudden price spike."""
        spike_factor = Decimal(str(1 + spike_percentage))
        new_price = self.current_price * spike_factor
        self.update_price(new_price)
        return new_price
    
    def simulate_price_crash(self, crash_percentage: float = 0.1) -> Decimal:
        """Simulate a sudden price crash."""
        crash_factor = Decimal(str(1 - crash_percentage))
        new_price = self.current_price * crash_factor
        self.update_price(new_price)
        return new_price
    
    def get_price_statistics(self) -> dict:
        """Get price statistics."""
        if len(self.price_history) < 2:
            return {}
        
        prices = [float(p) for p in self.price_history]
        
        # Calculate returns
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        if not returns:
            return {}
        
        # Calculate statistics
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = math.sqrt(variance)
        
        return {
            "current_price": float(self.current_price),
            "price_change": float(self.current_price - self.price_history[0]),
            "price_change_percent": float((self.current_price - self.price_history[0]) / self.price_history[0] * 100),
            "volatility": volatility,
            "mean_return": mean_return,
            "min_price": min(prices),
            "max_price": max(prices),
            "data_points": len(prices)
        }
    
    def reset(self, initial_price: Decimal = Decimal('60000')) -> None:
        """Reset the price oracle."""
        self.current_price = initial_price
        self.price_history = [initial_price]
        self.timestamps = [datetime.now()]
        self.market_data = MarketData(
            symbol="BTC/USD",
            mark_price=initial_price,
            index_price=initial_price
        )


class PriceDataGenerator:
    """Generates various types of price data for testing."""
    
    @staticmethod
    def generate_trending_prices(
        initial_price: Decimal,
        hours: int,
        trend_percent: float = 0.05
    ) -> List[Decimal]:
        """Generate prices with a clear trend."""
        oracle = PriceOracle(initial_price)
        return oracle.generate_price_series(
            hours=hours,
            volatility=0.01,
            trend=trend_percent
        )
    
    @staticmethod
    def generate_volatile_prices(
        initial_price: Decimal,
        hours: int,
        volatility: float = 0.05
    ) -> List[Decimal]:
        """Generate highly volatile prices."""
        oracle = PriceOracle(initial_price)
        return oracle.generate_price_series(
            hours=hours,
            volatility=volatility,
            trend=0.0
        )
    
    @staticmethod
    def generate_sideways_prices(
        initial_price: Decimal,
        hours: int
    ) -> List[Decimal]:
        """Generate sideways moving prices."""
        oracle = PriceOracle(initial_price)
        return oracle.generate_price_series(
            hours=hours,
            volatility=0.005,
            trend=0.0
        )
    
    @staticmethod
    def generate_crash_scenario(
        initial_price: Decimal,
        hours: int,
        crash_hour: int = 24,
        crash_percent: float = 0.3
    ) -> List[Decimal]:
        """Generate prices with a crash scenario."""
        oracle = PriceOracle(initial_price)
        prices = []
        
        # Generate normal prices until crash
        for hour in range(hours):
            if hour == crash_hour:
                # Simulate crash
                oracle.simulate_price_crash(crash_percent)
            else:
                oracle.simulate_price_movement(volatility=0.02)
            
            prices.append(oracle.get_current_price())
        
        return prices
    
    @staticmethod
    def generate_pump_scenario(
        initial_price: Decimal,
        hours: int,
        pump_hour: int = 12,
        pump_percent: float = 0.2
    ) -> List[Decimal]:
        """Generate prices with a pump scenario."""
        oracle = PriceOracle(initial_price)
        prices = []
        
        # Generate normal prices until pump
        for hour in range(hours):
            if hour == pump_hour:
                # Simulate pump
                oracle.simulate_price_spike(pump_percent)
            else:
                oracle.simulate_price_movement(volatility=0.02)
            
            prices.append(oracle.get_current_price())
        
        return prices
