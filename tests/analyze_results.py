#!/usr/bin/env python3
"""
Example analysis script for flattened JSON results.
Shows how to analyze trading simulation data.
"""

import json
import matplotlib.pyplot as plt
from datetime import datetime

def analyze_simulation_results(filename):
    """Analyze flattened simulation results."""
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    print("=== TRADING SIMULATION ANALYSIS ===")
    print()
    
    # Simulation Overview
    summary = data['simulation_summary']
    print(f"📊 SIMULATION OVERVIEW")
    print(f"   Duration: {summary['total_hours']} hours")
    print(f"   Final Price: ${summary['final_price']:,.2f}")
    print(f"   Price Change: {summary['price_change_percent']:.2f}%")
    print(f"   Total Trades: {summary['total_trades']}")
    print(f"   Total Volume: ${summary['total_volume']:,.2f}")
    print(f"   Liquidations: {summary['total_liquidations']}")
    print()
    
    # Price Analysis
    price_history = data['price_history']
    if price_history:
        prices = [p['price'] for p in price_history]
        print(f"📈 PRICE ANALYSIS")
        print(f"   Price Range: ${min(prices):,.2f} - ${max(prices):,.2f}")
        print(f"   Volatility: {data['price_statistics']['volatility']:.4f}")
        print(f"   Data Points: {len(price_history)}")
        print()
    
    # Trade Analysis
    trades = data['trade_history']
    if trades:
        print(f"💱 TRADE ANALYSIS")
        total_volume = sum(t['quantity'] * t['price'] for t in trades)
        avg_trade_size = total_volume / len(trades) if trades else 0
        print(f"   Total Trades: {len(trades)}")
        print(f"   Total Volume: ${total_volume:,.2f}")
        print(f"   Average Trade Size: ${avg_trade_size:,.2f}")
        print()
        
        # Show recent trades
        print("   Recent Trades:")
        for trade in trades[-3:]:  # Last 3 trades
            print(f"     {trade['buyer']} → {trade['seller']}: {trade['quantity']} @ ${trade['price']:,.2f}")
        print()
    else:
        print("💱 No trades executed (orders didn't match)")
        print()
    
    # User Analysis
    user_balances = data['final_user_balances']
    print(f"👥 USER ANALYSIS")
    for user_id, balance in user_balances.items():
        print(f"   {user_id}: ${balance['total_equity']:,.2f} (Position: {'Yes' if balance['has_position'] else 'No'})")
    print()
    
    # Funding Analysis
    funding_events = data['funding_events']
    if funding_events:
        print(f"💸 FUNDING ANALYSIS")
        total_funding = sum(f['total_funding_paid'] for f in funding_events)
        print(f"   Funding Events: {len(funding_events)}")
        print(f"   Total Funding Paid: ${total_funding:,.2f}")
        print()
    
    # Position Analysis
    positions = data['user_position_history']
    if positions:
        print(f"📊 POSITION ANALYSIS")
        print(f"   Position Snapshots: {len(positions)}")
        
        # Group by user
        user_positions = {}
        for pos in positions:
            user_id = pos['user_id']
            if user_id not in user_positions:
                user_positions[user_id] = []
            user_positions[user_id].append(pos)
        
        for user_id, user_pos_list in user_positions.items():
            latest_pos = user_pos_list[-1]  # Most recent position
            print(f"   {user_id}: {latest_pos['position_side']} {latest_pos['position_quantity']} @ ${latest_pos['entry_price']:,.2f}")
        print()
    
    return data

def create_price_chart(data, filename="price_chart.png", session_id=None):
    """Create a price chart from the data."""
    try:
        import matplotlib.pyplot as plt
        import os
        
        print(f"Creating price chart with session_id: {session_id}")
        print(f"Current working directory: {os.getcwd()}")
        
        # If session_id provided, save to session output directory
        if session_id:
            # Get the project root directory (parent of tests)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(project_root, f"output/session_{session_id}")
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.join(output_dir, filename)
            print(f"Saving chart to: {filename}")
            print(f"Absolute path: {os.path.abspath(filename)}")
        
        price_history = data['price_history']
        if not price_history:
            print("No price data to chart")
            return
        
        print(f"Found {len(price_history)} price data points")
        
        hours = [p['hour'] for p in price_history]
        prices = [p['price'] for p in price_history]
        
        plt.figure(figsize=(12, 6))
        plt.plot(hours, prices, 'b-', linewidth=2, marker='o', markersize=4)
        plt.title('BTC/USD Price Movement During Simulation')
        plt.xlabel('Hour')
        plt.ylabel('Price ($)')
        plt.grid(True, alpha=0.3)
        plt.ticklabel_format(style='plain', axis='y')
        
        # Format y-axis as currency
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Price chart saved as: {filename}")
        
    except ImportError:
        print("📊 Matplotlib not available for charting")
    except Exception as e:
        print(f"Error creating price chart: {e}")
        import traceback
        traceback.print_exc()

