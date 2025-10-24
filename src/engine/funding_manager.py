"""
Funding rate calculation and application system.
"""
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, timedelta

from src.models.data_models import MarketData, User, Position
from src.engine.position_manager import PositionManager


class FundingRateManager:
    """Manages funding rate calculations and applications."""
    
    def __init__(self, position_manager: PositionManager):
        self.position_manager = position_manager
        self.funding_history: List[Dict] = []
        self.last_funding_time: Optional[datetime] = None
        self.funding_interval_hours = 8  # Funding every 8 hours
    
    def calculate_funding_rate(self, market_data: MarketData) -> Decimal:
        """Calculate funding rate based on mark and index prices."""
        if market_data.index_price == Decimal('0'):
            return Decimal('0')
        
        # funding_rate = (mark_price - index_price) / index_price * (1/8)
        price_diff = market_data.mark_price - market_data.index_price
        funding_rate = (price_diff / market_data.index_price) * Decimal('0.125')  # 1/8
        
        # Cap funding rate to reasonable bounds (-1% to +1%)
        funding_rate = max(funding_rate, Decimal('-0.01'))
        funding_rate = min(funding_rate, Decimal('0.01'))
        
        return funding_rate
    
    def should_apply_funding(self, current_time: datetime) -> bool:
        """Check if it's time to apply funding."""
        if self.last_funding_time is None:
            return True
        
        time_since_last = current_time - self.last_funding_time
        return time_since_last >= timedelta(hours=self.funding_interval_hours)
    
    def apply_funding(self, market_data: MarketData, current_time: datetime) -> Dict:
        """Apply funding to all positions."""
        if not self.should_apply_funding(current_time):
            return {
                "applied": False,
                "message": "Funding not due yet"
            }
        
        # Update funding rate in market data
        funding_rate = self.calculate_funding_rate(market_data)
        market_data.funding_rate = funding_rate
        
        # Apply funding to positions
        funding_payments = self.position_manager.apply_funding()
        
        # Record funding event
        funding_record = {
            "timestamp": current_time.isoformat(),
            "funding_rate": float(funding_rate),
            "mark_price": float(market_data.mark_price),
            "index_price": float(market_data.index_price),
            "funding_payments": {user_id: float(payment) for user_id, payment in funding_payments.items()},
            "total_funding_paid": float(sum(funding_payments.values()))
        }
        
        self.funding_history.append(funding_record)
        self.last_funding_time = current_time
        
        return {
            "applied": True,
            "funding_rate": float(funding_rate),
            "funding_payments": funding_payments,
            "total_funding_paid": float(sum(funding_payments.values())),
            "message": f"Funding applied successfully. Rate: {funding_rate:.6f}"
        }
    
    def get_funding_rate_history(self, limit: int = 50) -> List[Dict]:
        """Get funding rate history."""
        return self.funding_history[-limit:] if limit else self.funding_history
    
    def get_current_funding_rate(self, market_data: MarketData) -> Decimal:
        """Get current funding rate without applying it."""
        return self.calculate_funding_rate(market_data)
    
    def get_funding_statistics(self) -> Dict:
        """Get funding statistics."""
        if not self.funding_history:
            return {
                "total_funding_events": 0,
                "total_funding_paid": 0.0,
                "average_funding_rate": 0.0,
                "max_funding_rate": 0.0,
                "min_funding_rate": 0.0
            }
        
        total_events = len(self.funding_history)
        total_paid = sum(record["total_funding_paid"] for record in self.funding_history)
        
        funding_rates = [record["funding_rate"] for record in self.funding_history]
        avg_rate = sum(funding_rates) / len(funding_rates)
        max_rate = max(funding_rates)
        min_rate = min(funding_rates)
        
        return {
            "total_funding_events": total_events,
            "total_funding_paid": total_paid,
            "average_funding_rate": avg_rate,
            "max_funding_rate": max_rate,
            "min_funding_rate": min_rate
        }
    
    def simulate_funding_scenarios(self, market_data: MarketData) -> Dict:
        """Simulate different funding scenarios."""
        scenarios = {}
        
        # Scenario 1: Mark price above index (positive funding)
        scenarios["positive_funding"] = {
            "mark_price": float(market_data.mark_price),
            "index_price": float(market_data.mark_price * Decimal('0.99')),  # 1% below mark
            "funding_rate": float(self.calculate_funding_rate(
                MarketData(
                    mark_price=market_data.mark_price,
                    index_price=market_data.mark_price * Decimal('0.99')
                )
            ))
        }
        
        # Scenario 2: Mark price below index (negative funding)
        scenarios["negative_funding"] = {
            "mark_price": float(market_data.mark_price),
            "index_price": float(market_data.mark_price * Decimal('1.01')),  # 1% above mark
            "funding_rate": float(self.calculate_funding_rate(
                MarketData(
                    mark_price=market_data.mark_price,
                    index_price=market_data.mark_price * Decimal('1.01')
                )
            ))
        }
        
        # Scenario 3: Mark price equals index (zero funding)
        scenarios["zero_funding"] = {
            "mark_price": float(market_data.mark_price),
            "index_price": float(market_data.mark_price),
            "funding_rate": 0.0
        }
        
        return scenarios
    
    def calculate_funding_impact(
        self, 
        position: Position, 
        funding_rate: Decimal
    ) -> Dict:
        """Calculate funding impact for a specific position."""
        position_value = position.quantity * position.entry_price
        
        if position.side.value == "long":
            # Long positions pay funding when rate is positive
            funding_payment = position_value * funding_rate
        else:
            # Short positions pay funding when rate is negative
            funding_payment = position_value * (-funding_rate)
        
        return {
            "position_value": float(position_value),
            "funding_rate": float(funding_rate),
            "funding_payment": float(funding_payment),
            "position_side": position.side.value,
            "impact_percentage": float(funding_payment / position.collateral * 100) if position.collateral > 0 else 0
        }
    
    def get_user_funding_summary(self, user_id: str) -> Dict:
        """Get funding summary for a specific user."""
        user = self.position_manager.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        position = user.get_position("BTC/USD")
        if not position:
            return {
                "user_id": user_id,
                "has_position": False,
                "total_funding_paid": float(position.funding_paid) if position else 0.0
            }
        
        # Calculate total funding paid from history
        total_funding_paid = Decimal('0')
        for record in self.funding_history:
            if user_id in record["funding_payments"]:
                total_funding_paid += Decimal(str(record["funding_payments"][user_id]))
        
        return {
            "user_id": user_id,
            "has_position": True,
            "position_side": position.side.value,
            "position_value": float(position.position_value),
            "total_funding_paid": float(total_funding_paid),
            "funding_paid_from_position": float(position.funding_paid),
            "funding_impact_percentage": float(total_funding_paid / user.collateral * 100) if user.collateral > 0 else 0
        }
    
    def reset_funding_history(self) -> None:
        """Reset funding history."""
        self.funding_history = []
        self.last_funding_time = None
