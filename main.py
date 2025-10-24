"""
JSON input/output system for configuration and results.
"""
import json
import argparse
from typing import Dict, List, Any
from decimal import Decimal
from datetime import datetime
import sqlite3
import os

from src.simulator import TradingSimulator
from src.engine.price_oracle import PriceDataGenerator


class ConfigManager:
    """Manages simulation configuration and data generation."""
    
    @staticmethod
    def create_sample_config() -> Dict:
        """Create a sample configuration file."""
        # Generate price series
        price_oracle = PriceDataGenerator()
        prices = price_oracle.generate_volatile_prices(
            initial_price=Decimal('60000'),
            hours=48,
            volatility=0.03
        )
        
        config = {
            "users": [
                {"id": "user1", "collateral": 10000},
                {"id": "user2", "collateral": 5000},
                {"id": "user3", "collateral": 15000}
            ],
            "prices": [float(price) for price in prices],
            "events": [
                {
                    "time": 0,
                    "action": "place_order",
                    "data": {
                        "user": "user1",
                        "side": "buy",
                        "quantity": 0.5,
                        "price": 59500,
                        "leverage": 5
                    }
                },
                {
                    "time": 1,
                    "action": "place_order",
                    "data": {
                        "user": "user2",
                        "side": "sell",
                        "quantity": 0.3,
                        "price": 60500,
                        "leverage": 3
                    }
                },
                {
                    "time": 8,
                    "action": "apply_funding"
                },
                {
                    "time": 16,
                    "action": "apply_funding"
                },
                {
                    "time": 24,
                    "action": "place_order",
                    "data": {
                        "user": "user3",
                        "side": "buy",
                        "quantity": 1.0,
                        "price": 58000,
                        "leverage": 10
                    }
                },
                {
                    "time": 32,
                    "action": "apply_funding"
                },
                {
                    "time": 40,
                    "action": "apply_funding"
                }
            ]
        }
        
        return config
    
    @staticmethod
    def create_crash_scenario_config() -> Dict:
        """Create a configuration with a market crash scenario."""
        prices = PriceDataGenerator.generate_crash_scenario(
            initial_price=Decimal('60000'),
            hours=48,
            crash_hour=24,
            crash_percent=0.3
        )
        
        config = {
            "users": [
                {"id": "trader1", "collateral": 20000},
                {"id": "trader2", "collateral": 10000},
                {"id": "trader3", "collateral": 5000}
            ],
            "prices": [float(price) for price in prices],
            "events": [
                {
                    "time": 0,
                    "action": "place_order",
                    "data": {
                        "user": "trader1",
                        "side": "buy",
                        "quantity": 2.0,
                        "price": 60000,
                        "leverage": 10
                    }
                },
                {
                    "time": 5,
                    "action": "place_order",
                    "data": {
                        "user": "trader2",
                        "side": "buy",
                        "quantity": 1.5,
                        "price": 61000,
                        "leverage": 8
                    }
                },
                {
                    "time": 10,
                    "action": "place_order",
                    "data": {
                        "user": "trader3",
                        "side": "buy",
                        "quantity": 1.0,
                        "price": 62000,
                        "leverage": 10
                    }
                },
                {
                    "time": 8,
                    "action": "apply_funding"
                },
                {
                    "time": 16,
                    "action": "apply_funding"
                },
                {
                    "time": 24,
                    "action": "apply_funding"
                },
                {
                    "time": 32,
                    "action": "apply_funding"
                },
                {
                    "time": 40,
                    "action": "apply_funding"
                }
            ]
        }
        
        return config
    
    @staticmethod
    def create_pump_scenario_config() -> Dict:
        """Create a configuration with a market pump scenario."""
        prices = PriceDataGenerator.generate_pump_scenario(
            initial_price=Decimal('60000'),
            hours=48,
            pump_hour=12,
            pump_percent=0.2
        )
        
        config = {
            "users": [
                {"id": "bull1", "collateral": 15000},
                {"id": "bear1", "collateral": 12000},
                {"id": "neutral1", "collateral": 8000}
            ],
            "prices": [float(price) for price in prices],
            "events": [
                {
                    "time": 0,
                    "action": "place_order",
                    "data": {
                        "user": "bull1",
                        "side": "buy",
                        "quantity": 1.5,
                        "price": 60000,
                        "leverage": 5
                    }
                },
                {
                    "time": 2,
                    "action": "place_order",
                    "data": {
                        "user": "bear1",
                        "side": "sell",
                        "quantity": 1.0,
                        "price": 61000,
                        "leverage": 6
                    }
                },
                {
                    "time": 4,
                    "action": "place_order",
                    "data": {
                        "user": "neutral1",
                        "side": "buy",
                        "quantity": 0.8,
                        "price": 60500,
                        "leverage": 4
                    }
                },
                {
                    "time": 8,
                    "action": "apply_funding"
                },
                {
                    "time": 16,
                    "action": "apply_funding"
                },
                {
                    "time": 24,
                    "action": "apply_funding"
                },
                {
                    "time": 32,
                    "action": "apply_funding"
                },
                {
                    "time": 40,
                    "action": "apply_funding"
                }
            ]
        }
        
        return config
    
    @staticmethod
    def save_config(config: Dict, filename: str) -> Dict:
        """Save configuration to JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            
            return {"success": True, "message": f"Configuration saved to {filename}"}
            
        except Exception as e:
            return {"success": False, "message": f"Error saving config: {str(e)}"}
    
    @staticmethod
    def load_config(filename: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            
            return {"success": True, "config": config}
            
        except Exception as e:
            return {"success": False, "message": f"Error loading config: {str(e)}"}


class ResultsExporter:
    """Exports simulation results in various formats."""
    
    @staticmethod
    def clean_for_json(obj, max_depth=30, current_depth=0):
        """Clean object for JSON serialization, handling circular references."""
        if current_depth > max_depth:
            return "[Max depth reached]"
        
        if isinstance(obj, dict):
            cleaned_dict = {}
            for k, v in obj.items():
                try:
                    cleaned_dict[str(k)] = ResultsExporter.clean_for_json(v, max_depth, current_depth + 1)
                except:
                    cleaned_dict[str(k)] = str(v)
            return cleaned_dict
        elif isinstance(obj, list):
            # Limit list size to prevent huge arrays
            limited_list = obj[:200] if len(obj) > 200 else obj
            return [ResultsExporter.clean_for_json(item, max_depth, current_depth + 1) 
                   for item in limited_list]
        elif hasattr(obj, '__dict__'):
            # Convert objects to dict representation, but be more careful
            try:
                obj_dict = {}
                for attr_name, attr_value in obj.__dict__.items():
                    if not attr_name.startswith('_'):  # Skip private attributes
                        obj_dict[attr_name] = ResultsExporter.clean_for_json(attr_value, max_depth, current_depth + 1)
                return obj_dict
            except:
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
        elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Decimal':
            # Handle Decimal objects
            try:
                return float(obj)
            except:
                return str(obj)
        else:
            # For other types, try to convert to string
            try:
                return str(obj)
            except:
                return "[Unserializable object]"
    
    @staticmethod
    def export_flattened_json(results: Dict, filename: str) -> Dict:
        """Export results in a flattened JSON structure to avoid depth issues."""
        try:
            # Extract and flatten the data
            flattened_results = {
                "simulation_summary": results["simulation_summary"],
                "execution_statistics": results["execution_statistics"],
                "funding_statistics": results["funding_statistics"],
                "liquidation_statistics": results["liquidation_statistics"],
                "price_statistics": results["price_statistics"],
                "final_user_balances": results["final_user_balances"],
                "trade_history": ResultsExporter._extract_trade_history(results),
                "price_history": ResultsExporter._extract_price_history(results),
                "funding_events": ResultsExporter._extract_funding_events(results),
                "liquidation_events": ResultsExporter._extract_liquidation_events(results),
                "user_position_history": ResultsExporter._extract_user_position_history(results)
            }
            
            with open(filename, 'w') as f:
                json.dump(flattened_results, f, indent=2, default=str)
            
            # Also save detailed logs separately
            log_filename = filename.replace('.json', '_detailed_logs.json')
            ResultsExporter._save_detailed_logs(results, log_filename)
            
            return {"success": True, "message": f"Flattened results exported to {filename}, detailed logs to {log_filename}"}
            
        except Exception as e:
            return {"success": False, "message": f"Error exporting flattened results: {str(e)}"}
    
    @staticmethod
    def _save_detailed_logs(results: Dict, filename: str) -> None:
        """Save detailed simulation logs separately."""
        try:
            # Create a simplified version of the simulation log
            simplified_logs = []
            
            for log_entry in results.get("simulation_log", []):
                simplified_entry = {
                    "timestamp": log_entry.get("timestamp", ""),
                    "hour": log_entry.get("hour", 0),
                    "event_type": log_entry.get("event_type", ""),
                    "data_summary": ResultsExporter._create_log_summary(log_entry.get("data", {}))
                }
                simplified_logs.append(simplified_entry)
            
            detailed_logs = {
                "simulation_log": simplified_logs,
                "metadata": {
                    "total_log_entries": len(results.get("simulation_log", [])),
                    "export_timestamp": datetime.now().isoformat(),
                    "note": "Simplified simulation logs - complex nested data converted to summaries"
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(detailed_logs, f, indent=2, default=str)
                
        except Exception as e:
            # If detailed logs fail, create a simple summary
            try:
                simple_logs = {
                    "simulation_log_summary": {
                        "total_entries": len(results.get("simulation_log", [])),
                        "event_types": list(set(log.get("event_type", "unknown") for log in results.get("simulation_log", []))),
                        "note": f"Detailed logs could not be exported: {str(e)}"
                    },
                    "metadata": {
                        "export_timestamp": datetime.now().isoformat()
                    }
                }
                
                with open(filename, 'w') as f:
                    json.dump(simple_logs, f, indent=2, default=str)
            except:
                pass  # If even the summary fails, just skip it
    
    @staticmethod
    def _create_log_summary(data: Dict) -> Dict:
        """Create a summary of log data to avoid depth issues."""
        summary = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Create a simple summary of nested data
                summary[key] = {
                    "type": "object",
                    "keys": list(value.keys()),
                    "summary": str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                }
            elif isinstance(value, list):
                summary[key] = {
                    "type": "list",
                    "length": len(value),
                    "summary": f"List with {len(value)} items"
                }
            else:
                summary[key] = value
        
        return summary
    
    @staticmethod
    def _extract_trade_history(results: Dict) -> List[Dict]:
        """Extract trade history from simulation log."""
        trades = []
        for log_entry in results.get("simulation_log", []):
            if log_entry.get("event_type") == "order_placed":
                event_data = log_entry.get("data", {})
                result_data = event_data.get("result", {})
                if result_data.get("valid") and "trades" in result_data:
                    for trade in result_data["trades"]:
                        trades.append({
                            "timestamp": log_entry.get("timestamp", ""),
                            "hour": log_entry.get("hour", 0),
                            "buyer": trade.get("buyer", ""),
                            "seller": trade.get("seller", ""),
                            "quantity": trade.get("quantity", 0),
                            "price": trade.get("price", 0)
                        })
            elif log_entry.get("event_type") == "random_order":
                # Also check random orders for trades
                event_data = log_entry.get("data", {})
                result_data = event_data.get("result", {})
                if result_data.get("valid") and "trades" in result_data:
                    for trade in result_data["trades"]:
                        trades.append({
                            "timestamp": log_entry.get("timestamp", ""),
                            "hour": log_entry.get("hour", 0),
                            "buyer": trade.get("buyer", ""),
                            "seller": trade.get("seller", ""),
                            "quantity": trade.get("quantity", 0),
                            "price": trade.get("price", 0)
                        })
        return trades
    
    @staticmethod
    def _extract_price_history(results: Dict) -> List[Dict]:
        """Extract price history from simulation log."""
        prices = []
        for log_entry in results.get("simulation_log", []):
            if log_entry.get("event_type") == "price_update":
                data = log_entry.get("data", {})
                prices.append({
                    "timestamp": log_entry.get("timestamp", ""),
                    "hour": log_entry.get("hour", 0),
                    "price": data.get("new_price", 0)
                })
        return prices
    
    @staticmethod
    def _extract_funding_events(results: Dict) -> List[Dict]:
        """Extract funding events from simulation log."""
        funding_events = []
        for log_entry in results.get("simulation_log", []):
            if log_entry.get("event_type") == "funding_applied":
                data = log_entry.get("data", {})
                funding_events.append({
                    "timestamp": log_entry.get("timestamp", ""),
                    "hour": log_entry.get("hour", 0),
                    "applied": data.get("applied", False),
                    "funding_rate": data.get("funding_rate", 0),
                    "total_funding_paid": data.get("total_funding_paid", 0)
                })
        return funding_events
    
    @staticmethod
    def _extract_liquidation_events(results: Dict) -> List[Dict]:
        """Extract liquidation events from simulation log."""
        liquidations = []
        for log_entry in results.get("simulation_log", []):
            if log_entry.get("event_type") == "hourly_summary":
                data = log_entry.get("data", {})
                if data.get("liquidations", 0) > 0:
                    liquidations.append({
                        "timestamp": log_entry.get("timestamp", ""),
                        "hour": log_entry.get("hour", 0),
                        "liquidations_count": data.get("liquidations", 0)
                    })
        return liquidations
    
    @staticmethod
    def _extract_user_position_history(results: Dict) -> List[Dict]:
        """Extract user position history from simulation log."""
        position_history = []
        for log_entry in results.get("simulation_log", []):
            if log_entry.get("event_type") == "hourly_summary":
                data = log_entry.get("data", {})
                user_summaries = data.get("user_summaries", {})
                for user_id, summary in user_summaries.items():
                    if summary and summary.get("has_position"):
                        position_history.append({
                            "timestamp": log_entry.get("timestamp", ""),
                            "hour": log_entry.get("hour", 0),
                            "user_id": user_id,
                            "collateral": summary.get("collateral", 0),
                            "realized_pnl": summary.get("realized_pnl", 0),
                            "unrealized_pnl": summary.get("unrealized_pnl", 0),
                            "total_equity": summary.get("total_equity", 0),
                            "position_side": summary.get("position_side", ""),
                            "position_quantity": summary.get("position_quantity", 0),
                            "entry_price": summary.get("entry_price", 0),
                            "leverage": summary.get("leverage", 1),
                            "margin_ratio": summary.get("margin_ratio", 0),
                            "is_liquidatable": summary.get("is_liquidatable", False)
                        })
        return position_history
    
    @staticmethod
    def export_to_sqlite(results: Dict, filename: str) -> Dict:
        """Export results to SQLite database for advanced analysis."""
        try:
            # Remove existing database if it exists
            if os.path.exists(filename):
                os.remove(filename)
            
            conn = sqlite3.connect(filename)
            cursor = conn.cursor()
            
            # Create tables
            ResultsExporter._create_sqlite_tables(cursor)
            
            # Insert data
            ResultsExporter._insert_simulation_data(cursor, results)
            ResultsExporter._insert_trade_data(cursor, results)
            ResultsExporter._insert_price_data(cursor, results)
            ResultsExporter._insert_funding_data(cursor, results)
            ResultsExporter._insert_user_data(cursor, results)
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": f"SQLite database exported to {filename}"}
            
        except Exception as e:
            return {"success": False, "message": f"Error exporting to SQLite: {str(e)}"}
    
    @staticmethod
    def _create_sqlite_tables(cursor):
        """Create SQLite tables for simulation data."""
        # Simulation summary table
        cursor.execute('''
            CREATE TABLE simulation_summary (
                id INTEGER PRIMARY KEY,
                total_hours INTEGER,
                final_price REAL,
                price_change_percent REAL,
                total_trades INTEGER,
                total_volume REAL,
                total_funding_paid REAL,
                total_liquidations INTEGER
            )
        ''')
        
        # Trades table
        cursor.execute('''
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                hour INTEGER,
                buyer TEXT,
                seller TEXT,
                quantity REAL,
                price REAL,
                trade_value REAL
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE price_history (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                hour INTEGER,
                price REAL
            )
        ''')
        
        # Funding events table
        cursor.execute('''
            CREATE TABLE funding_events (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                hour INTEGER,
                applied BOOLEAN,
                funding_rate REAL,
                total_funding_paid REAL
            )
        ''')
        
        # User positions table
        cursor.execute('''
            CREATE TABLE user_positions (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                hour INTEGER,
                user_id TEXT,
                collateral REAL,
                realized_pnl REAL,
                unrealized_pnl REAL,
                total_equity REAL,
                position_side TEXT,
                position_quantity REAL,
                entry_price REAL,
                leverage INTEGER,
                margin_ratio REAL,
                is_liquidatable BOOLEAN
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX idx_trades_hour ON trades(hour)')
        cursor.execute('CREATE INDEX idx_trades_buyer ON trades(buyer)')
        cursor.execute('CREATE INDEX idx_trades_seller ON trades(seller)')
        cursor.execute('CREATE INDEX idx_price_hour ON price_history(hour)')
        cursor.execute('CREATE INDEX idx_funding_hour ON funding_events(hour)')
        cursor.execute('CREATE INDEX idx_positions_user ON user_positions(user_id)')
        cursor.execute('CREATE INDEX idx_positions_hour ON user_positions(hour)')
    
    @staticmethod
    def _insert_simulation_data(cursor, results):
        """Insert simulation summary data."""
        summary = results["simulation_summary"]
        cursor.execute('''
            INSERT INTO simulation_summary 
            (total_hours, final_price, price_change_percent, total_trades, 
             total_volume, total_funding_paid, total_liquidations)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            summary["total_hours"],
            summary["final_price"],
            summary["price_change_percent"],
            summary["total_trades"],
            summary["total_volume"],
            summary["total_funding_paid"],
            summary["total_liquidations"]
        ))
    
    @staticmethod
    def _insert_trade_data(cursor, results):
        """Insert trade data."""
        trades = ResultsExporter._extract_trade_history(results)
        for trade in trades:
            cursor.execute('''
                INSERT INTO trades 
                (timestamp, hour, buyer, seller, quantity, price, trade_value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade["timestamp"],
                trade["hour"],
                trade["buyer"],
                trade["seller"],
                trade["quantity"],
                trade["price"],
                trade["quantity"] * trade["price"]
            ))
    
    @staticmethod
    def _insert_price_data(cursor, results):
        """Insert price history data."""
        prices = ResultsExporter._extract_price_history(results)
        for price in prices:
            cursor.execute('''
                INSERT INTO price_history (timestamp, hour, price)
                VALUES (?, ?, ?)
            ''', (price["timestamp"], price["hour"], price["price"]))
    
    @staticmethod
    def _insert_funding_data(cursor, results):
        """Insert funding events data."""
        funding_events = ResultsExporter._extract_funding_events(results)
        for event in funding_events:
            cursor.execute('''
                INSERT INTO funding_events 
                (timestamp, hour, applied, funding_rate, total_funding_paid)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                event["timestamp"],
                event["hour"],
                event["applied"],
                event["funding_rate"],
                event["total_funding_paid"]
            ))
    
    @staticmethod
    def _insert_user_data(cursor, results):
        """Insert user position data."""
        positions = ResultsExporter._extract_user_position_history(results)
        for pos in positions:
            cursor.execute('''
                INSERT INTO user_positions 
                (timestamp, hour, user_id, collateral, realized_pnl, unrealized_pnl,
                 total_equity, position_side, position_quantity, entry_price,
                 leverage, margin_ratio, is_liquidatable)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pos["timestamp"], pos["hour"], pos["user_id"], pos["collateral"],
                pos["realized_pnl"], pos["unrealized_pnl"], pos["total_equity"],
                pos["position_side"], pos["position_quantity"], pos["entry_price"],
                pos["leverage"], pos["margin_ratio"], pos["is_liquidatable"]
            ))
    
    @staticmethod
    def export_to_json(results: Dict, filename: str) -> Dict:
        """Export results to JSON file using the cleaned approach."""
        try:
            # Clean the results for JSON export
            cleaned_results = ResultsExporter.clean_for_json(results)
            
            with open(filename, 'w') as f:
                json.dump(cleaned_results, f, indent=2, default=str)
            
            return {"success": True, "message": f"Results exported to {filename}"}
            
        except Exception as e:
            return {"success": False, "message": f"Error exporting results: {str(e)}"}
    
    @staticmethod
    def export_summary_report(results: Dict, filename: str) -> Dict:
        """Export a summary report to text file."""
        try:
            summary = results["simulation_summary"]
            exec_stats = results["execution_statistics"]
            funding_stats = results["funding_statistics"]
            liquidation_stats = results["liquidation_statistics"]
            price_stats = results["price_statistics"]
            
            report = f"""
