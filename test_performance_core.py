#!/usr/bin/env python3
"""
Core Performance Dashboard Tests
===============================

Focused tests for Performance Dashboard core functionality without GUI timing issues.
"""

import sys
import os
import time
from datetime import datetime
import random

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from performance_dashboard import (
    PerformanceMetric, Alert, MetricType, AlertSeverity,
    MetricsCollector, AlertManager
)

def test_core_functionality():
    """Test core Performance Dashboard functionality."""
    print("Testing Core Performance Dashboard Functionality")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: PerformanceMetric
    print("\n1. Testing PerformanceMetric...")
    try:
        metric = PerformanceMetric(
            metric_type=MetricType.CPU_PERCENT,
            value=75.5,
            timestamp=datetime.now(),
            unit="%"
        )
        assert metric.value == 75.5
        assert metric.unit == "%"
        print("[OK] PerformanceMetric creation and attributes")
    except Exception as e:
        print(f"[FAIL] PerformanceMetric test failed: {e}")
        all_passed = False
    
    # Test 2: Alert System
    print("\n2. Testing Alert System...")
    try:
        alert_manager = AlertManager()
        alerts_received = []
        
        def alert_callback(alert):
            alerts_received.append(alert)
        
        alert_manager.add_alert_callback(alert_callback)
        
        # Test high CPU metric
        high_cpu = PerformanceMetric(MetricType.CPU_PERCENT, 85.0, datetime.now(), "%")
        alert_manager.check_metrics([high_cpu])
        
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) > 0, "Should have generated an alert"
        assert len(alerts_received) > 0, "Callback should have been called"
        
        print("[OK] Alert generation and callbacks work")
    except Exception as e:
        print(f"[FAIL] Alert system test failed: {e}")
        all_passed = False
    
    # Test 3: Multiple Metrics
    print("\n3. Testing Multiple Metric Types...")
    try:
        test_metrics = [
            PerformanceMetric(MetricType.CPU_PERCENT, 45.0, datetime.now(), "%"),
            PerformanceMetric(MetricType.MEMORY_PERCENT, 62.0, datetime.now(), "%"),
            PerformanceMetric(MetricType.IO_PERCENT, 28.0, datetime.now(), "%"),
            PerformanceMetric(MetricType.ACTIVE_CONNECTIONS, 15, datetime.now(), "connections"),
            PerformanceMetric(MetricType.DTU_PERCENT, 33.0, datetime.now(), "%"),
        ]
        
        for metric in test_metrics:
            assert metric.metric_type in MetricType
            assert metric.value >= 0
            assert metric.timestamp is not None
        
        print(f"[OK] Created and validated {len(test_metrics)} different metric types")
    except Exception as e:
        print(f"[FAIL] Multiple metrics test failed: {e}")
        all_passed = False
    
    # Test 4: Alert Thresholds
    print("\n4. Testing Alert Thresholds...")
    try:
        alert_manager = AlertManager()
        
        # Test different severity levels
        critical_cpu = PerformanceMetric(MetricType.CPU_PERCENT, 95.0, datetime.now(), "%")
        warning_cpu = PerformanceMetric(MetricType.CPU_PERCENT, 82.0, datetime.now(), "%")
        normal_cpu = PerformanceMetric(MetricType.CPU_PERCENT, 45.0, datetime.now(), "%")
        
        alert_manager.check_metrics([critical_cpu])
        critical_alerts = len(alert_manager.get_active_alerts())
        
        alert_manager.active_alerts.clear()  # Reset
        
        alert_manager.check_metrics([warning_cpu])
        warning_alerts = len(alert_manager.get_active_alerts())
        
        alert_manager.active_alerts.clear()  # Reset
        
        alert_manager.check_metrics([normal_cpu])
        normal_alerts = len(alert_manager.get_active_alerts())
        
        assert critical_alerts > 0, "Critical threshold should trigger alert"
        assert warning_alerts > 0, "Warning threshold should trigger alert"
        assert normal_alerts == 0, "Normal value should not trigger alert"
        
        print("[OK] Alert thresholds work correctly")
    except Exception as e:
        print(f"[FAIL] Alert thresholds test failed: {e}")
        all_passed = False
    
    # Test 5: MockMetricsCollector
    print("\n5. Testing Mock Metrics Collection...")
    try:
        class MockDBConnection:
            def execute_query(self, query, params=None):
                if "dm_db_resource_stats" in query:
                    return [{'avg_cpu_percent': 45.5, 'avg_dtu_percent': 38.2,
                            'avg_data_io_percent': 22.1, 'avg_log_write_percent': 15.3}]
                elif "dm_exec_sessions" in query:
                    return [{'active_connections': 25, 'running_sessions': 8, 'blocked_sessions': 1}]
                elif "database_files" in query:
                    return [{'used_gb': 8.5, 'allocated_gb': 20.0}]
                return []
        
        mock_db = MockDBConnection()
        collector = MetricsCollector(mock_db, None)
        
        # Test individual collection methods
        cpu_metrics = collector._collect_cpu_metrics(datetime.now())
        connection_metrics = collector._collect_connection_metrics(datetime.now())
        storage_metrics = collector._collect_storage_metrics(datetime.now())
        
        assert len(cpu_metrics) > 0, "Should collect CPU metrics"
        assert len(connection_metrics) > 0, "Should collect connection metrics"
        assert len(storage_metrics) > 0, "Should collect storage metrics"
        
        print(f"[OK] Mock metrics collection: CPU({len(cpu_metrics)}), Conn({len(connection_metrics)}), Storage({len(storage_metrics)})")
    except Exception as e:
        print(f"[FAIL] Mock metrics collection test failed: {e}")
        all_passed = False
    
    # Test 6: History Management
    print("\n6. Testing Metrics History...")
    try:
        mock_db = type('MockDB', (), {'execute_query': lambda self, q, p=None: []})()
        collector = MetricsCollector(mock_db, None)
        
        # Add test metrics to history
        for i in range(10):
            metric = PerformanceMetric(
                MetricType.CPU_PERCENT,
                random.uniform(20, 80),
                datetime.now(),
                "%"
            )
            collector._add_to_history(metric)
        
        history = collector.get_metric_history(MetricType.CPU_PERCENT, hours=1)
        latest = collector.get_latest_metric(MetricType.CPU_PERCENT)
        
        assert len(history) == 10, f"Expected 10 history items, got {len(history)}"
        assert latest is not None, "Should have latest metric"
        
        print("[OK] Metrics history management works")
    except Exception as e:
        print(f"[FAIL] Metrics history test failed: {e}")
        all_passed = False
    
    # Final Results
    print("\n" + "=" * 60)
    if all_passed:
        print("All core functionality tests passed!")
        print("\nCore features verified:")
        print("- PerformanceMetric data structures [OK]")
        print("- Alert system with thresholds [OK]")
        print("- Multiple metric type support [OK]")
        print("- Alert severity levels [OK]")
        print("- Mock metrics collection [OK]")
        print("- Metrics history management [OK]")
    else:
        print("Some core functionality tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    success = test_core_functionality()
    sys.exit(0 if success else 1)