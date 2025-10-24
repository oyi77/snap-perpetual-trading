"""
Position management and PNL calculation system.
"""
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime

from src.models.data_models import (
    User, Position, PositionSide, Order, OrderSide, Trade, MarketData
)


class PositionManager:
    """Manages user positions and PNL calculations."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.market_data: Optional[MarketData] = None
    
    def add_user(self, user: User) -> None:
        """Add a user to the position manager."""
        self.users[user.id] = user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return self.users.get(user_id)
    
    def update_market_data(self, market_data: MarketData) -> None:
        """Update market data for PNL calculations."""
        self.market_data = market_data
        self._update_all_unrealized_pnl()
    
    def process_trade(self, trade: Trade, buy_order: Order, sell_order: Order) -> None:
        """Process a trade and update positions."""
        buy_user = self.users.get(buy_order.user_id)
        sell_user = self.users.get(sell_order.user_id)
        
        if not buy_user or not sell_user:
            return
        
        # Process buy side
        self._process_trade_for_user(
            buy_user, trade, buy_order, PositionSide.LONG
        )
        
        # Process sell side
        self._process_trade_for_user(
            sell_user, trade, sell_order, PositionSide.SHORT
        )
    
    def _process_trade_for_user(
        self, 
        user: User, 
        trade: Trade, 
        order: Order, 
        side: PositionSide
    ) -> None:
        """Process a trade for a specific user."""
        symbol = "BTC/USD"  # Default symbol
        current_position = user.get_position(symbol)
        
        if current_position is None:
            # Create new position
            required_collateral = self._calculate_required_collateral(
                trade.quantity, trade.price, order.leverage
            )
            
            # Deduct collateral from user
            user.collateral -= required_collateral
            
            position = Position(
                user_id=user.id,
                side=side,
                quantity=trade.quantity,
                entry_price=trade.price,
                leverage=order.leverage,
                collateral=required_collateral
            )
            user.add_position(position, symbol)
        else:
            # Update existing position
            if current_position.side == side:
                # Same side - increase position
                self._increase_position(current_position, trade, order)
            else:
                # Opposite side - reduce or close position
                self._reduce_position(current_position, trade, order)
    
    def _calculate_required_collateral(
        self, 
        quantity: Decimal, 
        price: Decimal, 
        leverage: int
    ) -> Decimal:
        """Calculate required collateral for a position."""
        position_value = quantity * price
        return position_value / Decimal(str(leverage))
    
    def _increase_position(
        self, 
        position: Position, 
        trade: Trade, 
        order: Order
    ) -> None:
        """Increase an existing position."""
        # Calculate weighted average entry price
        old_value = position.quantity * position.entry_price
        new_value = trade.quantity * trade.price
        total_quantity = position.quantity + trade.quantity
        
        if total_quantity > Decimal('0'):
            position.entry_price = (old_value + new_value) / total_quantity
        
        # Update quantity and collateral
        position.quantity = total_quantity
        additional_collateral = self._calculate_required_collateral(
            trade.quantity, trade.price, order.leverage
        )
        position.collateral += additional_collateral
        
        # Update leverage (use the higher leverage)
        position.leverage = max(position.leverage, order.leverage)
    
    def _reduce_position(
        self, 
        position: Position, 
        trade: Trade, 
        order: Order
    ) -> None:
        """Reduce an existing position."""
        if trade.quantity >= position.quantity:
            # Close position completely
            self._close_position(position, trade)
        else:
            # Partial close
            self._partial_close_position(position, trade)
    
    def _close_position(self, position: Position, trade: Trade) -> None:
        """Close a position completely."""
        # Calculate realized PNL
        if position.side == PositionSide.LONG:
            realized_pnl = (trade.price - position.entry_price) * position.quantity
        else:
            realized_pnl = (position.entry_price - trade.price) * position.quantity
        
        # Update user's realized PNL
        user = self.users[position.user_id]
        user.total_realized_pnl += realized_pnl
        
        # Return collateral to user
        user.collateral += position.collateral
        
        # Remove position
        user.remove_position("BTC/USD")
    
    def _partial_close_position(self, position: Position, trade: Trade) -> None:
        """Partially close a position."""
        # Calculate realized PNL for closed portion
        if position.side == PositionSide.LONG:
            realized_pnl = (trade.price - position.entry_price) * trade.quantity
        else:
            realized_pnl = (position.entry_price - trade.price) * trade.quantity
        
        # Update user's realized PNL
        user = self.users[position.user_id]
        user.total_realized_pnl += realized_pnl
        
        # Calculate collateral to return
        collateral_ratio = trade.quantity / position.quantity
        returned_collateral = position.collateral * collateral_ratio
        
        # Update position
        position.quantity -= trade.quantity
        position.collateral -= returned_collateral
        
        # Return collateral to user
        user.collateral += returned_collateral
    
    def _update_all_unrealized_pnl(self) -> None:
        """Update unrealized PNL for all positions."""
        if not self.market_data:
            return
        
        current_price = self.market_data.mark_price
        
        for user in self.users.values():
            position = user.get_position("BTC/USD")
            if position:
                self._update_position_pnl(position, current_price)
    
    def _update_position_pnl(self, position: Position, current_price: Decimal) -> None:
        """Update PNL for a specific position."""
        if position.side == PositionSide.LONG:
            position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
        else:
            position.unrealized_pnl = (position.entry_price - current_price) * position.quantity
    
    def get_liquidatable_positions(self) -> List[Position]:
        """Get all positions that can be liquidated."""
        liquidatable = []
        
        for user in self.users.values():
            position = user.get_position("BTC/USD")
            if position and position.is_liquidatable:
                liquidatable.append(position)
        
        return liquidatable
    
    def liquidate_position(self, position: Position) -> Decimal:
        """Liquidate a position and return liquidation fee."""
        user = self.users[position.user_id]
        
        if not self.market_data:
            return Decimal('0')
        
        # Calculate liquidation price (current mark price)
        liquidation_price = self.market_data.mark_price
        
        # Calculate realized PNL
        if position.side == PositionSide.LONG:
            realized_pnl = (liquidation_price - position.entry_price) * position.quantity
        else:
            realized_pnl = (position.entry_price - liquidation_price) * position.quantity
        
        # Calculate liquidation fee (1% of position value)
        position_value = position.quantity * liquidation_price
        liquidation_fee = position_value * Decimal('0.01')
        
        # Update user's realized PNL
        user.total_realized_pnl += realized_pnl
        
        # Return remaining collateral after liquidation fee
        remaining_collateral = position.collateral + realized_pnl - liquidation_fee
        user.collateral += max(Decimal('0'), remaining_collateral)
        
        # Remove position
        user.remove_position("BTC/USD")
        
        return liquidation_fee
    
    def apply_funding(self) -> Dict[str, Decimal]:
        """Apply funding rates to all positions."""
        if not self.market_data or self.market_data.funding_rate == Decimal('0'):
            return {}
        
        funding_payments = {}
        
        for user in self.users.values():
            position = user.get_position("BTC/USD")
            if position:
                funding_payment = self._calculate_funding_payment(position)
                position.funding_paid += funding_payment
                user.collateral -= funding_payment
                funding_payments[user.id] = funding_payment
        
        return funding_payments
    
    def _calculate_funding_payment(self, position: Position) -> Decimal:
        """Calculate funding payment for a position."""
        if not self.market_data:
            return Decimal('0')
        
        position_value = position.quantity * self.market_data.mark_price
        funding_rate = self.market_data.funding_rate
        
        if position.side == PositionSide.LONG:
            # Long positions pay funding when rate is positive
            return position_value * funding_rate
        else:
            # Short positions pay funding when rate is negative
            return position_value * (-funding_rate)
    
    def get_liquidatable_positions(self) -> List[Position]:
        """Get all positions that can be liquidated."""
        liquidatable = []
        
        for user in self.users.values():
            position = user.get_position("BTC/USD")
            if position and position.is_liquidatable:
                liquidatable.append(position)
        
        return liquidatable
    
    def apply_funding(self) -> Dict[str, Decimal]:
        """Apply funding rates to all positions."""
        if not self.market_data or self.market_data.funding_rate == Decimal('0'):
            return {}
        
        funding_payments = {}
        
        for user in self.users.values():
            position = user.get_position("BTC/USD")
            if position:
                funding_payment = self._calculate_funding_payment(position)
                position.funding_paid += funding_payment
                user.collateral -= funding_payment
                funding_payments[user.id] = funding_payment
        
        return funding_payments
    
    def _calculate_funding_payment(self, position: Position) -> Decimal:
        """Calculate funding payment for a position."""
        if not self.market_data:
            return Decimal('0')
        
        position_value = position.quantity * self.market_data.mark_price
        funding_rate = self.market_data.funding_rate
        
        if position.side.value == "long":
            # Long positions pay funding when rate is positive
            return position_value * funding_rate
        else:
            # Short positions pay funding when rate is negative
            return position_value * (-funding_rate)
    
    def get_user_summary(self, user_id: str) -> Optional[Dict]:
        """Get a summary of a user's account."""
        user = self.users.get(user_id)
        if not user:
            return None
        
        position = user.get_position("BTC/USD")
        
        summary = {
            "user_id": user_id,
            "collateral": float(user.collateral),
            "total_realized_pnl": float(user.total_realized_pnl),
            "has_position": position is not None,
            "total_equity": float(user.collateral + user.total_realized_pnl)
        }
        
        if position:
            summary.update({
                "position_side": position.side.value,
                "position_quantity": float(position.quantity),
                "entry_price": float(position.entry_price),
                "leverage": position.leverage,
                "unrealized_pnl": float(position.unrealized_pnl),
                "funding_paid": float(position.funding_paid),
                "margin_ratio": float(position.margin_ratio),
                "is_liquidatable": position.is_liquidatable
            })
        
        return summary
    
    def get_all_user_summaries(self) -> Dict[str, Dict]:
        """Get summaries for all users."""
        return {
            user_id: self.get_user_summary(user_id)
            for user_id in self.users.keys()
        }