PERPETUAL FUTURES TRADING SIMULATION REPORT
==========================================

Simulation Summary:
- Total Hours: {summary['total_hours']}
- Final Price: ${summary['final_price']:,.2f}
- Price Change: {summary['price_change_percent']:.2f}%
- Total Trades: {summary['total_trades']}
- Total Volume: ${summary['total_volume']:,.2f}
- Total Funding Paid: ${summary['total_funding_paid']:,.2f}
- Total Liquidations: {summary['total_liquidations']}

Execution Statistics:
- Average Trade Size: ${exec_stats['average_trade_size']:,.2f}
- Filled Orders: {exec_stats['filled_orders']}
- Partially Filled Orders: {exec_stats['partially_filled_orders']}

Funding Statistics:
- Total Funding Events: {funding_stats['total_funding_events']}
- Average Funding Rate: {funding_stats['average_funding_rate']:.6f}
- Max Funding Rate: {funding_stats['max_funding_rate']:.6f}
- Min Funding Rate: {funding_stats['min_funding_rate']:.6f}

Liquidation Statistics:
- Total Liquidations: {liquidation_stats['total_liquidations']}
- Total Liquidation Fees: ${liquidation_stats['total_liquidation_fees']:,.2f}
- Total Collateral Lost: ${liquidation_stats['total_collateral_lost']:,.2f}
- Average Liquidation Size: ${liquidation_stats['average_liquidation_size']:,.2f}

