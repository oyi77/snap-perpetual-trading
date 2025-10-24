#!/usr/bin/env python3
"""
Log management utility for the Perpetual Futures Trading Simulator.
Provides tools to organize, clean, and analyze session-based logs.
"""
import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Optional
import argparse


class LogManager:
    """Manages session-based logs for the trading simulator."""
    
    def __init__(self, logs_dir: str = "logs", output_dir: str = "output"):
        self.logs_dir = logs_dir
        self.output_dir = output_dir
    
    def list_sessions(self) -> List[Dict]:
        """List all available sessions."""
        if not os.path.exists(self.logs_dir):
            return []
        
        sessions = []
        for item in os.listdir(self.logs_dir):
            if item.startswith("session_"):
                session_path = os.path.join(self.logs_dir, item)
                if os.path.isdir(session_path):
                    session_id = item.replace("session_", "")
                    
                    # Get session info
                    session_info = self._get_session_info(session_path, session_id)
                    sessions.append(session_info)
        
        # Sort by creation time (newest first)
        sessions.sort(key=lambda x: x["created_at"], reverse=True)
        return sessions
    
    def _get_session_info(self, session_path: str, session_id: str) -> Dict:
        """Get information about a session."""
        info = {
            "session_id": session_id,
            "path": session_path,
            "created_at": datetime.fromtimestamp(os.path.getctime(session_path)),
            "files": [],
            "total_size": 0
        }
        
        # List files in session directory
        if os.path.exists(session_path):
            for file in os.listdir(session_path):
                file_path = os.path.join(session_path, file)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    info["files"].append({
                        "name": file,
                        "size": file_size,
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path))
                    })
                    info["total_size"] += file_size
        
        # Check for corresponding output directory
        output_session_path = os.path.join(self.output_dir, f"session_{session_id}")
        if os.path.exists(output_session_path):
            info["has_output"] = True
            info["output_path"] = output_session_path
            # Count output files
            output_files = 0
            output_size = 0
            for file in os.listdir(output_session_path):
                file_path = os.path.join(output_session_path, file)
                if os.path.isfile(file_path):
                    output_files += 1
                    output_size += os.path.getsize(file_path)
            info["output_files"] = output_files
            info["output_size"] = output_size
        else:
            info["has_output"] = False
        
        return info
    
    def clean_old_sessions(self, days: int = 7, dry_run: bool = True) -> List[str]:
        """Clean sessions older than specified days."""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        sessions = self.list_sessions()
        
        sessions_to_remove = []
        for session in sessions:
            if session["created_at"].timestamp() < cutoff_time:
                sessions_to_remove.append(session["session_id"])
                
                if not dry_run:
                    session_path = session["path"]
                    shutil.rmtree(session_path)
                    
                    # Also remove corresponding output directory
                    output_session_path = os.path.join(self.output_dir, f"session_{session['session_id']}")
                    if os.path.exists(output_session_path):
                        shutil.rmtree(output_session_path)
                        print(f"Removed session: {session['session_id']} (logs + output)")
                    else:
                        print(f"Removed session: {session['session_id']} (logs only)")
        
        return sessions_to_remove
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get a summary of a specific session."""
        session_path = os.path.join(self.logs_dir, f"session_{session_id}")
        if not os.path.exists(session_path):
            return None
        
        summary = {
            "session_id": session_id,
            "path": session_path,
            "files": {},
            "statistics": {}
        }
        
        # Read simulation log
        log_file = os.path.join(session_path, "simulation.log")
        if os.path.exists(log_file):
            summary["files"]["simulation_log"] = {
                "exists": True,
                "size": os.path.getsize(log_file),
                "lines": self._count_lines(log_file)
            }
        
        # Read JSON logs
        json_files = [
            "detailed_logs.json",
            "trade_logs.json", 
            "funding_logs.json",
            "liquidation_logs.json",
            "price_logs.json",
            "order_logs.json"
        ]
        
        for json_file in json_files:
            file_path = os.path.join(session_path, json_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    summary["files"][json_file] = {
                        "exists": True,
                        "size": os.path.getsize(file_path),
                        "records": len(data.get("events", data.get("trades", data.get("funding_events", []))))
                    }
                    
                    # Extract statistics
                    if json_file == "trade_logs.json":
                        summary["statistics"]["total_trades"] = len(data.get("trades", []))
                    elif json_file == "funding_logs.json":
                        summary["statistics"]["total_funding_events"] = len(data.get("funding_events", []))
                    elif json_file == "liquidation_logs.json":
                        summary["statistics"]["total_liquidations"] = len(data.get("liquidation_events", []))
                    elif json_file == "price_logs.json":
                        summary["statistics"]["total_price_updates"] = len(data.get("price_updates", []))
                    elif json_file == "order_logs.json":
                        summary["statistics"]["total_orders"] = len(data.get("orders", []))
                        
                except Exception as e:
                    summary["files"][json_file] = {
                        "exists": True,
                        "size": os.path.getsize(file_path),
                        "error": str(e)
                    }
        
        return summary
    
    def _count_lines(self, file_path: str) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, 'r') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def export_session(self, session_id: str, output_dir: str) -> bool:
        """Export a session to a specific directory."""
        session_path = os.path.join(self.logs_dir, f"session_{session_id}")
        if not os.path.exists(session_path):
            return False
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy session directory
        dest_path = os.path.join(output_dir, f"session_{session_id}")
        shutil.copytree(session_path, dest_path)
        
        # Also copy output directory if it exists
        output_session_path = os.path.join(self.output_dir, f"session_{session_id}")
        if os.path.exists(output_session_path):
            dest_output_path = os.path.join(output_dir, f"session_{session_id}_output")
            shutil.copytree(output_session_path, dest_output_path)
            print(f"Exported session {session_id} to {dest_path} (logs + output)")
        else:
            print(f"Exported session {session_id} to {dest_path} (logs only)")
        
        return True
    
    def get_total_logs_size(self) -> Dict:
        """Get total size of all logs."""
        sessions = self.list_sessions()
        
        total_size = 0
        total_files = 0
        
        for session in sessions:
            total_size += session["total_size"]
            total_files += len(session["files"])
            
            # Include output files if they exist
            if session.get("has_output", False):
                total_size += session.get("output_size", 0)
                total_files += session.get("output_files", 0)
        
        return {
            "total_sessions": len(sessions),
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024)
        }


def format_size(size_bytes: int) -> str:
    """Format size in human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def main():
    """Main CLI interface for log management."""
    parser = argparse.ArgumentParser(description="Manage trading simulator logs")
    parser.add_argument("--logs-dir", default="logs", help="Logs directory path")
    parser.add_argument("--list", action="store_true", help="List all sessions")
    parser.add_argument("--summary", help="Get summary for specific session ID")
    parser.add_argument("--clean", type=int, metavar="DAYS", help="Clean sessions older than DAYS")
    parser.add_argument("--dry-run", action="store_true", help="Dry run for clean operation")
    parser.add_argument("--export", nargs=2, metavar=("SESSION_ID", "OUTPUT_DIR"), 
                       help="Export session to directory")
    parser.add_argument("--stats", action="store_true", help="Show overall statistics")
    
    args = parser.parse_args()
    
    log_manager = LogManager(args.logs_dir)
    
    if args.list:
        print("📋 Available Sessions:")
        print("=" * 80)
        sessions = log_manager.list_sessions()
        
        if not sessions:
            print("No sessions found.")
            return
        
        for session in sessions:
            print(f"Session ID: {session['session_id']}")
            print(f"Created: {session['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Log Files: {len(session['files'])} ({format_size(session['total_size'])})")
            if session.get("has_output", False):
                print(f"Output Files: {session.get('output_files', 0)} ({format_size(session.get('output_size', 0))})")
                print(f"Total: {len(session['files']) + session.get('output_files', 0)} files ({format_size(session['total_size'] + session.get('output_size', 0))})")
            else:
                print("Output Files: None")
            print(f"Log Path: {session['path']}")
            if session.get("has_output", False):
                print(f"Output Path: {session['output_path']}")
            print("-" * 40)
    
    elif args.summary:
        print(f"📊 Session Summary: {args.summary}")
        print("=" * 80)
        summary = log_manager.get_session_summary(args.summary)
        
        if not summary:
            print("Session not found.")
            return
        
        print(f"Session ID: {summary['session_id']}")
        print(f"Path: {summary['path']}")
        print("\nFiles:")
        for file_name, file_info in summary["files"].items():
            if file_info["exists"]:
                size_str = format_size(file_info["size"])
                if "records" in file_info:
                    print(f"  ✅ {file_name}: {size_str} ({file_info['records']} records)")
                elif "lines" in file_info:
                    print(f"  ✅ {file_name}: {size_str} ({file_info['lines']} lines)")
                else:
                    print(f"  ✅ {file_name}: {size_str}")
            else:
                print(f"  ❌ {file_name}: Not found")
        
        if summary["statistics"]:
            print("\nStatistics:")
            for key, value in summary["statistics"].items():
                print(f"  {key}: {value}")
    
    elif args.clean is not None:
        print(f"🧹 Cleaning sessions older than {args.clean} days...")
        sessions_to_remove = log_manager.clean_old_sessions(args.clean, args.dry_run)
        
        if not sessions_to_remove:
            print("No sessions to clean.")
        else:
            if args.dry_run:
                print(f"Would remove {len(sessions_to_remove)} sessions:")
                for session_id in sessions_to_remove:
                    print(f"  - {session_id}")
                print("\nRun without --dry-run to actually remove them.")
            else:
                print(f"Removed {len(sessions_to_remove)} sessions.")
    
    elif args.export:
        session_id, output_dir = args.export
        print(f"📦 Exporting session {session_id} to {output_dir}...")
        success = log_manager.export_session(session_id, output_dir)
        if success:
            print("Export completed successfully.")
        else:
            print("Export failed - session not found.")
    
    elif args.stats:
        print("📈 Overall Log Statistics:")
        print("=" * 80)
        stats = log_manager.get_total_logs_size()
        
        print(f"Total Sessions: {stats['total_sessions']}")
        print(f"Total Files: {stats['total_files']}")
        print(f"Total Size: {format_size(stats['total_size_bytes'])}")
        print(f"Average Size per Session: {format_size(stats['total_size_bytes'] / max(1, stats['total_sessions']))}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
