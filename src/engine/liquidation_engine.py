"""
Liquidation engine with margin monitoring and automatic position closure.
"""
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime

from src.models.data_models import Position, User, MarketData
from src.engine.position_manager import PositionManager


class LiquidationEngine:
    """Handles liquidation monitoring and execution."""
    
    def __init__(self, position_manager: PositionManager):
        self.position_manager = position_manager
        self.liquidation_history: List[Dict] = []
        self.liquidation_fee_rate = Decimal('0.01')  # 1% liquidation fee
        self.liquidation_threshold = Decimal('1.0')  # Liquidation when equity < maintenance margin
    
    def check_liquidations(self, market_data: MarketData) -> List[Dict]:
        """Check for positions that need to be liquidated."""
        liquidatable_positions = self.position_manager.get_liquidatable_positions()
        liquidations = []
        
        for position in liquidatable_positions:
            liquidation_result = self.liquidate_position(position, market_data)
            liquidations.append(liquidation_result)
        
        return liquidations
    
    def liquidate_position(self, position: Position, market_data: MarketData) -> Dict:
        """Liquidate a specific position."""
        user = self.position_manager.get_user(position.user_id)
        if not user:
            return {
                "success": False,
                "message": f"User {position.user_id} not found",
                "position_id": position.user_id
            }
        
        # Calculate liquidation details
        liquidation_price = market_data.mark_price
        position_value = position.quantity * liquidation_price
        
        # Calculate PNL
        if position.side.value == "long":
            realized_pnl = (liquidation_price - position.entry_price) * position.quantity
        else:
            realized_pnl = (position.entry_price - liquidation_price) * position.quantity
        
        # Calculate liquidation fee
        liquidation_fee = position_value * self.liquidation_fee_rate
        
        # Calculate final collateral
        final_collateral = position.collateral + realized_pnl - liquidation_fee
        
        # Record liquidation
        liquidation_record = {
            "timestamp": datetime.now().isoformat(),
            "user_id": position.user_id,
            "position_side": position.side.value,
            "position_quantity": float(position.quantity),
            "entry_price": float(position.entry_price),
            "liquidation_price": float(liquidation_price),
            "position_value": float(position_value),
            "realized_pnl": float(realized_pnl),
            "liquidation_fee": float(liquidation_fee),
            "initial_collateral": float(position.collateral),
            "final_collateral": float(max(Decimal('0'), final_collateral)),
            "margin_ratio_before": float(position.margin_ratio),
            "leverage": position.leverage
        }
        
        # Execute liquidation
        liquidation_fee_paid = self.position_manager.liquidate_position(position)
        
        # Update liquidation record with actual fee paid
        liquidation_record["actual_liquidation_fee"] = float(liquidation_fee_paid)
        
        # Add to history
        self.liquidation_history.append(liquidation_record)
        
        return {
            "success": True,
            "liquidation_record": liquidation_record,
            "message": f"Position liquidated successfully. Fee: {liquidation_fee_paid}"
        }
    
    def simulate_liquidation_scenarios(self, market_data: MarketData) -> Dict:
        """Simulate different liquidation scenarios."""
        scenarios = {}
        
        for user_id, user in self.position_manager.users.items():
            position = user.get_position("BTC/USD")
            if not position:
                continue
            
            # Current scenario
            scenarios[user_id] = {
                "current": self._analyze_position_liquidation_risk(position, market_data),
                "price_drop_10": self._analyze_position_liquidation_risk(
                    position, 
                    MarketData(mark_price=market_data.mark_price * Decimal('0.9'))
                ),
                "price_drop_20": self._analyze_position_liquidation_risk(
                    position, 
                    MarketData(mark_price=market_data.mark_price * Decimal('0.8'))
                ),
                "price_drop_30": self._analyze_position_liquidation_risk(
                    position, 
                    MarketData(mark_price=market_data.mark_price * Decimal('0.7'))
                )
            }
        
        return scenarios
    
    def _analyze_position_liquidation_risk(
        self, 
        position: Position, 
        market_data: MarketData
    ) -> Dict:
        """Analyze liquidation risk for a position at given market data."""
        # Update PNL with current market data
        if position.side.value == "long":
            unrealized_pnl = (market_data.mark_price - position.entry_price) * position.quantity
        else:
            unrealized_pnl = (position.entry_price - market_data.mark_price) * position.quantity
        
        # Calculate equity
        equity = position.collateral + unrealized_pnl
        
        # Calculate maintenance margin
        position_value = position.quantity * market_data.mark_price
        maintenance_margin = position_value * Decimal('0.05')
        
        # Calculate margin ratio
        margin_ratio = equity / maintenance_margin if maintenance_margin > 0 else Decimal('inf')
        
        # Calculate liquidation price
        liquidation_price = self._calculate_liquidation_price(position, market_data)
        
        return {
            "mark_price": float(market_data.mark_price),
            "unrealized_pnl": float(unrealized_pnl),
            "equity": float(equity),
            "maintenance_margin": float(maintenance_margin),
            "margin_ratio": float(margin_ratio),
            "is_liquidatable": equity < maintenance_margin,
            "liquidation_price": float(liquidation_price),
            "price_distance_to_liquidation": float(abs(market_data.mark_price - liquidation_price)),
            "liquidation_distance_percent": float(
                abs(market_data.mark_price - liquidation_price) / market_data.mark_price * 100
            )
        }
    
    def _calculate_liquidation_price(self, position: Position, market_data: MarketData) -> Decimal:
        """Calculate the liquidation price for a position."""
        # For long positions: liquidation when equity = maintenance margin
        # equity = collateral + (liquidation_price - entry_price) * quantity
        # maintenance_margin = liquidation_price * quantity * 0.05
        # Solving: collateral + (lp - ep) * q = lp * q * 0.05
        # lp = (collateral - ep * q) / (q * 0.05 - q)
        
        if position.side.value == "long":
            # Long liquidation price
            numerator = position.collateral - position.entry_price * position.quantity
            denominator = position.quantity * Decimal('0.05') - position.quantity
            if denominator != Decimal('0'):
                liquidation_price = numerator / denominator
            else:
                liquidation_price = Decimal('0')
        else:
            # Short liquidation price
            numerator = position.collateral + position.entry_price * position.quantity
            denominator = position.quantity * Decimal('0.05') + position.quantity
            if denominator != Decimal('0'):
                liquidation_price = numerator / denominator
            else:
                liquidation_price = Decimal('inf')
        
        return liquidation_price
    
    def get_liquidation_history(self, limit: int = 50) -> List[Dict]:
        """Get liquidation history."""
        return self.liquidation_history[-limit:] if limit else self.liquidation_history
    
    def get_liquidation_statistics(self) -> Dict:
        """Get liquidation statistics."""
        if not self.liquidation_history:
            return {
                "total_liquidations": 0,
                "total_liquidation_fees": 0.0,
                "total_collateral_lost": 0.0,
                "average_liquidation_size": 0.0
            }
        
        total_liquidations = len(self.liquidation_history)
        total_fees = sum(record["actual_liquidation_fee"] for record in self.liquidation_history)
        total_collateral_lost = sum(
            record["initial_collateral"] - record["final_collateral"] 
            for record in self.liquidation_history
        )
        
        avg_size = sum(record["position_value"] for record in self.liquidation_history) / total_liquidations
        
        return {
            "total_liquidations": total_liquidations,
            "total_liquidation_fees": float(total_fees),
            "total_collateral_lost": float(total_collateral_lost),
            "average_liquidation_size": float(avg_size)
        }
    
    def get_user_liquidation_risk(self, user_id: str, market_data: MarketData) -> Optional[Dict]:
        """Get liquidation risk analysis for a specific user."""
        user = self.position_manager.get_user(user_id)
        if not user:
            return None
        
        position = user.get_position("BTC/USD")
        if not position:
            return {
                "user_id": user_id,
                "has_position": False,
                "risk_level": "none"
            }
        
        risk_analysis = self._analyze_position_liquidation_risk(position, market_data)
        
        # Determine risk level
        margin_ratio = risk_analysis["margin_ratio"]
        if margin_ratio < Decimal('1.1'):
            risk_level = "critical"
        elif margin_ratio < Decimal('1.5'):
            risk_level = "high"
        elif margin_ratio < Decimal('2.0'):
            risk_level = "medium"
        else:
            risk_level = "low"
        
        risk_analysis["risk_level"] = risk_level
        risk_analysis["user_id"] = user_id
        risk_analysis["has_position"] = True
        
        return risk_analysis
    
    def get_all_liquidation_risks(self, market_data: MarketData) -> Dict[str, Dict]:
        """Get liquidation risk analysis for all users."""
        risks = {}
        
        for user_id in self.position_manager.users.keys():
            risk = self.get_user_liquidation_risk(user_id, market_data)
            if risk:
                risks[user_id] = risk
        
        return risks
    
    def calculate_optimal_position_size(
        self, 
        user_collateral: Decimal, 
        entry_price: Decimal, 
        leverage: int,
        risk_tolerance: Decimal = Decimal('0.8')  # 80% of liquidation threshold
    ) -> Decimal:
        """Calculate optimal position size to avoid liquidation."""
        # Calculate maximum position value that keeps margin ratio above risk_tolerance
        # maintenance_margin = position_value * 0.05
        # equity = collateral + unrealized_pnl
        # We want: equity / maintenance_margin >= risk_tolerance
        
        # For a new position: equity = collateral (no unrealized PNL)
        # So: collateral / (position_value * 0.05) >= risk_tolerance
        # position_value <= collateral / (0.05 * risk_tolerance)
        
        max_position_value = user_collateral / (Decimal('0.05') * risk_tolerance)
        max_quantity = max_position_value / entry_price
        
        return max_quantity
    
    def reset_liquidation_history(self) -> None:
        """Reset liquidation history."""
        self.liquidation_history = []
