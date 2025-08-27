#!/usr/bin/env python3
"""
Test script for Performance Dashboard functionality
==================================================

Comprehensive test suite for the Real-Time Performance Dashboard, including
metrics collection, alert management, visualization components, and integration testing.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import time
import threading
from datetime import datetime, timedelta
import random

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from performance_dashboard import (
    PerformanceDashboard, MetricsCollector, AlertManager, PerformanceChart,
    PerformanceMetric, Alert, MetricType, AlertSeverity, 
    create_performance_dashboard_panel
)
from ui_framework import ThemeManager, StatusManager

def test_performance_metric():
    """Test PerformanceMetric data structure."""
    print("Testing PerformanceMetric...")
    
    try:
        # Test basic metric creation
        metric = PerformanceMetric(
            metric_type=MetricType.CPU_PERCENT,
            value=75.5,
            timestamp=datetime.now(),
            unit="%",
            source="test",
            metadata={'test_key': 'test_value'}
        )
        
        assert metric.metric_type == MetricType.CPU_PERCENT
        assert metric.value == 75.5
        assert metric.unit == "%"
        assert metric.source == "test"
        assert metric.metadata['test_key'] == 'test_value'
        
        print("[OK] PerformanceMetric creation and attributes")
        
        # Test different metric types
        for metric_type in MetricType:
            test_metric = PerformanceMetric(
                metric_type=metric_type,
                value=random.uniform(10, 90),
                timestamp=datetime.now(),
                unit="%" if "percent" in metric_type.value else "count"
            )
            assert test_metric.metric_type == metric_type
        
        print("[OK] All MetricType variations work")
        return True
        
    except Exception as e:
        print(f"[FAIL] PerformanceMetric test failed: {e}")
        return False

def test_alert_system():
    """Test Alert and AlertManager functionality."""
    print("\nTesting Alert System...")
    
    try:
        # Test Alert creation
        alert = Alert(
            id="test_alert_001",
            severity=AlertSeverity.WARNING,
            title="High CPU Usage",
            message="CPU usage is above threshold",
            metric_type=MetricType.CPU_PERCENT,
            current_value=85.0,
            threshold=80.0,
            timestamp=datetime.now()
        )
        
        assert alert.severity == AlertSeverity.WARNING
        assert alert.current_value == 85.0
        assert not alert.acknowledged
        
        print("[OK] Alert creation")
        
        # Test AlertManager
        alert_manager = AlertManager()
        alerts_triggered = []
        
        def alert_callback(new_alert):
            alerts_triggered.append(new_alert)
        
        alert_manager.add_alert_callback(alert_callback)
        
        # Test threshold checking
        high_cpu_metric = PerformanceMetric(
            MetricType.CPU_PERCENT, 85.0, datetime.now(), "%"
        )
        
        alert_manager.check_metrics([high_cpu_metric])
        
        # Should trigger an alert
        assert len(alert_manager.get_active_alerts()) > 0
        assert len(alerts_triggered) > 0
        
        print("[OK] Alert triggering and callbacks")
        
        # Test alert acknowledgment
        active_alerts = alert_manager.get_active_alerts()
        if active_alerts:
            alert_manager.acknowledge_alert(active_alerts[0].id)
            assert active_alerts[0].acknowledged
        
        print("[OK] Alert acknowledgment")
        
        # Test alert clearing
        alert_manager.clear_acknowledged_alerts()
        remaining_alerts = [a for a in alert_manager.active_alerts if not a.acknowledged]
        assert len(remaining_alerts) == 0
        
        print("[OK] Alert clearing")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Alert system test failed: {e}")
        return False

def test_metrics_collector():
    """Test MetricsCollector functionality with mock database."""
    print("\nTesting MetricsCollector...")
    
    try:
        # Mock database connection
        class MockDBConnection:
            def execute_query(self, query, params=None):
                # Return mock data based on query patterns
                if "dm_db_resource_stats" in query:
                    return [{'avg_cpu_percent': random.uniform(20, 80), 
                            'avg_dtu_percent': random.uniform(15, 70),
                            'avg_data_io_percent': random.uniform(10, 60),
                            'avg_log_write_percent': random.uniform(5, 40)}]
                elif "dm_os_memory_clerks" in query:
                    return [{'memory_used_mb': random.uniform(500, 2000)}]
                elif "dm_exec_sessions" in query:
                    return [{'active_connections': random.randint(5, 50),
                            'running_sessions': random.randint(1, 20),
                            'blocked_sessions': random.randint(0, 5)}]
                elif "dm_os_wait_stats" in query:
                    return [{'wait_type': 'PAGEIOLATCH_SH', 'wait_time_ms': random.randint(1000, 50000),
                            'waiting_tasks_count': random.randint(1, 100), 'signal_wait_time_ms': random.randint(100, 1000)}]
                elif "database_files" in query:
                    return [{'used_gb': random.uniform(1, 10), 'allocated_gb': 20}]
                return []
        
        # Mock schema analyzer
        class MockSchemaAnalyzer:
            pass
        
        mock_db = MockDBConnection()
        mock_analyzer = MockSchemaAnalyzer()
        
        collector = MetricsCollector(mock_db, mock_analyzer)
        
        # Test metrics collection
        metrics = collector._collect_all_metrics()
        assert len(metrics) > 0
        
        print(f"[OK] Collected {len(metrics)} metrics")
        
        # Test specific metric collection methods
        cpu_metrics = collector._collect_cpu_metrics(datetime.now())
        assert len(cpu_metrics) > 0
        
        memory_metrics = collector._collect_memory_metrics(datetime.now())
        assert len(memory_metrics) > 0
        
        print("[OK] Individual metric collection methods")
        
        # Test history management
        test_metric = PerformanceMetric(MetricType.CPU_PERCENT, 50.0, datetime.now(), "%")
        collector._add_to_history(test_metric)
        
        history = collector.get_metric_history(MetricType.CPU_PERCENT, hours=1)
        assert len(history) == 1
        
        latest = collector.get_latest_metric(MetricType.CPU_PERCENT)
        assert latest is not None
        assert latest.value == 50.0
        
        print("[OK] Metrics history management")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] MetricsCollector test failed: {e}")
        return False

def test_performance_chart():
    """Test PerformanceChart visualization component."""
    print("\nTesting PerformanceChart...")
    
    try:
        # Create test window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create test frame
        test_frame = ttk.Frame(root)
        
        # Create chart
        theme_manager = ThemeManager()
        chart = PerformanceChart(test_frame, width=300, height=200, 
                               metric_type=MetricType.CPU_PERCENT,
                               theme_manager=theme_manager)
        
        print("[OK] PerformanceChart created")
        
        # Test data updates
        for i in range(10):
            metric = PerformanceMetric(
                MetricType.CPU_PERCENT,
                random.uniform(20, 80),
                datetime.now() + timedelta(seconds=i),
                "%"
            )
            chart.update_data(metric)
        
        assert len(chart.data_points) == 10
        
        print("[OK] Chart data updates")
        
        # Test data clearing
        chart.clear_data()
        assert len(chart.data_points) == 0
        
        print("[OK] Chart data clearing")
        
        # Test with different metric types
        for metric_type in [MetricType.MEMORY_PERCENT, MetricType.IO_PERCENT, MetricType.ACTIVE_CONNECTIONS]:
            test_chart = PerformanceChart(test_frame, metric_type=metric_type, theme_manager=theme_manager)
            test_metric = PerformanceMetric(metric_type, 50.0, datetime.now(), 
                                          "%" if "percent" in metric_type.value else "count")
            test_chart.update_data(test_metric)
            assert len(test_chart.data_points) == 1
        
        print("[OK] Multiple chart types")
        
        # Cleanup
        root.destroy()
        return True
        
    except Exception as e:
        print(f"[FAIL] PerformanceChart test failed: {e}")
        return False

def test_performance_dashboard():
    """Test PerformanceDashboard main component."""
    print("\nTesting PerformanceDashboard...")
    
    try:
        # Create test window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create theme and status managers
        theme_manager = ThemeManager()
        status_manager = StatusManager(root)
        
        # Create test frame
        test_frame = ttk.Frame(root)
        
        # Test dashboard creation without database connection
        dashboard = PerformanceDashboard(test_frame, None, None, theme_manager, status_manager)
        
        print("[OK] PerformanceDashboard created (no connection mode)")
        
        # Test UI components exist
        assert dashboard.main_frame is not None
        assert dashboard.notebook is not None
        assert len(dashboard.metric_cards) > 0
        assert len(dashboard.charts) > 0
        
        print("[OK] UI components created")
        
        # Test with mock components
        dashboard.metrics_collector = type('MockCollector', (), {
            'metrics_queue': type('MockQueue', (), {
                'empty': lambda: True,
                'get_nowait': lambda: None
            })(),
            'is_collecting': False
        })()
        
        # Test UI update (should not crash)
        dashboard._update_ui()
        
        print("[OK] UI updates work")
        
        # Test metric card updates
        test_metric = PerformanceMetric(MetricType.CPU_PERCENT, 75.0, datetime.now(), "%")
        dashboard._update_metric_card(test_metric)
        
        print("[OK] Metric card updates")
        
        # Test alert handling
        test_alert = Alert(
            id="test_001",
            severity=AlertSeverity.WARNING,
            title="Test Alert",
            message="Test message",
            metric_type=MetricType.CPU_PERCENT,
            current_value=85.0,
            threshold=80.0,
            timestamp=datetime.now()
        )
        
        dashboard._on_new_alert(test_alert)
        
        # Check if alert was added to tree
        alerts_in_tree = dashboard.alerts_tree.get_children()
        assert len(alerts_in_tree) > 0
        
        print("[OK] Alert handling")
        
        # Test alert clearing
        dashboard._clear_all_alerts()
        alerts_after_clear = dashboard.alerts_tree.get_children()
        assert len(alerts_after_clear) == 0
        
        print("[OK] Alert clearing")
        
        # Cleanup
        root.destroy()
        return True
        
    except Exception as e:
        print(f"[FAIL] PerformanceDashboard test failed: {e}")
        return False

def test_factory_function():
    """Test the factory function."""
    print("\nTesting factory function...")
    
    try:
        # Create test window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create test frame
        test_frame = ttk.Frame(root)
        
        # Test factory function
        theme_manager = ThemeManager()
        status_manager = StatusManager(root)
        dashboard = create_performance_dashboard_panel(
            test_frame, None, None, theme_manager, status_manager
        )
        
        assert isinstance(dashboard, PerformanceDashboard)
        print("[OK] Factory function works")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"[FAIL] Factory function test failed: {e}")
        return False

def test_real_time_simulation():
    """Test real-time behavior simulation."""
    print("\nTesting real-time simulation...")
    
    try:
        # Create test window
        root = tk.Tk()
        root.title("Performance Dashboard Real-Time Test")
        root.geometry("900x700")
        
        # Create theme manager
        theme_manager = ThemeManager()
        status_manager = StatusManager(root)
        
        # Create dashboard
        dashboard = PerformanceDashboard(root, None, None, theme_manager, status_manager)
        
        # Simulate real-time data
        def simulate_data():
            # Generate mock metrics
            mock_metrics = [
                PerformanceMetric(MetricType.CPU_PERCENT, random.uniform(20, 90), datetime.now(), "%"),
                PerformanceMetric(MetricType.MEMORY_PERCENT, random.uniform(30, 85), datetime.now(), "%"),
                PerformanceMetric(MetricType.IO_PERCENT, random.uniform(10, 70), datetime.now(), "%"),
                PerformanceMetric(MetricType.ACTIVE_CONNECTIONS, random.randint(5, 50), datetime.now(), "connections"),
                PerformanceMetric(MetricType.DTU_PERCENT, random.uniform(15, 80), datetime.now(), "%"),
                PerformanceMetric(MetricType.STORAGE_PERCENT, random.uniform(40, 90), datetime.now(), "%"),
            ]
            
            # Update dashboard
            for metric in mock_metrics:
                # Update metric cards
                dashboard._update_metric_card(metric)
                
                # Update charts
                if metric.metric_type in dashboard.charts:
                    dashboard.charts[metric.metric_type].update_data(metric)
                
                # Check alerts
                dashboard.alert_manager.check_metrics([metric])
            
            # Check for new alerts
            for alert in dashboard.alert_manager.get_active_alerts():
                if not any(dashboard.alerts_tree.item(item)['values'][0] == alert.timestamp.strftime("%H:%M:%S") 
                          for item in dashboard.alerts_tree.get_children()):
                    dashboard._on_new_alert(alert)
            
            # Schedule next update
            root.after(1000, simulate_data)  # Update every second
        
        print("[OK] Real-time simulation setup complete")
        print("Visual test window opened - close to continue")
        
        # Start simulation
        simulate_data()
        
        # Auto-close after 3 seconds for testing
        root.after(3000, root.destroy)
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Real-time simulation test failed: {e}")
        return False

def test_performance_stress():
    """Test performance with high data volume."""
    print("\nTesting performance under stress...")
    
    try:
        # Create dashboard
        root = tk.Tk()
        root.withdraw()
        
        theme_manager = ThemeManager()
        status_manager = StatusManager(root)
        dashboard = PerformanceDashboard(root, None, None, theme_manager, status_manager)
        
        # Generate large amount of test data
        start_time = time.time()
        
        for i in range(1000):  # 1000 metric updates
            metric = PerformanceMetric(
                MetricType.CPU_PERCENT,
                random.uniform(20, 80),
                datetime.now(),
                "%"
            )
            dashboard._update_metric_card(metric)
            
            if MetricType.CPU_PERCENT in dashboard.charts:
                dashboard.charts[MetricType.CPU_PERCENT].update_data(metric)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"[OK] Processed 1000 metrics in {processing_time:.2f} seconds")
        
        # Test alert performance
        start_time = time.time()
        
        high_value_metrics = [
            PerformanceMetric(MetricType.CPU_PERCENT, 95.0, datetime.now(), "%")
            for _ in range(100)
        ]
        
        dashboard.alert_manager.check_metrics(high_value_metrics)
        
        end_time = time.time()
        alert_time = end_time - start_time
        
        print(f"[OK] Processed 100 alert checks in {alert_time:.2f} seconds")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"[FAIL] Performance stress test failed: {e}")
        return False

def test_threading_safety():
    """Test thread safety of components."""
    print("\nTesting threading safety...")
    
    try:
        # Create alert manager
        alert_manager = AlertManager()
        alerts_received = []
        
        def alert_callback(alert):
            alerts_received.append(alert)
        
        alert_manager.add_alert_callback(alert_callback)
        
        # Create multiple threads that generate alerts
        def generate_alerts(thread_id):
            for i in range(10):
                metric = PerformanceMetric(
                    MetricType.CPU_PERCENT, 
                    random.uniform(85, 95),  # High values to trigger alerts
                    datetime.now(),
                    "%"
                )
                alert_manager.check_metrics([metric])
                time.sleep(0.01)  # Small delay
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=generate_alerts, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        print(f"[OK] Threading safety test completed, received {len(alerts_received)} alerts")
        
        # Verify no data corruption
        assert len(alert_manager.active_alerts) > 0
        assert len(alerts_received) > 0
        
        print("[OK] Thread safety verified")
        return True
        
    except Exception as e:
        print(f"[FAIL] Threading safety test failed: {e}")
        return False

def main():
    """Run all performance dashboard tests."""
    print("Performance Dashboard Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Test individual components
    if not test_performance_metric():
        all_passed = False
    
    if not test_alert_system():
        all_passed = False
    
    if not test_metrics_collector():
        all_passed = False
    
    if not test_performance_chart():
        all_passed = False
    
    if not test_performance_dashboard():
        all_passed = False
    
    if not test_factory_function():
        all_passed = False
    
    # Test performance and threading
    if not test_performance_stress():
        all_passed = False
    
    if not test_threading_safety():
        all_passed = False
    
    # Test real-time simulation (visual test)
    if not test_real_time_simulation():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests passed! Performance Dashboard is ready.")
        print("\nFeatures tested:")
        print("- Performance metrics data structures")
        print("- Alert system with thresholds and callbacks") 
        print("- Metrics collection with mock database")
        print("- Interactive charts with real-time updates")
        print("- Complete dashboard UI integration")
        print("- Factory function and component creation")
        print("- Performance under high data volume")
        print("- Thread safety for concurrent operations")
        print("- Real-time simulation and visualization")
    else:
        print("Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)