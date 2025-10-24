#!/usr/bin/env python3
"""
Real-time visualization for trading simulator.
Generates live price and PNL charts during simulation.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import numpy as np
from decimal import Decimal
import threading
import time

class LiveTradingVisualizer:
    """Real-time visualization for trading simulator."""
    
    def __init__(self, max_points=100):
        self.max_points = max_points
        
        # Data storage
        self.hours = deque(maxlen=max_points)
        self.prices = deque(maxlen=max_points)
        self.user_pnl = {user_id: deque(maxlen=max_points) for user_id in ['user1', 'user2', 'user3']}
        self.user_equity = {user_id: deque(maxlen=max_points) for user_id in ['user1', 'user2', 'user3']}
        
        # Setup plots
        self.setup_plots()
        
        # Animation
        self.animation = None
        self.is_running = False
    
    def setup_plots(self):
        """Setup matplotlib plots."""
        plt.style.use('seaborn-v0_8')
        
        # Create figure with subplots
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 10))
        self.fig.suptitle('Live Trading Simulation Dashboard', fontsize=16, fontweight='bold')
        
        # Price chart
        self.ax1.set_title('BTC/USD Price Movement', fontweight='bold')
        self.ax1.set_xlabel('Hour')
        self.ax1.set_ylabel('Price ($)')
        self.ax1.grid(True, alpha=0.3)
        
        # PNL chart
        self.ax2.set_title('User PNL & Equity', fontweight='bold')
        self.ax2.set_xlabel('Hour')
        self.ax2.set_ylabel('Value ($)')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Color scheme
        self.colors = {
            'user1': '#1f77b4',  # Blue
            'user2': '#ff7f0e',  # Orange  
            'user3': '#2ca02c'   # Green
        }
        
        plt.tight_layout()
    
    def update_data(self, hour, price, user_data):
        """Update data for visualization."""
        self.hours.append(hour)
        self.prices.append(float(price))
        
        for user_id, data in user_data.items():
            if user_id in self.user_pnl:
                self.user_pnl[user_id].append(float(data.get('unrealized_pnl', 0)))
                self.user_equity[user_id].append(float(data.get('total_equity', 0)))
    
    def animate(self, frame):
        """Animation function for live updates."""
        if not self.hours:
            return
        
        # Clear and redraw price chart
        self.ax1.clear()
        self.ax1.set_title('BTC/USD Price Movement', fontweight='bold')
        self.ax1.set_xlabel('Hour')
        self.ax1.set_ylabel('Price ($)')
        self.ax1.grid(True, alpha=0.3)
        
        if len(self.hours) > 1:
            self.ax1.plot(list(self.hours), list(self.prices), 'b-', linewidth=2, marker='o', markersize=4)
            self.ax1.fill_between(list(self.hours), list(self.prices), alpha=0.3)
        
        # Format price axis
        self.ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Clear and redraw PNL chart
        self.ax2.clear()
        self.ax2.set_title('User PNL & Equity', fontweight='bold')
        self.ax2.set_xlabel('Hour')
        self.ax2.set_ylabel('Value ($)')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        if len(self.hours) > 1:
            # Plot PNL lines
            for user_id in self.user_pnl:
                if len(self.user_pnl[user_id]) > 0:
                    self.ax2.plot(list(self.hours), list(self.user_pnl[user_id]), 
                               color=self.colors[user_id], linestyle='-', linewidth=2, 
                               label=f'{user_id} PNL', alpha=0.7)
            
            # Plot equity lines
            for user_id in self.user_equity:
                if len(self.user_equity[user_id]) > 0:
                    self.ax2.plot(list(self.hours), list(self.user_equity[user_id]), 
                               color=self.colors[user_id], linestyle='--', linewidth=1, 
                               label=f'{user_id} Equity', alpha=0.5)
        
        self.ax2.legend(loc='upper left', fontsize=8)
        self.ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
    
    def start_animation(self):
        """Start the live animation."""
        self.is_running = True
        self.animation = animation.FuncAnimation(
            self.fig, self.animate, interval=1000, blit=False
        )
        plt.show(block=False)
    
    def stop_animation(self):
        """Stop the animation."""
        self.is_running = False
        if self.animation:
            self.animation.event_source.stop()
    
    def save_final_chart(self, filename="trading_simulation_chart.png"):
        """Save the final chart."""
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 Final chart saved as: {filename}")

def create_comprehensive_analysis(results_file, session_id=None):
    """Create comprehensive analysis with multiple charts."""
    import json
    import os
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    # Determine output filename
    output_filename = "comprehensive_analysis.png"
    if session_id:
        # Get the project root directory (parent of tests)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, f"output/session_{session_id}")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, output_filename)
    
    # Create figure with multiple subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Comprehensive Trading Analysis', fontsize=16, fontweight='bold')
    
    # 1. Price Movement Chart
    price_history = data['price_history']
    if price_history:
        hours = [p['hour'] for p in price_history]
        prices = [p['price'] for p in price_history]
        
        ax1.plot(hours, prices, 'b-', linewidth=2, marker='o', markersize=3)
        ax1.set_title('BTC/USD Price Movement')
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('Price ($)')
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add price change annotation
        if len(prices) > 1:
            price_change = ((prices[-1] - prices[0]) / prices[0]) * 100
            ax1.annotate(f'Change: {price_change:.2f}%', 
                        xy=(0.02, 0.98), xycoords='axes fraction',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    # 2. Trade Volume Chart
    trades = data['trade_history']
    if trades:
        trade_hours = [t['hour'] for t in trades]
        trade_volumes = [t['quantity'] * t['price'] for t in trades]
        
        ax2.bar(trade_hours, trade_volumes, alpha=0.7, color='green')
        ax2.set_title('Trade Volume by Hour')
        ax2.set_xlabel('Hour')
        ax2.set_ylabel('Volume ($)')
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    else:
        ax2.text(0.5, 0.5, 'No Trades Executed', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Trade Volume by Hour')
    
    # 3. User Equity Over Time
    user_balances = data['final_user_balances']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for i, (user_id, balance) in enumerate(user_balances.items()):
        # For simplicity, show final equity (in real implementation, you'd track over time)
        ax3.bar(user_id, balance['total_equity'], color=colors[i % len(colors)], alpha=0.7)
    
    ax3.set_title('Final User Equity')
    ax3.set_ylabel('Equity ($)')
    ax3.grid(True, alpha=0.3)
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # 4. Funding Events
    funding_events = data['funding_events']
    if funding_events:
        funding_hours = [f['hour'] for f in funding_events]
        funding_amounts = [f['total_funding_paid'] for f in funding_events]
        
        ax4.bar(funding_hours, funding_amounts, alpha=0.7, color='red')
        ax4.set_title('Funding Payments by Hour')
        ax4.set_xlabel('Hour')
        ax4.set_ylabel('Funding Paid ($)')
        ax4.grid(True, alpha=0.3)
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    else:
        ax4.text(0.5, 0.5, 'No Funding Events', ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Funding Payments by Hour')
    
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"📊 Comprehensive analysis chart saved as: {output_filename}")
    plt.close()

def create_pnl_heatmap(results_file, session_id=None):
    """Create a PNL heatmap showing user performance."""
    import json
    import pandas as pd
    import os
    
    # Determine output filename
    output_filename = "pnl_heatmap.png"
    if session_id:
        # Get the project root directory (parent of tests)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, f"output/session_{session_id}")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, output_filename)
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    # Extract user position history
    positions = data.get('user_position_history', [])
    if not positions:
        print("No position history available for heatmap")
        return
    
    # Create PNL matrix
    user_pnl_data = {}
    for pos in positions:
        user_id = pos['user_id']
        hour = pos['hour']
        pnl = pos.get('unrealized_pnl', 0)
        
        if user_id not in user_pnl_data:
            user_pnl_data[user_id] = {}
        user_pnl_data[user_id][hour] = pnl
    
    # Convert to DataFrame
    df = pd.DataFrame(user_pnl_data).fillna(0)
    
    # Create heatmap
    plt.figure(figsize=(12, 8))
    plt.imshow(df.values, cmap='RdYlGn', aspect='auto')
    plt.colorbar(label='PNL ($)')
    plt.title('User PNL Heatmap Over Time')
    plt.xlabel('Users')
    plt.ylabel('Hour')
    plt.xticks(range(len(df.columns)), df.columns)
    plt.yticks(range(len(df.index)), df.index)
    
    # Add value annotations
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            plt.text(j, i, f'{df.iloc[i, j]:.0f}', ha='center', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"📊 PNL heatmap saved as: {output_filename}")
    plt.close()

if __name__ == "__main__":
    # Example usage
    print("📊 Trading Visualization Tools")
    print("=" * 50)
    print("1. analyze_results.py - Analyze simulation results")
    print("2. debug_trades.py - Debug trade data")
    print("3. test_simulator.py - Test simulator functionality")
    print("4. Live visualization - Real-time charts during simulation")
    print("5. Comprehensive analysis - Multi-chart analysis")
    print("6. PNL heatmap - User performance visualization")
    print()
    print("To use live visualization, integrate LiveTradingVisualizer into your simulator!")
