"""
Efficient Order Book implementation using priority queues for price levels.
"""
import heapq
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from collections import defaultdict

from src.models.data_models import Order, OrderSide, Trade


class PriceLevel:
    """Represents a price level in the order book."""
    
    def __init__(self, price: Decimal):
        self.price = price
        self.orders: List[Order] = []
        self.total_quantity = Decimal('0')
    
    def add_order(self, order: Order) -> None:
        """Add an order to this price level."""
        self.orders.append(order)
        self.total_quantity += order.remaining_quantity
    
    def remove_order(self, order: Order) -> None:
        """Remove an order from this price level."""
        if order in self.orders:
            self.orders.remove(order)
            self.total_quantity -= order.remaining_quantity
    
    def update_order(self, order: Order) -> None:
        """Update an order's filled quantity."""
        # Recalculate total quantity
        self.total_quantity = sum(o.remaining_quantity for o in self.orders)
    
    def get_orders(self) -> List[Order]:
        """Get all orders at this price level."""
        return self.orders.copy()
    
    def is_empty(self) -> bool:
        """Check if this price level is empty."""
        return len(self.orders) == 0


class OrderBook:
    """Efficient order book implementation with O(log n) operations."""
    
    def __init__(self):
        # Price levels for buy orders (max heap - highest price first)
        self.buy_levels: Dict[Decimal, PriceLevel] = {}
        self.buy_prices: List[Tuple[Decimal, Decimal]] = []  # (-price, price) for max heap
        
        # Price levels for sell orders (min heap - lowest price first)
        self.sell_levels: Dict[Decimal, PriceLevel] = {}
        self.sell_prices: List[Tuple[Decimal, Decimal]] = []  # (price, price) for min heap
        
        # Order lookup for O(1) access
        self.orders: Dict[str, Order] = {}
        
        # Track best bid/ask
        self.best_bid: Optional[Decimal] = None
        self.best_ask: Optional[Decimal] = None
    
    def add_order(self, order: Order) -> List[Trade]:
        """Add an order to the book and return any trades executed."""
        trades = []
        
        # Store order for lookup
        self.orders[order.id] = order
        
        if order.side == OrderSide.BUY:
            trades = self._match_buy_order(order)
            if order.remaining_quantity > Decimal('0'):
                self._add_buy_order(order)
        else:
            trades = self._match_sell_order(order)
            if order.remaining_quantity > Decimal('0'):
                self._add_sell_order(order)
        
        self._update_best_prices()
        return trades
    
    def _match_buy_order(self, buy_order: Order) -> List[Trade]:
        """Match a buy order against sell orders."""
        trades = []
        
        while (buy_order.remaining_quantity > Decimal('0') and 
               self.sell_prices and 
               self.sell_prices[0][1] <= buy_order.price):
            
            best_ask_price = self.sell_prices[0][1]
            sell_level = self.sell_levels[best_ask_price]
            
            if sell_level.is_empty():
                heapq.heappop(self.sell_prices)
                continue
            
            # Get the first sell order (FIFO)
            sell_order = sell_level.orders[0]
            
            # Calculate trade quantity
            trade_quantity = min(buy_order.remaining_quantity, sell_order.remaining_quantity)
            
            # Execute trade
            trade = Trade(
                buy_order_id=buy_order.id,
                sell_order_id=sell_order.id,
                quantity=trade_quantity,
                price=best_ask_price
            )
            trades.append(trade)
            
            # Update order quantities
            buy_order.filled_quantity += trade_quantity
            sell_order.filled_quantity += trade_quantity
            
            # Update order status
            if buy_order.is_filled:
                buy_order.status = "filled"
            elif buy_order.is_partially_filled:
                buy_order.status = "partially_filled"
            
            if sell_order.is_filled:
                sell_order.status = "filled"
                sell_level.remove_order(sell_order)
                if sell_level.is_empty():
                    heapq.heappop(self.sell_prices)
                    del self.sell_levels[best_ask_price]
            elif sell_order.is_partially_filled:
                sell_order.status = "partially_filled"
                sell_level.update_order(sell_order)
        
        return trades
    
    def _match_sell_order(self, sell_order: Order) -> List[Trade]:
        """Match a sell order against buy orders."""
        trades = []
        
        while (sell_order.remaining_quantity > Decimal('0') and 
               self.buy_prices and 
               self.buy_prices[0][1] >= sell_order.price):
            
            best_bid_price = self.buy_prices[0][1]
            buy_level = self.buy_levels[best_bid_price]
            
            if buy_level.is_empty():
                heapq.heappop(self.buy_prices)
                continue
            
            # Get the first buy order (FIFO)
            buy_order = buy_level.orders[0]
            
            # Calculate trade quantity
            trade_quantity = min(sell_order.remaining_quantity, buy_order.remaining_quantity)
            
            # Execute trade
            trade = Trade(
                buy_order_id=buy_order.id,
                sell_order_id=sell_order.id,
                quantity=trade_quantity,
                price=best_bid_price
            )
            trades.append(trade)
            
            # Update order quantities
            sell_order.filled_quantity += trade_quantity
            buy_order.filled_quantity += trade_quantity
            
            # Update order status
            if sell_order.is_filled:
                sell_order.status = "filled"
            elif sell_order.is_partially_filled:
                sell_order.status = "partially_filled"
            
            if buy_order.is_filled:
                buy_order.status = "filled"
                buy_level.remove_order(buy_order)
                if buy_level.is_empty():
                    heapq.heappop(self.buy_prices)
                    del self.buy_levels[best_bid_price]
            elif buy_order.is_partially_filled:
                buy_order.status = "partially_filled"
                buy_level.update_order(buy_order)
        
        return trades
    
    def _add_buy_order(self, order: Order) -> None:
        """Add a buy order to the book."""
        price = order.price
        
        if price not in self.buy_levels:
            self.buy_levels[price] = PriceLevel(price)
            heapq.heappush(self.buy_prices, (-price, price))  # Negative for max heap
        
        self.buy_levels[price].add_order(order)
    
    def _add_sell_order(self, order: Order) -> None:
        """Add a sell order to the book."""
        price = order.price
        
        if price not in self.sell_levels:
            self.sell_levels[price] = PriceLevel(price)
            heapq.heappush(self.sell_prices, (price, price))  # Min heap
        
        self.sell_levels[price].add_order(order)
    
    def _update_best_prices(self) -> None:
        """Update best bid and ask prices."""
        self.best_bid = None
        self.best_ask = None
        
        if self.buy_prices:
            self.best_bid = self.buy_prices[0][1]
        
        if self.sell_prices:
            self.best_ask = self.sell_prices[0][1]
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.status in ["filled", "cancelled"]:
            return False
        
        order.status = "cancelled"
        
        if order.side == OrderSide.BUY:
            price = order.price
            if price in self.buy_levels:
                self.buy_levels[price].remove_order(order)
                if self.buy_levels[price].is_empty():
                    del self.buy_levels[price]
                    # Remove from heap
                    self.buy_prices = [(p, p) for p, _ in self.buy_prices if p != -price]
                    heapq.heapify(self.buy_prices)
        else:
            price = order.price
            if price in self.sell_levels:
                self.sell_levels[price].remove_order(order)
                if self.sell_levels[price].is_empty():
                    del self.sell_levels[price]
                    # Remove from heap
                    self.sell_prices = [(p, p) for p, _ in self.sell_prices if p != price]
                    heapq.heapify(self.sell_prices)
        
        del self.orders[order_id]
        self._update_best_prices()
        return True
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by ID."""
        return self.orders.get(order_id)
    
    def get_best_bid(self) -> Optional[Decimal]:
        """Get the best bid price."""
        return self.best_bid
    
    def get_best_ask(self) -> Optional[Decimal]:
        """Get the best ask price."""
        return self.best_ask
    
    def get_spread(self) -> Optional[Decimal]:
        """Get the bid-ask spread."""
        if self.best_bid and self.best_ask:
            return self.best_ask - self.best_bid
        return None
    
    def get_market_depth(self, levels: int = 5) -> Dict[str, List[Tuple[Decimal, Decimal]]]:
        """Get market depth for both sides."""
        buy_depth = []
        sell_depth = []
        
        # Get buy side (highest prices first)
        buy_prices_copy = self.buy_prices.copy()
        for _ in range(min(levels, len(buy_prices_copy))):
            if not buy_prices_copy:
                break
            price = heapq.heappop(buy_prices_copy)[1]
            if price in self.buy_levels:
                quantity = self.buy_levels[price].total_quantity
                buy_depth.append((price, quantity))
        
        # Get sell side (lowest prices first)
        sell_prices_copy = self.sell_prices.copy()
        for _ in range(min(levels, len(sell_prices_copy))):
            if not sell_prices_copy:
                break
            price = heapq.heappop(sell_prices_copy)[1]
            if price in self.sell_levels:
                quantity = self.sell_levels[price].total_quantity
                sell_depth.append((price, quantity))
        
        return {
            "bids": buy_depth,
            "asks": sell_depth
        }
    
    def get_total_volume(self) -> Decimal:
        """Get total volume in the order book."""
        total = Decimal('0')
        for level in self.buy_levels.values():
            total += level.total_quantity
        for level in self.sell_levels.values():
            total += level.total_quantity
        return total
