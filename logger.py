"""
Audit logging system for compliance and traceability.
Logs all agent actions with timestamps, inputs, outputs, and outcomes.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from schemas import AuditLog


class AuditLogger:
    """Centralized audit logging for all agent actions"""
    
    def __init__(self, log_file: str = "audit_log.jsonl"):
        """
        Initialize audit logger.
        
        Args:
            log_file: Path to log file (JSONL format)
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_action(
        self,
        action: str,
        function_name: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        dry_run: bool = False
    ):
        """
        Log an agent action.
        
        Args:
            action: Description of the action
            function_name: Name of the function called
            input_data: Input parameters
            output_data: Output/result data
            success: Whether action succeeded
            error_message: Error message if failed
            dry_run: Whether this was a dry run
        """
        log_entry = AuditLog(
            timestamp=datetime.now().isoformat(),
            action=action,
            function_name=function_name,
            input_data=input_data,
            output_data=output_data,
            success=success,
            error_message=error_message,
            dry_run=dry_run
        )
        
        # Write to JSONL file (one JSON object per line)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry.model_dump_json() + "\n")
        
        # Also print to console for visibility
        status = "[OK]" if success else "[FAIL]"
        dry_run_indicator = "[DRY RUN] " if dry_run else ""
        print(f"\n{dry_run_indicator}[AUDIT] {status} {action}")
        if error_message:
            print(f"  Error: {error_message}")
    
    def get_recent_logs(self, limit: int = 10) -> list:
        """
        Retrieve recent log entries.
        
        Args:
            limit: Number of recent entries to retrieve
            
        Returns:
            List of log entries
        """
        if not self.log_file.exists():
            return []
        
        logs = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return logs


# Global logger instance
audit_logger = AuditLogger()

