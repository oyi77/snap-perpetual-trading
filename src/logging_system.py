"""
Comprehensive logging system for the trading simulator.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal
import logging


class TradingLogger:
    """Comprehensive logging system for trading simulator."""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = logs_dir
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create session-specific directory
        self.session_dir = os.path.join(logs_dir, f"session_{self.session_id}")
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Setup file logging
        self._setup_file_logging()
        
        # Detailed event logs
        self.detailed_logs: List[Dict] = []
        self.trade_logs: List[Dict] = []
        self.funding_logs: List[Dict] = []
        self.liquidation_logs: List[Dict] = []
        self.price_logs: List[Dict] = []
        self.order_logs: List[Dict] = []
        
    def _setup_file_logging(self):
        """Setup file-based logging in session directory."""
        # Create session-specific log file
        log_filename = os.path.join(self.session_dir, "simulation.log")
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Trading simulation started - Session ID: {self.session_id}")
        self.logger.info(f"Session directory: {self.session_dir}")
    
    def log_simulation_start(self, config: Dict):
        """Log simulation start with configuration."""
        self.logger.info("=" * 80)
        self.logger.info("SIMULATION STARTED")
        self.logger.info("=" * 80)
        self.logger.info(f"Session ID: {self.session_id}")
        self.logger.info(f"Configuration: {json.dumps(config, indent=2, default=str)}")
        
        # Add to detailed logs
        self.detailed_logs.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": "simulation_start",
            "session_id": self.session_id,
            "config": config
        })
    
    def log_price_update(self, hour: int, old_price: Decimal, new_price: Decimal, 
                        price_change: Decimal, price_change_percent: float):
        """Log price updates with detailed information."""
        self.logger.info(f"Hour {hour}: Price updated from ${old_price} to ${new_price} "
                        f"(Change: ${price_change:.2f}, {price_change_percent:.2f}%)")
        
        # Add to detailed logs
        self.detailed_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "event_type": "price_update",
            "old_price": float(old_price),
            "new_price": float(new_price),
            "price_change": float(price_change),
            "price_change_percent": price_change_percent
        })
        
        # Add to price logs
        self.price_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "price": float(new_price),
            "change": float(price_change),
            "change_percent": price_change_percent
        })
    
    def log_order_placed(self, hour: int, event: Dict, result: Dict):
        """Log order placement with full details."""
        order_info = f"User: {event.get('user', 'unknown')}, Side: {event.get('side', 'unknown')}, "
        order_info += f"Quantity: {event.get('quantity', 0)}, Price: ${event.get('price', 0)}, "
        order_info += f"Leverage: {event.get('leverage', 1)}x"
        
        status = "SUCCESS" if result.get("valid", False) else "FAILED"
        self.logger.info(f"Hour {hour}: Order placed - {order_info} - {status}")
        
        if not result.get("valid", False):
            self.logger.warning(f"Order failed: {result.get('message', 'Unknown error')}")
        
        # Add to detailed logs
        self.detailed_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "event_type": "order_placed",
            "event": event,
            "result": result
        })
        
        # Add to order logs
        self.order_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "order_event": event,
            "order_result": result,
            "success": result.get("valid", False)
        })
    
    def log_random_order(self, hour: int, order: Dict, result: Dict):
        """Log random order generation."""
        order_info = f"User: {order.get('user_id', 'unknown')}, Side: {order.get('side', 'unknown')}, "
        order_info += f"Quantity: {order.get('quantity', 0):.4f}, Price: ${order.get('price', 0):.2f}, "
        order_info += f"Leverage: {order.get('leverage', 1)}x"
        
        status = "SUCCESS" if result.get("valid", False) else "FAILED"
        self.logger.info(f"Hour {hour}: Random order - {order_info} - {status}")
        
        if not result.get("valid", False):
            self.logger.warning(f"Random order failed: {result.get('message', 'Unknown error')}")
        
        # Add to detailed logs
        self.detailed_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "event_type": "random_order",
            "order": order,
            "result": result
        })
        
        # Add to order logs
        self.order_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "order_event": order,
            "order_result": result,
            "success": result.get("valid", False),
            "is_random": True
        })
    
    def log_trade_execution(self, hour: int, trade: Dict, buy_order: Dict, sell_order: Dict):
        """Log trade execution with full details."""
        trade_info = f"Trade executed: {trade.get('quantity', 0):.4f} BTC at ${trade.get('price', 0):.2f}"
        trade_info += f" - Buyer: {buy_order.get('user_id', 'unknown')}, Seller: {sell_order.get('user_id', 'unknown')}"
        
        self.logger.info(f"Hour {hour}: {trade_info}")
        
        # Add to detailed logs
        self.detailed_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "event_type": "trade_execution",
            "trade": trade,
            "buy_order": buy_order,
            "sell_order": sell_order
        })
        
        # Add to trade logs
        self.trade_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "trade": trade,
            "buy_order": buy_order,
            "sell_order": sell_order
        })
    
    def log_funding_applied(self, hour: int, funding_result: Dict):
        """Log funding application."""
        if funding_result.get("applied", False):
            rate = funding_result.get("funding_rate", 0)
            total_paid = funding_result.get("total_funding_paid", 0)
            payments = funding_result.get("funding_payments", {})
            
            self.logger.info(f"Hour {hour}: Funding applied - Rate: {rate:.6f}, Total paid: ${total_paid:.2f}")
            
            for user_id, payment in payments.items():
                if payment != 0:
                    self.logger.info(f"  User {user_id}: ${payment:.2f}")
        else:
            self.logger.info(f"Hour {hour}: Funding not applied - {funding_result.get('message', 'Not due yet')}")
        
        # Add to detailed logs
        self.detailed_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "event_type": "funding_applied",
            "funding_result": funding_result
        })
        
        # Add to funding logs
        self.funding_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "funding_result": funding_result
        })
    
    def log_liquidation(self, hour: int, liquidation_result: Dict):
        """Log liquidation events."""
        if liquidation_result.get("liquidated", False):
            user_id = liquidation_result.get("user_id", "unknown")
            position_size = liquidation_result.get("position_size", 0)
            liquidation_price = liquidation_result.get("liquidation_price", 0)
            fee = liquidation_result.get("liquidation_fee", 0)
            
            self.logger.warning(f"Hour {hour}: LIQUIDATION - User {user_id} liquidated!")
            self.logger.warning(f"  Position size: {position_size:.4f} BTC at ${liquidation_price:.2f}")
            self.logger.warning(f"  Liquidation fee: ${fee:.2f}")
        else:
            self.logger.info(f"Hour {hour}: No liquidations")
        
        # Add to detailed logs
        self.detailed_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "event_type": "liquidation_check",
            "liquidation_result": liquidation_result
        })
        
        # Add to liquidation logs
        self.liquidation_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "liquidation_result": liquidation_result
        })
    
    def log_position_update(self, hour: int, user_id: str, position: Dict):
        """Log position updates."""
        side = position.get("side", "unknown")
        quantity = position.get("quantity", 0)
        entry_price = position.get("entry_price", 0)
        unrealized_pnl = position.get("unrealized_pnl", 0)
        equity = position.get("equity", 0)
        
        self.logger.info(f"Hour {hour}: Position update - User {user_id}")
        self.logger.info(f"  {side.upper()}: {quantity:.4f} BTC @ ${entry_price:.2f}")
        self.logger.info(f"  Unrealized PNL: ${unrealized_pnl:.2f}, Equity: ${equity:.2f}")
        
        # Add to detailed logs
        self.detailed_logs.append({
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "event_type": "position_update",
            "user_id": user_id,
            "position": position
        })
    
    def log_simulation_end(self, results: Dict):
        """Log simulation end with summary."""
        self.logger.info("=" * 80)
        self.logger.info("SIMULATION COMPLETED")
        self.logger.info("=" * 80)
        
        summary = results.get("simulation_summary", {})
        self.logger.info(f"Total hours: {summary.get('total_hours', 0)}")
        self.logger.info(f"Final price: ${summary.get('final_price', 0):.2f}")
        self.logger.info(f"Price change: {summary.get('price_change_percent', 0):.2f}%")
        self.logger.info(f"Total trades: {summary.get('total_trades', 0)}")
        self.logger.info(f"Total volume: ${summary.get('total_volume', 0):.2f}")
        self.logger.info(f"Total liquidations: {summary.get('total_liquidations', 0)}")
        
        # Log final user balances
        balances = results.get("final_user_balances", {})
        self.logger.info("Final user balances:")
        for user_id, balance_info in balances.items():
            collateral = balance_info.get("collateral", 0)
            realized_pnl = balance_info.get("realized_pnl", 0)
            unrealized_pnl = balance_info.get("unrealized_pnl", 0)
            self.logger.info(f"  {user_id}: Collateral=${collateral:.2f}, "
                           f"Realized PNL=${realized_pnl:.2f}, Unrealized PNL=${unrealized_pnl:.2f}")
        
        # Add to detailed logs
        self.detailed_logs.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": "simulation_end",
            "results": results
        })
    
    def save_detailed_logs(self):
        """Save all detailed logs to JSON files."""
        # Clean the logs to avoid circular references
        cleaned_detailed_logs = self._clean_logs_for_json(self.detailed_logs)
        cleaned_trade_logs = self._clean_logs_for_json(self.trade_logs)
        cleaned_funding_logs = self._clean_logs_for_json(self.funding_logs)
        cleaned_liquidation_logs = self._clean_logs_for_json(self.liquidation_logs)
        cleaned_price_logs = self._clean_logs_for_json(self.price_logs)
        cleaned_order_logs = self._clean_logs_for_json(self.order_logs)
        
        # Save comprehensive detailed logs
        detailed_logs_file = os.path.join(self.session_dir, "detailed_logs.json")
        with open(detailed_logs_file, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "total_events": len(cleaned_detailed_logs),
                "events": cleaned_detailed_logs
            }, f, indent=2, default=str)
        
        # Save trade logs
        trade_logs_file = os.path.join(self.session_dir, "trade_logs.json")
        with open(trade_logs_file, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "total_trades": len(cleaned_trade_logs),
                "trades": cleaned_trade_logs
            }, f, indent=2, default=str)
        
        # Save funding logs
        funding_logs_file = os.path.join(self.session_dir, "funding_logs.json")
        with open(funding_logs_file, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "total_funding_events": len(cleaned_funding_logs),
                "funding_events": cleaned_funding_logs
            }, f, indent=2, default=str)
        
        # Save liquidation logs
        liquidation_logs_file = os.path.join(self.session_dir, "liquidation_logs.json")
        with open(liquidation_logs_file, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "total_liquidation_events": len(cleaned_liquidation_logs),
                "liquidation_events": cleaned_liquidation_logs
            }, f, indent=2, default=str)
        
        # Save price logs
        price_logs_file = os.path.join(self.session_dir, "price_logs.json")
        with open(price_logs_file, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "total_price_updates": len(cleaned_price_logs),
                "price_updates": cleaned_price_logs
            }, f, indent=2, default=str)
        
        # Save order logs
        order_logs_file = os.path.join(self.session_dir, "order_logs.json")
        with open(order_logs_file, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "total_orders": len(cleaned_order_logs),
                "orders": cleaned_order_logs
            }, f, indent=2, default=str)
        
        self.logger.info(f"Detailed logs saved to session directory: {self.session_dir}/")
        self.logger.info(f"  - Main log: simulation.log")
        self.logger.info(f"  - Detailed logs: detailed_logs.json")
        self.logger.info(f"  - Trade logs: trade_logs.json")
        self.logger.info(f"  - Funding logs: funding_logs.json")
        self.logger.info(f"  - Liquidation logs: liquidation_logs.json")
        self.logger.info(f"  - Price logs: price_logs.json")
        self.logger.info(f"  - Order logs: order_logs.json")
    
    def _clean_logs_for_json(self, logs: List[Dict], max_depth: int = 10, current_depth: int = 0) -> List[Dict]:
        """Clean logs for JSON serialization, handling circular references."""
        if current_depth > max_depth:
            return [{"error": "Max depth reached", "type": "truncated"}]
        
        cleaned_logs = []
        for log_entry in logs:
            try:
                cleaned_entry = self._clean_object_for_json(log_entry, max_depth, current_depth)
                cleaned_logs.append(cleaned_entry)
            except Exception as e:
                cleaned_logs.append({
                    "error": f"Serialization error: {str(e)}",
                    "timestamp": log_entry.get("timestamp", "unknown"),
                    "event_type": log_entry.get("event_type", "unknown")
                })
        
        return cleaned_logs
    
    def _clean_object_for_json(self, obj, max_depth: int = 10, current_depth: int = 0):
        """Clean an object for JSON serialization."""
        if current_depth > max_depth:
            return "[Max depth reached]"
        
        if isinstance(obj, dict):
            cleaned_dict = {}
            for k, v in obj.items():
                try:
                    cleaned_dict[str(k)] = self._clean_object_for_json(v, max_depth, current_depth + 1)
                except Exception:
                    cleaned_dict[str(k)] = str(v)
            return cleaned_dict
        elif isinstance(obj, list):
            # Limit list size to prevent huge arrays
            limited_list = obj[:100] if len(obj) > 100 else obj
            return [self._clean_object_for_json(item, max_depth, current_depth + 1) 
                   for item in limited_list]
        elif hasattr(obj, '__dict__'):
            # Convert objects to dict representation, but be more careful
            try:
                obj_dict = {}
                for attr_name, attr_value in obj.__dict__.items():
                    if not attr_name.startswith('_'):  # Skip private attributes
                        obj_dict[attr_name] = self._clean_object_for_json(attr_value, max_depth, current_depth + 1)
                return obj_dict
            except Exception:
                return str(obj)
        elif isinstance(obj, (str, int, float, bool, type(None))):
            # Handle special float values
            if isinstance(obj, float):
                if obj == float('inf'):
                    return "infinity"
                elif obj == float('-inf'):
                    return "-infinity"
                elif obj != obj:  # NaN check
                    return "NaN"
            return obj
        elif hasattr(obj, '__class__') and hasattr(obj, '__name__'):
            # Handle Decimal objects
            try:
                return float(obj)
            except Exception:
                return str(obj)
        else:
            # For other types, try to convert to string
            try:
                return str(obj)
            except Exception:
                return "[Unserializable object]"
    
    def get_session_id(self) -> str:
        """Get the current session ID."""
        return self.session_id