def create_pnl_chart(data, session_id=None, filename="pnl_chart.png"):
    """Create a PNL chart showing user performance."""
    try:
        import matplotlib.pyplot as plt
        import os
        
        print(f"Creating PNL chart with session_id: {session_id}")
        
        # If session_id provided, save to session output directory
        if session_id:
            # Get the project root directory (parent of tests)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(project_root, f"output/session_{session_id}")
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.join(output_dir, filename)
            print(f"Saving PNL chart to: {filename}")
        
        # Extract user balances
        user_balances = data['final_user_balances']
        if not user_balances:
            print("No user balance data to chart")
            return
        
        # Prepare data for charting
        users = list(user_balances.keys())
        total_equity = [user_balances[user]['total_equity'] for user in users]
        realized_pnl = [user_balances[user]['realized_pnl'] for user in users]
        unrealized_pnl = [user_balances[user]['unrealized_pnl'] for user in users]
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('User PNL Analysis', fontsize=16, fontweight='bold')
        
        # 1. Total Equity Chart
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        bars1 = ax1.bar(users, total_equity, color=colors[:len(users)], alpha=0.7)
        ax1.set_title('Final User Equity')
        ax1.set_ylabel('Total Equity ($)')
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add value labels on bars
        for bar, value in zip(bars1, total_equity):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(total_equity)*0.01,
                    f'${value:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        # 2. PNL Breakdown Chart
        x = range(len(users))
        width = 0.35
        
        bars2 = ax2.bar([i - width/2 for i in x], realized_pnl, width, label='Realized PNL', alpha=0.7, color='green')
        bars3 = ax2.bar([i + width/2 for i in x], unrealized_pnl, width, label='Unrealized PNL', alpha=0.7, color='orange')
        
        ax2.set_title('PNL Breakdown')
        ax2.set_ylabel('PNL ($)')
        ax2.set_xlabel('Users')
        ax2.set_xticks(x)
        ax2.set_xticklabels(users)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add zero line
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 PNL chart saved as: {filename}")
        
    except ImportError:
        print("📊 Matplotlib not available for PNL charting")
    except Exception as e:
        print(f"Error creating PNL chart: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    import os
    
    # Add parent directory to path for imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Check for different result files
    result_files = [
        'short_simulation_results.json',
        '24h_simulation_results.json',
        'demo_results.json',
        '../demo_results.json'
    ]

    # Also look for session results
    import glob
    session_results = glob.glob('../output/session_*/simulation_results.json')
    if session_results:
        result_files.extend(session_results)
    
    # Also look for any JSON files in output directories
    output_results = glob.glob('../output/session_*/*.json')
    if output_results:
        result_files.extend(output_results)

    result_file = None
    
    # If command line argument provided, use that file
    if len(sys.argv) > 1:
        result_file = sys.argv[1]
        if not os.path.exists(result_file):
            print(f"❌ File not found: {result_file}")
            sys.exit(1)
    else:
        # Find the most recent session result
        session_results = glob.glob('../output/session_*/simulation_results.json')
        if session_results:
            # Sort by modification time, most recent first
            session_results.sort(key=os.path.getmtime, reverse=True)
            result_file = session_results[0]
        else:
            # Fall back to other result files
            for file in result_files:
                if os.path.exists(file):
                    result_file = file
                    break

    if result_file:
        print(f"📊 Analyzing results from: {result_file}")
        data = analyze_simulation_results(result_file)

        # Extract session ID from path if it's a session result
        session_id = None
        if 'session_' in result_file:
            import re
            # Extract the full session ID including underscores
            match = re.search(r'session_(\d+_\d+)', result_file)
            if match:
                session_id = match.group(1)

        # Create charts
        create_price_chart(data, session_id=session_id)
        
        # Create PNL charts
        try:
            from visualization_tools import create_comprehensive_analysis, create_pnl_heatmap
            
            # Create comprehensive analysis with multiple charts
            print("📊 Creating comprehensive analysis charts...")
            create_comprehensive_analysis(result_file, session_id)
            
            # Create PNL heatmap
            print("📊 Creating PNL heatmap...")
            create_pnl_heatmap(result_file, session_id)
            
            # Create simple PNL chart
            print("📊 Creating PNL chart...")
            create_pnl_chart(data, session_id)
            
        except ImportError as e:
            print(f"⚠️  Could not import visualization tools: {e}")
        except Exception as e:
            print(f"⚠️  Error creating PNL charts: {e}")

        print("=== ANALYSIS COMPLETE ===")
        print("The flattened JSON format makes it easy to:")
        print("• Load data into any programming language")
        print("• Perform statistical analysis")
        print("• Create visualizations")
        print("• Share results with others")
        print("• No depth limits or circular reference issues!")
    else:
        print("❌ No result files found. Please run a simulation first.")
        print("Available files to look for:")
        for file in result_files:
            print(f"  - {file}")
