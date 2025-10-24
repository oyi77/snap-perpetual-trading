"""
Order placement and matching engine with partial fills support.
"""
from typing import List, Optional, Dict
from decimal import Decimal
from datetime import datetime

from src.models.data_models import Order, OrderSide, OrderType, User
from src.engine.order_book import OrderBook
from src.engine.position_manager import PositionManager


class OrderMatchingEngine:
    """Handles order placement, matching, and execution."""
    
    def __init__(self, position_manager: PositionManager, logger=None):
        self.order_book = OrderBook()
        self.position_manager = position_manager
        self.logger = logger  # Add logger reference
        self.trade_history: List[Dict] = []
        self.order_history: List[Order] = []
    
    def place_order(self, order: Order, current_hour: int = 0) -> Dict:
        """Place an order and return execution results."""
        # Validate order
        validation_result = self._validate_order(order)
        if not validation_result["valid"]:
            return validation_result
        
        # Check margin requirements
        margin_check = self._check_margin_requirements(order)
        if not margin_check["valid"]:
            return margin_check
        
        # Add order to history
        self.order_history.append(order)
        
        # Place order in order book and get trades
        trades = self.order_book.add_order(order)
        
        # Process trades
        execution_result = self._process_trades(trades, current_hour)
        
        # Update order status
        if order.is_filled:
            order.status = "filled"
        elif order.is_partially_filled:
            order.status = "partially_filled"
        
        return {
            "valid": True,
            "order_id": order.id,
            "status": order.status,
            "trades": execution_result["trades"],
            "message": f"Order placed successfully. {len(trades)} trades executed."
        }
    
    def _validate_order(self, order: Order) -> Dict:
        """Validate an order before placement."""
        if order.quantity <= Decimal('0'):
            return {
                "valid": False,
                "message": "Order quantity must be greater than 0"
            }
        
        if order.price <= Decimal('0'):
            return {
                "valid": False,
                "message": "Order price must be greater than 0"
            }
        
        if order.leverage < 1 or order.leverage > 10:
            return {
                "valid": False,
                "message": "Leverage must be between 1 and 10"
            }
        
        if order.side not in [OrderSide.BUY, OrderSide.SELL]:
            return {
                "valid": False,
                "message": "Invalid order side"
            }
        
        if order.order_type not in [OrderType.LIMIT, OrderType.MARKET]:
            return {
                "valid": False,
                "message": "Invalid order type"
            }
        
        return {"valid": True}
    
    def _check_margin_requirements(self, order: Order) -> Dict:
        """Check if user has sufficient margin for the order."""
        user = self.position_manager.get_user(order.user_id)
        if not user:
            return {
                "valid": False,
                "message": f"User {order.user_id} not found"
            }
        
        # Calculate required margin
        position_value = order.quantity * order.price
        required_margin = position_value / Decimal(str(order.leverage))
        
        # Check if user has sufficient collateral
        if user.collateral < required_margin:
            return {
                "valid": False,
                "message": f"Insufficient margin. Required: {required_margin}, Available: {user.collateral}"
            }
        
        return {"valid": True}
    
    def _process_trades(self, trades: List, current_hour: int = 0) -> Dict:
        """Process executed trades and update positions."""
        processed_trades = []
        
        for trade in trades:
            # Get orders involved in the trade
            buy_order = self.order_book.get_order(trade.buy_order_id)
            sell_order = self.order_book.get_order(trade.sell_order_id)
            
            if not buy_order or not sell_order:
                continue
            
            # Process trade in position manager
            self.position_manager.process_trade(trade, buy_order, sell_order)
            
            # Record trade
            trade_record = {
                "trade_id": trade.id,
                "buy_order_id": trade.buy_order_id,
                "sell_order_id": trade.sell_order_id,
                "buyer": buy_order.user_id,
                "seller": sell_order.user_id,
                "quantity": float(trade.quantity),
                "price": float(trade.price),
                "timestamp": trade.timestamp.isoformat()
            }
            
            processed_trades.append(trade_record)
            self.trade_history.append(trade_record)
            
            # Log trade execution if logger is available
            if self.logger:
                # Convert orders to dict format for logging
                buy_order_dict = {
                    "user_id": buy_order.user_id,
                    "side": buy_order.side.value,
                    "quantity": float(buy_order.quantity),
                    "price": float(buy_order.price),
                    "leverage": buy_order.leverage
                }
                sell_order_dict = {
                    "user_id": sell_order.user_id,
                    "side": sell_order.side.value,
                    "quantity": float(sell_order.quantity),
                    "price": float(sell_order.price),
                    "leverage": sell_order.leverage
                }
                trade_dict = {
                    "trade_id": trade.id,
                    "quantity": float(trade.quantity),
                    "price": float(trade.price),
                    "timestamp": trade.timestamp.isoformat()
                }
                
                self.logger.log_trade_execution(current_hour, trade_dict, buy_order_dict, sell_order_dict)
        
        return {"trades": processed_trades}
    
    def cancel_order(self, order_id: str, user_id: str) -> Dict:
        """Cancel an order."""
        order = self.order_book.get_order(order_id)
        
        if not order:
            return {
                "valid": False,
                "message": f"Order {order_id} not found"
            }
        
        if order.user_id != user_id:
            return {
                "valid": False,
                "message": "Unauthorized to cancel this order"
            }
        
        if order.status in ["filled", "cancelled"]:
            return {
                "valid": False,
                "message": f"Cannot cancel order with status: {order.status}"
            }
        
        success = self.order_book.cancel_order(order_id)
        
        if success:
            order.status = "cancelled"
            return {
                "valid": True,
                "message": f"Order {order_id} cancelled successfully"
            }
        else:
            return {
                "valid": False,
                "message": f"Failed to cancel order {order_id}"
            }
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get the status of an order."""
        order = self.order_book.get_order(order_id)
        
        if not order:
            return None
        
        return {
            "order_id": order.id,
            "user_id": order.user_id,
            "side": order.side.value,
            "order_type": order.order_type.value,
            "quantity": float(order.quantity),
            "price": float(order.price),
            "leverage": order.leverage,
            "filled_quantity": float(order.filled_quantity),
            "remaining_quantity": float(order.remaining_quantity),
            "status": order.status,
            "timestamp": order.timestamp.isoformat()
        }
    
    def get_user_orders(self, user_id: str) -> List[Dict]:
        """Get all orders for a user."""
        user_orders = []
        
        for order in self.order_history:
            if order.user_id == user_id:
                user_orders.append(self.get_order_status(order.id))
        
        return user_orders
    
    def get_market_depth(self, levels: int = 5) -> Dict:
        """Get market depth."""
        return self.order_book.get_market_depth(levels)
    
    def get_best_prices(self) -> Dict:
        """Get best bid and ask prices."""
        return {
            "best_bid": float(self.order_book.get_best_bid()) if self.order_book.get_best_bid() else None,
            "best_ask": float(self.order_book.get_best_ask()) if self.order_book.get_best_ask() else None,
            "spread": float(self.order_book.get_spread()) if self.order_book.get_spread() else None
        }
    
    def get_trade_history(self, limit: int = 100) -> List[Dict]:
        """Get recent trade history."""
        return self.trade_history[-limit:] if limit else self.trade_history
    
    def get_order_book_summary(self) -> Dict:
        """Get order book summary."""
        depth = self.get_market_depth(10)
        best_prices = self.get_best_prices()
        
        return {
            "best_prices": best_prices,
            "market_depth": depth,
            "total_volume": float(self.order_book.get_total_volume()),
            "total_orders": len(self.order_book.orders)
        }
    
    def simulate_market_order(
        self, 
        user_id: str, 
        side: OrderSide, 
        quantity: Decimal, 
        leverage: int = 1
    ) -> Dict:
        """Simulate a market order by placing at best available price."""
        best_prices = self.get_best_prices()
        
        if side == OrderSide.BUY:
            if not best_prices["best_ask"]:
                return {
                    "valid": False,
                    "message": "No sell orders available for market buy"
                }
            price = Decimal(str(best_prices["best_ask"]))
        else:
            if not best_prices["best_bid"]:
                return {
                    "valid": False,
                    "message": "No buy orders available for market sell"
                }
            price = Decimal(str(best_prices["best_bid"]))
        
        # Create market order
        order = Order(
            user_id=user_id,
            side=side,
            order_type=OrderType.LIMIT,  # Place as limit at market price
            quantity=quantity,
            price=price,
            leverage=leverage
        )
        
        return self.place_order(order)
    
    def get_execution_statistics(self) -> Dict:
        """Get execution statistics."""
        total_trades = len(self.trade_history)
        total_volume = sum(trade["quantity"] * trade["price"] for trade in self.trade_history)
        
        # Calculate average trade size
        avg_trade_size = total_volume / total_trades if total_trades > 0 else 0
        
        # Count filled vs partially filled orders
        filled_orders = sum(1 for order in self.order_history if order.status == "filled")
        partial_orders = sum(1 for order in self.order_history if order.status == "partially_filled")
        
        return {
            "total_trades": total_trades,
            "total_volume": float(total_volume),
            "average_trade_size": float(avg_trade_size),
            "filled_orders": filled_orders,
            "partially_filled_orders": partial_orders,
            "total_orders": len(self.order_history)
        }
