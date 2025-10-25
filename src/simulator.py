"""
Main simulation loop and trading simulator.
"""
import json
import random
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime, timedelta

from src.models.data_models import (
    User, Order, OrderSide, OrderType, SimulationEvent, MarketData
)
from src.engine.position_manager import PositionManager
from src.engine.order_book import OrderBook
from src.engine.matching_engine import OrderMatchingEngine
from src.engine.price_oracle import PriceOracle
from src.engine.funding_manager import FundingRateManager
from src.engine.liquidation_engine import LiquidationEngine
from src.logging_system import TradingLogger


class TradingSimulator:
    """Main trading simulator that orchestrates all components."""
    
    def __init__(self, logs_dir: str = "logs"):
        # Initialize core components
        self.position_manager = PositionManager()
        self.order_book = OrderBook()
        self.matching_engine = OrderMatchingEngine(self.position_manager)
        self.price_oracle = PriceOracle()
        self.funding_manager = FundingRateManager(self.position_manager)
        self.liquidation_engine = LiquidationEngine(self.position_manager)
        
        # Simulation state
        self.current_time = datetime.now()
        self.simulation_hours = 0
        self.events: List[SimulationEvent] = []
        self.simulation_log: List[Dict] = []
        
        # Statistics
        self.total_trades = 0
        self.total_volume = Decimal('0')
        self.total_funding_paid = Decimal('0')
        self.total_liquidation_fees = Decimal('0')
        
        # Initialize logging system
        self.logger = TradingLogger(logs_dir)
        
        # Connect logger to matching engine
        self.matching_engine.logger = self.logger
    
    def load_simulation_config(self, config_file: str) -> Dict:
        """Load simulation configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Load users
            for user_data in config.get("users", []):
                user = User(
                    id=user_data["id"],
                    collateral=Decimal(str(user_data["collateral"]))
                )
                self.position_manager.add_user(user)
            
            # Load price series
            prices = config.get("prices", [])
            if prices:
                self.price_oracle = PriceOracle(Decimal(str(prices[0])))
                for price in prices[1:]:
                    self.price_oracle.update_price(Decimal(str(price)))
            
            # Load events
            self.events = [
                SimulationEvent(
                    time=event["time"],
                    action=event["action"],
                    data=event.get("data", {})
                )
                for event in config.get("events", [])
            ]
            
            return {"success": True, "message": "Configuration loaded successfully"}
            
        except Exception as e:
            return {"success": False, "message": f"Error loading config: {str(e)}"}
    
    def run_simulation(self, hours: int = 48) -> Dict:
        """Run the main simulation loop."""
        print(f"Starting simulation for {hours} hours...")
        
        self.simulation_hours = hours
        self.simulation_log = []
        self.current_time = datetime.now()
        
        # Log simulation start
        config_summary = {
            "hours": hours,
            "users": list(self.position_manager.users.keys()),
            "initial_price": float(self.price_oracle.get_current_price())
        }
        self.logger.log_simulation_start(config_summary)
        
        self._log_event("simulation_start", {"hours": hours})
        
        for hour in range(hours + 1):  # Include hour 0
            self.simulation_hours = hour
            self.current_time = datetime.now() + timedelta(hours=hour)
            
            # Process events for this hour
            self._process_hourly_events(hour)
            
            # Update price (if not already updated by events)
            if not self._has_price_update_event(hour):
                old_price = self.price_oracle.get_current_price()
                self._update_price_randomly()
                new_price = self.price_oracle.get_current_price()
                price_change = new_price - old_price
                price_change_percent = float(price_change / old_price * 100) if old_price > 0 else 0
                
                # Log price update
                self.logger.log_price_update(hour, old_price, new_price, price_change, price_change_percent)
            
            # Update market data for position PNL calculations
            market_data = self.price_oracle.get_market_data()
            self.position_manager.update_market_data(market_data)
            
            # Check for liquidations
            liquidations = self.liquidation_engine.check_liquidations(market_data)
            
            for liquidation in liquidations:
                self.logger.log_liquidation(hour, liquidation)
                if liquidation.get("liquidated", False):
                    self.total_liquidation_fees += Decimal(str(liquidation.get("liquidation_fee", 0)))
            
            # Apply funding every 8 hours
            if hour % 8 == 0 and hour > 0:
                funding_result = self.funding_manager.apply_funding(
                    self.price_oracle.get_market_data(),
                    self.current_time
                )
                self.logger.log_funding_applied(hour, funding_result)
                
                if funding_result["applied"]:
                    self.total_funding_paid += Decimal(str(funding_result["total_funding_paid"]))
            
            # Log hourly summary
            self._log_hourly_summary(hour, liquidations)
            
            # Add random events
            if random.random() < 0.3:  # 30% chance of random event
                self.add_random_events(hours)
        
        print("Simulation completed successfully!")
        
        # Generate final report
        final_report = self._generate_final_report()
        self._log_event("simulation_end", final_report)
        
        # Log simulation end
        self.logger.log_simulation_end(final_report)
        
        # Save detailed logs
        self.logger.save_detailed_logs()
        
        return final_report
    
    def _process_hourly_events(self, hour: int) -> None:
        """Process events scheduled for this hour."""
        for event in self.events:
            if event.time == hour:
                self._process_event(event)
    
    def _process_event(self, event: SimulationEvent) -> None:
        """Process a single simulation event."""
        if event.action == "place_order":
            self._process_order_event(event)
        elif event.action == "price_update":
            self._process_price_update_event(event)
        elif event.action == "apply_funding":
            self._process_funding_event(event)
        elif event.action == "random_order":
            self._process_random_order_event(event)
    
    def _process_order_event(self, event: SimulationEvent) -> None:
        """Process an order placement event."""
        data = event.data
        
        order = Order(
            user_id=data["user"],
            side=OrderSide(data["side"]),
            order_type=OrderType.LIMIT,
            quantity=Decimal(str(data["quantity"])),
            price=Decimal(str(data["price"])),
            leverage=data.get("leverage", 1)
        )
        
        result = self.matching_engine.place_order(order, self.simulation_hours)
        
        if result["valid"]:
            self.total_trades += len(result["trades"])
            for trade in result["trades"]:
                self.total_volume += Decimal(str(trade["quantity"])) * Decimal(str(trade["price"]))
        
        # Log order placement with comprehensive logging
        self.logger.log_order_placed(self.simulation_hours, event.data, result)
        
        self._log_event("order_placed", {
            "event": event.data,
            "result": {
                "valid": result.get("valid", False),
                "order_id": result.get("order_id", ""),
                "status": result.get("status", ""),
                "trades_count": len(result.get("trades", [])),
                "message": result.get("message", "")
            }
        })
    
    def _process_price_update_event(self, event: SimulationEvent) -> None:
        """Process a price update event."""
        new_price = Decimal(str(event.data["price"]))
        self.price_oracle.update_price(new_price)
        
        self._log_event("price_update", {
            "new_price": float(new_price),
            "hour": event.time
        })
    
    def _process_funding_event(self, event: SimulationEvent) -> None:
        """Process a funding application event."""
        funding_result = self.funding_manager.apply_funding(
            self.price_oracle.get_market_data(),
            self.current_time
        )
        
        self._log_event("funding_applied", {
            "applied": funding_result["applied"],
            "funding_rate": funding_result.get("funding_rate", 0),
            "total_funding_paid": funding_result.get("total_funding_paid", 0),
            "message": funding_result.get("message", "")
        })
    
    def _process_random_order_event(self, event: SimulationEvent) -> None:
        """Process a random order generation event."""
        users = list(self.position_manager.users.keys())
        if not users:
            return
        
        user_id = random.choice(users)
        side = random.choice([OrderSide.BUY, OrderSide.SELL])
        
        # Generate random order parameters
        current_price = self.price_oracle.get_current_price()
        price_variance = Decimal('0.02')  # 2% variance
        
        if side == OrderSide.BUY:
            # Buy orders slightly below current price
            price = current_price * (Decimal('1') - price_variance * Decimal(str(random.random())))
        else:
            # Sell orders slightly above current price
            price = current_price * (Decimal('1') + price_variance * Decimal(str(random.random())))
        
        quantity = Decimal(str(random.uniform(0.1, 2.0)))  # Random quantity
        leverage = random.randint(1, 10)
        
        order = Order(
            user_id=user_id,
            side=side,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
            leverage=leverage
        )
        
        result = self.matching_engine.place_order(order, self.simulation_hours)
        
        # Log random order with comprehensive logging
        order_data = {
            "user_id": user_id,
            "side": side.value,
            "quantity": float(quantity),
            "price": float(price),
            "leverage": leverage
        }
        self.logger.log_random_order(self.simulation_hours, order_data, result)
        
        self._log_event("random_order", {
            "order": order_data,
            "result": {
                "valid": result.get("valid", False),
                "order_id": result.get("order_id", ""),
                "status": result.get("status", ""),
                "trades_count": len(result.get("trades", [])),
                "message": result.get("message", "")
            }
        })
    
    def _update_price_randomly(self) -> None:
        """Update price with random movement."""
        volatility = 0.02  # 2% volatility
        trend = 0.0  # No trend
        
        new_price = self.price_oracle.simulate_price_movement(volatility, trend)
        
        self._log_event("price_update", {
            "new_price": float(new_price),
            "hour": self.simulation_hours
        })
    
    def _has_price_update_event(self, hour: int) -> bool:
        """Check if there's a price update event for this hour."""
        return any(
            event.time == hour and event.action == "price_update"
            for event in self.events
        )
    
    def _log_hourly_summary(self, hour: int, liquidations: List[Dict]) -> None:
        """Log hourly simulation summary."""
        market_data = self.price_oracle.get_market_data()
        
        summary = {
            "hour": hour,
            "price": float(market_data.mark_price),
            "funding_rate": float(market_data.funding_rate),
            "liquidations": len(liquidations),
            "total_trades": self.total_trades,
            "total_volume": float(self.total_volume),
            "user_summaries": self.position_manager.get_all_user_summaries()
        }
        
        self.simulation_log.append(summary)
    
    def _log_event(self, event_type: str, data: Dict) -> None:
        """Log a simulation event."""
        log_entry = {
            "timestamp": self.current_time.isoformat(),
            "hour": self.simulation_hours,
            "event_type": event_type,
            "data": data
        }
        
        self.simulation_log.append(log_entry)
        
        # Keep only last 1000 log entries to prevent memory issues
        if len(self.simulation_log) > 1000:
            self.simulation_log = self.simulation_log[-1000:]
    
    def _generate_final_report(self) -> Dict:
        """Generate final simulation report."""
        market_data = self.price_oracle.get_market_data()
        
        # Get statistics from all components
        execution_stats = self.matching_engine.get_execution_statistics()
        funding_stats = self.funding_manager.get_funding_statistics()
        liquidation_stats = self.liquidation_engine.get_liquidation_statistics()
        price_stats = self.price_oracle.get_price_statistics()
        
        # Calculate final user balances
        final_balances = {}
        for user_id, user in self.position_manager.users.items():
            position = user.get_position("BTC/USD")
            total_equity = user.collateral + user.total_realized_pnl
            
            if position:
                total_equity += position.unrealized_pnl
            
            final_balances[user_id] = {
                "collateral": float(user.collateral),
                "realized_pnl": float(user.total_realized_pnl),
                "unrealized_pnl": float(position.unrealized_pnl) if position else 0.0,
                "total_equity": float(total_equity),
                "has_position": position is not None
            }
        
        return {
            "simulation_summary": {
                "total_hours": self.simulation_hours,
                "final_price": float(market_data.mark_price),
                "price_change_percent": price_stats.get("price_change_percent", 0),
                "total_trades": execution_stats["total_trades"],
                "total_volume": execution_stats["total_volume"],
                "total_funding_paid": funding_stats["total_funding_paid"],
                "total_liquidations": liquidation_stats["total_liquidations"]
            },
            "execution_statistics": execution_stats,
            "funding_statistics": funding_stats,
            "liquidation_statistics": liquidation_stats,
            "price_statistics": price_stats,
            "final_user_balances": final_balances,
            "simulation_log": self.simulation_log
        }
    
    def get_current_state(self) -> Dict:
        """Get current simulation state."""
        market_data = self.price_oracle.get_market_data()
        
        return {
            "current_hour": self.simulation_hours,
            "current_price": float(market_data.mark_price),
            "funding_rate": float(market_data.funding_rate),
            "order_book_summary": self.matching_engine.get_order_book_summary(),
            "user_summaries": self.position_manager.get_all_user_summaries(),
            "liquidation_risks": self.liquidation_engine.get_all_liquidation_risks(market_data)
        }
    
    def add_random_events(self, num_events: int = 10, hours: int = None) -> None:
        """Add random events to the simulation."""
        users = list(self.position_manager.users.keys())
        if not users:
            return
        
        # Use provided hours or fall back to simulation_hours
        max_hours = hours if hours is not None else self.simulation_hours
        if max_hours <= 1:
            max_hours = 24  # Default to 24 hours if not set
        
        for _ in range(num_events):
            hour = random.randint(1, max(1, max_hours - 1))
            user_id = random.choice(users)
            
            # Random order event
            event = SimulationEvent(
                time=hour,
                action="random_order",
                data={"user": user_id}
            )
            self.events.append(event)
    
    def save_simulation_results(self, filename: str) -> Dict:
        """Save simulation results to JSON file."""
        try:
            final_report = self._generate_final_report()
            
            with open(filename, 'w') as f:
                json.dump(final_report, f, indent=2, default=str)
            
            return {"success": True, "message": f"Results saved to {filename}"}
            
        except Exception as e:
            return {"success": False, "message": f"Error saving results: {str(e)}"}
