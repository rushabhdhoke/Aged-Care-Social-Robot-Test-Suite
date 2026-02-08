"""
Regression Detection Framework for Aged Care Robot Testing

Tracks metrics over time and detects regressions by comparing
against baseline measurements.
"""

import json
import os
from pathlib import Path
from typing import Dict
from datetime import datetime


class RegressionDetector:
    """
    Tracks metrics over time and detects regressions.
    
    Baseline metrics are stored in JSON files.
    Each test run is compared against the baseline.
    """
    
    def __init__(self, baseline_dir: str = "tests/baselines"):
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(exist_ok=True, parents=True)
    
    def save_baseline(self, test_name: str, metrics: Dict):
        """
        Save current metrics as the new baseline.
        
        This should be run on 'main' branch after validating quality.
        """
        baseline_file = self.baseline_dir / f"{test_name}_baseline.json"
        
        baseline_data = {
            'test_name': test_name,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'git_commit': os.getenv('GIT_COMMIT', 'unknown')
        }
        
        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        print(f"✅ Saved baseline: {baseline_file}")
    
    def load_baseline(self, test_name: str) -> Dict:
        """Load baseline metrics for comparison"""
        baseline_file = self.baseline_dir / f"{test_name}_baseline.json"
        
        if not baseline_file.exists():
            print(f"⚠️  No baseline found for {test_name}")
            return None
        
        with open(baseline_file, 'r') as f:
            return json.load(f)
    
    def detect_regression(self, test_name: str, current_metrics: Dict) -> Dict:
        """
        Compare current metrics to baseline.
        
        Returns:
            {
                'regression_detected': bool,
                'failing_metrics': List[str],
                'comparison': Dict  # metric-by-metric comparison
            }
        """
        baseline = self.load_baseline(test_name)
        
        if baseline is None:
            # No baseline = can't detect regression, but save current as baseline
            self.save_baseline(test_name, current_metrics)
            return {
                'regression_detected': False,
                'failing_metrics': [],
                'comparison': {},
                'note': 'No baseline found, saved current run as baseline'
            }
        
        failing_metrics = []
        comparison = {}
        
        baseline_metrics = baseline['metrics']
        
        # Compare each metric
        for metric_name, current_value in current_metrics.items():
            if metric_name not in baseline_metrics:
                continue  # New metric, skip
            
            baseline_value = baseline_metrics[metric_name]
            
            # Determine if regression occurred
            # For boolean metrics (passed), False < True is regression
            # For numeric metrics, check thresholds
            
            if isinstance(current_value, bool):
                regressed = (current_value == False and baseline_value == True)
            elif isinstance(current_value, (int, float)):
                # For latency: increase is bad, but allow for API variance
                if 'latency' in metric_name.lower():
                    regressed = current_value > baseline_value * 1.5  # 50% tolerance for API variance
                else:
                    # For success rates: decrease is bad
                    regressed = current_value < baseline_value * 0.9  # 10% tolerance
            else:
                regressed = False
            
            comparison[metric_name] = {
                'baseline': baseline_value,
                'current': current_value,
                'regressed': regressed
            }
            
            if regressed:
                failing_metrics.append(metric_name)
        
        return {
            'regression_detected': len(failing_metrics) > 0,
            'failing_metrics': failing_metrics,
            'comparison': comparison
        }