Price Statistics:
- Volatility: {price_stats.get('volatility', 0):.4f}
- Min Price: ${price_stats.get('min_price', 0):,.2f}
- Max Price: ${price_stats.get('max_price', 0):,.2f}
- Data Points: {price_stats.get('data_points', 0)}

Final User Balances:
"""
            
            for user_id, balance in results["final_user_balances"].items():
                report += f"""
{user_id}:
  Collateral: ${balance['collateral']:,.2f}
  Realized PNL: ${balance['realized_pnl']:,.2f}
  Unrealized PNL: ${balance['unrealized_pnl']:,.2f}
  Total Equity: ${balance['total_equity']:,.2f}
  Has Position: {balance['has_position']}
"""
            
            with open(filename, 'w') as f:
                f.write(report)
            
            return {"success": True, "message": f"Summary report exported to {filename}"}
            
        except Exception as e:
            return {"success": False, "message": f"Error exporting report: {str(e)}"}
    
    @staticmethod
    def export_trade_history(results: Dict, filename: str) -> Dict:
        """Export trade history to CSV file."""
        try:
            import csv
            
            # Extract trade history from simulation log
            trades = []
            for log_entry in results["simulation_log"]:
                if log_entry["event_type"] == "order_placed" and log_entry["data"]["result"]["valid"]:
                    for trade in log_entry["data"]["result"]["trades"]:
                        trades.append({
                            "timestamp": log_entry["timestamp"],
                            "hour": log_entry["hour"],
                            "buyer": trade["buyer"],
                            "seller": trade["seller"],
                            "quantity": trade["quantity"],
                            "price": trade["price"]
                        })
            
            with open(filename, 'w', newline='') as f:
                if trades:
                    writer = csv.DictWriter(f, fieldnames=trades[0].keys())
                    writer.writeheader()
                    writer.writerows(trades)
            
            return {"success": True, "message": f"Trade history exported to {filename}"}
            
        except Exception as e:
            return {"success": False, "message": f"Error exporting trade history: {str(e)}"}


def main():
    """Main entry point for the trading simulator."""
    parser = argparse.ArgumentParser(description="Perpetual Futures Trading Simulator")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--hours", type=int, default=48, help="Simulation hours")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", choices=["json", "flattened", "sqlite"], 
                       default="flattened", help="Export format (default: flattened)")
    parser.add_argument("--scenario", "-s", choices=["sample", "crash", "pump"], 
                       help="Generate sample scenario")
    parser.add_argument("--generate-config", "-g", help="Generate config file")
    
    args = parser.parse_args()
    
    # Generate configuration if requested
    if args.generate_config:
        if args.scenario == "sample":
            config = ConfigManager.create_sample_config()
        elif args.scenario == "crash":
            config = ConfigManager.create_crash_scenario_config()
        elif args.scenario == "pump":
            config = ConfigManager.create_pump_scenario_config()
        else:
            config = ConfigManager.create_sample_config()
        
        result = ConfigManager.save_config(config, args.generate_config)
        print(result["message"])
        return
    
    # Load configuration
    if args.config:
        config_result = ConfigManager.load_config(args.config)
        if not config_result["success"]:
            print(f"Error loading config: {config_result['message']}")
            return
        config = config_result["config"]
    else:
        # Use default configuration
        config = ConfigManager.create_sample_config()
    
    # Create and run simulator with logs in project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(project_root, "logs")
    simulator = TradingSimulator(logs_dir)
    
    # Load configuration
    load_result = simulator.load_simulation_config(args.config or "default_config.json")
    if not load_result["success"]:
        print(f"Error loading simulation config: {load_result['message']}")
        return
    
    # Add some random events for more realistic simulation (after users are loaded)
    simulator.add_random_events(20, args.hours)
    
    # Run simulation
    print(f"Starting simulation for {args.hours} hours...")
    results = simulator.run_simulation(args.hours)
    
    # Print results
    print(f"Simulation completed successfully!")
    
    # Print key statistics
    summary = results["simulation_summary"]
    print(f"\nKey Statistics:")
    print(f"- Final Price: ${summary['final_price']:,.2f}")
    print(f"- Price Change: {summary['price_change_percent']:.2f}%")
    print(f"- Total Trades: {summary['total_trades']}")
    print(f"- Total Volume: ${summary['total_volume']:,.2f}")
    print(f"- Total Liquidations: {summary['total_liquidations']}")
    
    # Print user balances
    print(f"\nFinal User Balances:")
    for user_id, balance in results["final_user_balances"].items():
        print(f"- {user_id}: ${balance['total_equity']:,.2f}")
    
        # Print logging information
        session_id = simulator.logger.get_session_id()
        session_dir = f"logs/session_{session_id}"
        print(f"\n📋 Detailed Logs Saved:")
        print(f"- Session ID: {session_id}")
        print(f"- Session directory: {session_dir}/")
        print(f"- Main log file: {session_dir}/simulation.log")
        print(f"- Detailed logs: {session_dir}/detailed_logs.json")
        print(f"- Trade logs: {session_dir}/trade_logs.json")
        print(f"- Funding logs: {session_dir}/funding_logs.json")
        print(f"- Liquidation logs: {session_dir}/liquidation_logs.json")
        print(f"- Price logs: {session_dir}/price_logs.json")
        print(f"- Order logs: {session_dir}/order_logs.json")
    
    # Create output directory for this session
    session_id = simulator.logger.get_session_id()
    output_dir = os.path.join(project_root, f"output/session_{session_id}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Try to save results if output file specified
    if args.output:
        # Save to session-specific output directory
        output_filename = os.path.join(output_dir, args.output)
        export_result = None
        
        if args.format == "flattened":
            export_result = ResultsExporter.export_flattened_json(results, output_filename)
        elif args.format == "sqlite":
            export_result = ResultsExporter.export_to_sqlite(results, output_filename)
        else:  # json format
            export_result = ResultsExporter.export_to_json(results, output_filename)
        
        if export_result["success"]:
            print(f"\n{export_result['message']}")
            print(f"📁 Results saved to: {output_dir}/")
        else:
            print(f"\nExport failed: {export_result['message']}")
            # Try to save just the summary as fallback
            try:
                summary_only = {
                    "simulation_summary": results["simulation_summary"],
                    "execution_statistics": results["execution_statistics"],
                    "final_user_balances": results["final_user_balances"]
                }
                fallback_file = args.output.replace('.json', '_summary.json').replace('.db', '_summary.json')
                with open(fallback_file, 'w') as f:
                    json.dump(summary_only, f, indent=2, default=str)
                print(f"Summary saved to: {fallback_file}")
            except Exception as e2:
                print(f"Could not save summary either: {e2}")
    else:
        # Save default results to session directory
        default_output = os.path.join(output_dir, "simulation_results.json")
        export_result = ResultsExporter.export_flattened_json(results, default_output)
        if export_result and export_result["success"]:
            print(f"\n📁 Results saved to: {output_dir}/simulation_results.json")
        else:
            print(f"\nError saving default results: {export_result['message'] if export_result else 'Unknown error'}")


if __name__ == "__main__":
    main()
