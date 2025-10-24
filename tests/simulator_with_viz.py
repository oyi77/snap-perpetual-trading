#!/usr/bin/env python3
"""
Enhanced simulator with live visualization capabilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulator import TradingSimulator
from visualization_tools import LiveTradingVisualizer, create_comprehensive_analysis
import matplotlib.pyplot as plt
import argparse

def run_simulation_with_live_viz(hours=24, config_file=None, save_charts=True):
    """Run simulation with live visualization."""
    
    print("🚀 Starting Trading Simulation with Live Visualization")
    print("=" * 60)
    
    # Get the project root directory (parent of tests)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(project_root, "logs")
    
    # Create simulator with correct logs directory
    simulator = TradingSimulator(logs_dir)
    
    # Load configuration
    if config_file:
        result = simulator.load_simulation_config(config_file)
        if not result["success"]:
            print(f"❌ Error loading config: {result['message']}")
            return
    else:
        # Use default configuration
        config_path = "../configs/sample_config.json"
        if os.path.exists(config_path):
            result = simulator.load_simulation_config(config_path)
        else:
            # Fallback to creating sample config
            from main import ConfigManager
            config = ConfigManager.create_sample_config()
            # Save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                import json
                json.dump(config, f)
                config_file = f.name
            
            result = simulator.load_simulation_config(config_file)
            os.unlink(config_file)  # Clean up temp file
    
    # Add random events
    simulator.add_random_events(20, hours)
    
    # Create visualizer
    visualizer = LiveTradingVisualizer(max_points=hours + 10)
    
    print("📊 Starting live visualization...")
    visualizer.start_animation()
    
    try:
        # Run simulation with live updates
        print(f"⏱️  Running simulation for {hours} hours...")
        
        # Override the simulator's run method to include live updates
        original_run = simulator.run_simulation
        
        def run_with_viz(hours_param):
            # Run the original simulation
            results = original_run(hours_param)
            
            # Extract data for visualization
            price_history = []
            user_history = {}
            
            # Process simulation log for visualization data
            for log_entry in simulator.simulation_log:
                if log_entry.get('event_type') == 'price_update':
                    hour = log_entry.get('hour', 0)
                    price = log_entry.get('data', {}).get('new_price', 0)
                    price_history.append((hour, price))
                
                elif log_entry.get('event_type') == 'hourly_summary':
                    hour = log_entry.get('hour', 0)
                    summary = log_entry.get('data', {})
                    user_summaries = summary.get('user_summaries', {})
                    
                    for user_id, user_data in user_summaries.items():
                        if user_id not in user_history:
                            user_history[user_id] = []
                        user_history[user_id].append((hour, user_data))
            
            # Update visualizer with all data
            for hour, price in price_history:
                user_data = {}
                for user_id, history in user_history.items():
                    # Find data for this hour
                    for h, data in history:
                        if h == hour:
                            user_data[user_id] = data
                            break
                
                visualizer.update_data(hour, price, user_data)
            
            return results
        
        # Replace the run method temporarily
        simulator.run_simulation = run_with_viz
        
        # Run simulation
        results = simulator.run_simulation(hours)
        
        print("✅ Simulation completed!")
        
        # Save final chart
        if save_charts:
            # Save final chart to session output directory
            session_id = simulator.logger.get_session_id()
            # Get the project root directory (parent of tests)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(project_root, f"output/session_{session_id}")
            os.makedirs(output_dir, exist_ok=True)
            chart_filename = os.path.join(output_dir, f"live_simulation_{hours}h.png")
            
            visualizer.save_final_chart(chart_filename)
        
        # Stop animation
        visualizer.stop_animation()
        
        # Create comprehensive analysis
        if save_charts:
            print("📊 Creating comprehensive analysis...")
            # Save results first to session output directory
            import json
            session_id = simulator.logger.get_session_id()
            # Get the project root directory (parent of tests)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(project_root, f"output/session_{session_id}")
            os.makedirs(output_dir, exist_ok=True)
            results_file = os.path.join(output_dir, f"simulation_results_{hours}h.json")
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            # Create analysis charts
            create_comprehensive_analysis(results_file, session_id)
        
        return results
        
    except KeyboardInterrupt:
        print("\n⏹️  Simulation interrupted by user")
        visualizer.stop_animation()
        return None
    except Exception as e:
        print(f"❌ Error during simulation: {str(e)}")
        visualizer.stop_animation()
        return None

def run_analysis_only(results_file):
    """Run analysis on existing results file."""
    print(f"📊 Analyzing results from: {results_file}")
    
    try:
        create_comprehensive_analysis(results_file)
        print("✅ Analysis completed!")
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Trading Simulator with Live Visualization")
    parser.add_argument("--hours", type=int, default=24, help="Simulation hours")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--analyze", help="Analyze existing results file")
    parser.add_argument("--no-charts", action="store_true", help="Don't save charts")
    
    args = parser.parse_args()
    
    if args.analyze:
        run_analysis_only(args.analyze)
    else:
        results = run_simulation_with_live_viz(
            hours=args.hours,
            config_file=args.config,
            save_charts=not args.no_charts
        )
        
        if results:
            print("\n📋 SIMULATION SUMMARY:")
            summary = results["simulation_summary"]
            print(f"   Duration: {summary['total_hours']} hours")
            print(f"   Final Price: ${summary['final_price']:,.2f}")
            print(f"   Price Change: {summary['price_change_percent']:.2f}%")
            print(f"   Total Trades: {summary['total_trades']}")
            print(f"   Total Volume: ${summary['total_volume']:,.2f}")
            print(f"   Liquidations: {summary['total_liquidations']}")
            
            print("\n👥 FINAL USER BALANCES:")
            for user_id, balance in results["final_user_balances"].items():
                print(f"   {user_id}: ${balance['total_equity']:,.2f}")

if __name__ == "__main__":
    main()
