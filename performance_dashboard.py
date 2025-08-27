#!/usr/bin/env python3
"""
Real-Time Performance Dashboard
===============================

A comprehensive real-time performance monitoring dashboard for Azure SQL Database.
Provides live metrics, health monitoring, alerting, and performance trending capabilities.

Features:
- Real-time performance metrics collection and display
- Interactive charts and visualizations with live updates
- Database health monitoring with intelligent alerting
- Performance history tracking and trending analysis
- Resource utilization monitoring (CPU, Memory, IO, Storage)
- Query performance analysis and optimization recommendations
- Wait statistics and blocking process detection
- Customizable alerts and notification system
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Callable, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import queue
import json
import statistics

# Import existing components
from schema_analyzer import SchemaAnalyzer
from ui_framework import ThemeManager, StatusManager, CardComponent

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning" 
    CRITICAL = "critical"
    ERROR = "error"

class MetricType(Enum):
    CPU_PERCENT = "cpu_percent"
    MEMORY_PERCENT = "memory_percent"
    IO_PERCENT = "io_percent"
    DTU_PERCENT = "dtu_percent"
    STORAGE_PERCENT = "storage_percent"
    ACTIVE_CONNECTIONS = "active_connections"
    BLOCKED_PROCESSES = "blocked_processes"
    WAIT_TIME = "wait_time"
    QUERY_DURATION = "query_duration"

@dataclass
class PerformanceMetric:
    """Represents a performance metric data point."""
    metric_type: MetricType
    value: float
    timestamp: datetime
    unit: str = ""
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Represents a performance alert."""
    id: str
    severity: AlertSeverity
    title: str
    message: str
    metric_type: MetricType
    current_value: float
    threshold: float
    timestamp: datetime
    acknowledged: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetricsCollector:
    """Collects performance metrics from Azure SQL Database."""
    
    def __init__(self, db_connection, schema_analyzer: SchemaAnalyzer):
        self.db_connection = db_connection
        self.schema_analyzer = schema_analyzer
        self.is_collecting = False
        self.collection_thread = None
        self.metrics_queue = queue.Queue()
        self.collection_interval = 5  # seconds
        
        # Metric history storage
        self.metrics_history: Dict[MetricType, List[PerformanceMetric]] = {}
        self.max_history_points = 1440  # 24 hours at 1-minute intervals
        
    def start_collection(self):
        """Start metrics collection in background thread."""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        logger.info("Performance metrics collection started")
    
    def stop_collection(self):
        """Stop metrics collection."""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=1)
        logger.info("Performance metrics collection stopped")
    
    def _collection_loop(self):
        """Main metrics collection loop."""
        while self.is_collecting:
            try:
                # Collect all metrics
                metrics = self._collect_all_metrics()
                
                # Add to queue for UI updates
                for metric in metrics:
                    self.metrics_queue.put(metric)
                    self._add_to_history(metric)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                time.sleep(self.collection_interval * 2)  # Back off on error
    
    def _collect_all_metrics(self) -> List[PerformanceMetric]:
        """Collect all performance metrics."""
        metrics = []
        current_time = datetime.now()
        
        try:
            # CPU and DTU metrics
            cpu_metrics = self._collect_cpu_metrics(current_time)
            metrics.extend(cpu_metrics)
            
            # Memory metrics
            memory_metrics = self._collect_memory_metrics(current_time)
            metrics.extend(memory_metrics)
            
            # IO metrics
            io_metrics = self._collect_io_metrics(current_time)
            metrics.extend(io_metrics)
            
            # Connection metrics
            connection_metrics = self._collect_connection_metrics(current_time)
            metrics.extend(connection_metrics)
            
            # Wait statistics
            wait_metrics = self._collect_wait_statistics(current_time)
            metrics.extend(wait_metrics)
            
            # Storage metrics
            storage_metrics = self._collect_storage_metrics(current_time)
            metrics.extend(storage_metrics)
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
        
        return metrics
    
    def _collect_cpu_metrics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect CPU and DTU utilization metrics."""
        metrics = []
        
        try:
            # For Azure SQL Database, we can use sys.dm_db_resource_stats for recent metrics
            query = """
            SELECT TOP 1
                avg_cpu_percent,
                avg_dtu_percent,
                end_time
            FROM sys.dm_db_resource_stats 
            ORDER BY end_time DESC
            """
            
            result = self.db_connection.execute_query(query)
            if result:
                row = result[0]
                
                cpu_metric = PerformanceMetric(
                    metric_type=MetricType.CPU_PERCENT,
                    value=row['avg_cpu_percent'] or 0,
                    timestamp=timestamp,
                    unit="%",
                    source="sys.dm_db_resource_stats"
                )
                metrics.append(cpu_metric)
                
                dtu_metric = PerformanceMetric(
                    metric_type=MetricType.DTU_PERCENT,
                    value=row['avg_dtu_percent'] or 0,
                    timestamp=timestamp,
                    unit="%",
                    source="sys.dm_db_resource_stats"
                )
                metrics.append(dtu_metric)
                
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}")
        
        return metrics
    
    def _collect_memory_metrics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect memory utilization metrics."""
        metrics = []
        
        try:
            # Memory clerks information
            query = """
            SELECT 
                SUM(single_pages_kb + multi_pages_kb) / 1024.0 as memory_used_mb
            FROM sys.dm_os_memory_clerks
            WHERE type IN ('MEMORYCLERK_SQLBUFFERPOOL')
            """
            
            result = self.db_connection.execute_query(query)
            if result:
                memory_used = result[0]['memory_used_mb'] or 0
                
                # For Azure SQL, approximate memory percentage (this is a simplified calculation)
                # In practice, you'd want to get actual memory limits from Azure monitoring
                estimated_memory_percent = min(memory_used / 1000 * 100, 100)  # Rough estimate
                
                memory_metric = PerformanceMetric(
                    metric_type=MetricType.MEMORY_PERCENT,
                    value=estimated_memory_percent,
                    timestamp=timestamp,
                    unit="%",
                    source="sys.dm_os_memory_clerks",
                    metadata={"memory_used_mb": memory_used}
                )
                metrics.append(memory_metric)
                
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
        
        return metrics
    
    def _collect_io_metrics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect IO utilization metrics."""
        metrics = []
        
        try:
            # Recent IO stats
            query = """
            SELECT TOP 1
                avg_data_io_percent,
                avg_log_write_percent
            FROM sys.dm_db_resource_stats 
            ORDER BY end_time DESC
            """
            
            result = self.db_connection.execute_query(query)
            if result:
                row = result[0]
                
                io_metric = PerformanceMetric(
                    metric_type=MetricType.IO_PERCENT,
                    value=max(row['avg_data_io_percent'] or 0, row['avg_log_write_percent'] or 0),
                    timestamp=timestamp,
                    unit="%",
                    source="sys.dm_db_resource_stats",
                    metadata={
                        "data_io_percent": row['avg_data_io_percent'],
                        "log_write_percent": row['avg_log_write_percent']
                    }
                )
                metrics.append(io_metric)
                
        except Exception as e:
            logger.error(f"Error collecting IO metrics: {e}")
        
        return metrics
    
    def _collect_connection_metrics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect connection and session metrics."""
        metrics = []
        
        try:
            # Active connections
            connection_query = """
            SELECT 
                COUNT(*) as active_connections,
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running_sessions,
                COUNT(CASE WHEN blocking_session_id > 0 THEN 1 END) as blocked_sessions
            FROM sys.dm_exec_sessions
            WHERE is_user_process = 1
            """
            
            result = self.db_connection.execute_query(connection_query)
            if result:
                row = result[0]
                
                conn_metric = PerformanceMetric(
                    metric_type=MetricType.ACTIVE_CONNECTIONS,
                    value=row['active_connections'] or 0,
                    timestamp=timestamp,
                    unit="connections",
                    source="sys.dm_exec_sessions",
                    metadata={
                        "running_sessions": row['running_sessions'],
                        "blocked_sessions": row['blocked_sessions']
                    }
                )
                metrics.append(conn_metric)
                
                blocked_metric = PerformanceMetric(
                    metric_type=MetricType.BLOCKED_PROCESSES,
                    value=row['blocked_sessions'] or 0,
                    timestamp=timestamp,
                    unit="processes",
                    source="sys.dm_exec_sessions"
                )
                metrics.append(blocked_metric)
                
        except Exception as e:
            logger.error(f"Error collecting connection metrics: {e}")
        
        return metrics
    
    def _collect_wait_statistics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect wait statistics."""
        metrics = []
        
        try:
            # Top wait types
            wait_query = """
            SELECT TOP 5
                wait_type,
                waiting_tasks_count,
                wait_time_ms,
                signal_wait_time_ms,
                wait_time_ms - signal_wait_time_ms as resource_wait_time_ms
            FROM sys.dm_os_wait_stats
            WHERE wait_time_ms > 0
              AND wait_type NOT LIKE '%SLEEP%'
              AND wait_type NOT LIKE '%IDLE%'
              AND wait_type NOT LIKE '%QUEUE%'
            ORDER BY wait_time_ms DESC
            """
            
            result = self.db_connection.execute_query(wait_query)
            if result and result:
                total_wait_time = sum(row['wait_time_ms'] for row in result)
                
                wait_metric = PerformanceMetric(
                    metric_type=MetricType.WAIT_TIME,
                    value=total_wait_time,
                    timestamp=timestamp,
                    unit="ms",
                    source="sys.dm_os_wait_stats",
                    metadata={"top_waits": result}
                )
                metrics.append(wait_metric)
                
        except Exception as e:
            logger.error(f"Error collecting wait statistics: {e}")
        
        return metrics
    
    def _collect_storage_metrics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect storage utilization metrics."""
        metrics = []
        
        try:
            # Database size and storage
            storage_query = """
            SELECT 
                SUM(CAST(FILEPROPERTY(name, 'SpaceUsed') AS bigint) * 8192.) / (1024 * 1024 * 1024) as used_gb,
                SUM(size * 8192.) / (1024 * 1024 * 1024) as allocated_gb
            FROM sys.database_files
            WHERE type IN (0,1)
            """
            
            result = self.db_connection.execute_query(storage_query)
            if result:
                row = result[0]
                used_gb = row['used_gb'] or 0
                allocated_gb = row['allocated_gb'] or 1  # Avoid division by zero
                
                storage_percent = (used_gb / allocated_gb) * 100 if allocated_gb > 0 else 0
                
                storage_metric = PerformanceMetric(
                    metric_type=MetricType.STORAGE_PERCENT,
                    value=storage_percent,
                    timestamp=timestamp,
                    unit="%",
                    source="sys.database_files",
                    metadata={
                        "used_gb": used_gb,
                        "allocated_gb": allocated_gb
                    }
                )
                metrics.append(storage_metric)
                
        except Exception as e:
            logger.error(f"Error collecting storage metrics: {e}")
        
        return metrics
    
    def _add_to_history(self, metric: PerformanceMetric):
        """Add metric to historical data."""
        if metric.metric_type not in self.metrics_history:
            self.metrics_history[metric.metric_type] = []
        
        history = self.metrics_history[metric.metric_type]
        history.append(metric)
        
        # Keep only recent history
        if len(history) > self.max_history_points:
            history.pop(0)
    
    def get_latest_metric(self, metric_type: MetricType) -> Optional[PerformanceMetric]:
        """Get the latest metric value for a specific type."""
        history = self.metrics_history.get(metric_type, [])
        return history[-1] if history else None
    
    def get_metric_history(self, metric_type: MetricType, 
                          hours: int = 1) -> List[PerformanceMetric]:
        """Get metric history for specified time period."""
        history = self.metrics_history.get(metric_type, [])
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in history if m.timestamp >= cutoff_time]

class AlertManager:
    """Manages performance alerts and notifications."""
    
    def __init__(self):
        self.active_alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Default alert thresholds
        self.thresholds = {
            MetricType.CPU_PERCENT: 80.0,
            MetricType.MEMORY_PERCENT: 85.0,
            MetricType.IO_PERCENT: 90.0,
            MetricType.DTU_PERCENT: 80.0,
            MetricType.STORAGE_PERCENT: 85.0,
            MetricType.BLOCKED_PROCESSES: 5,
            MetricType.ACTIVE_CONNECTIONS: 100,
            MetricType.WAIT_TIME: 10000  # 10 seconds
        }
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback function for new alerts."""
        self.alert_callbacks.append(callback)
    
    def check_metrics(self, metrics: List[PerformanceMetric]):
        """Check metrics against thresholds and generate alerts."""
        for metric in metrics:
            self._check_metric_threshold(metric)
    
    def _check_metric_threshold(self, metric: PerformanceMetric):
        """Check if metric exceeds threshold."""
        threshold = self.thresholds.get(metric.metric_type)
        if not threshold:
            return
        
        if metric.value > threshold:
            # Check if we already have an active alert for this metric
            existing_alert = self._find_active_alert(metric.metric_type)
            
            if not existing_alert:
                # Create new alert
                alert = Alert(
                    id=f"{metric.metric_type.value}_{int(time.time())}",
                    severity=self._determine_severity(metric.value, threshold),
                    title=f"High {metric.metric_type.value.replace('_', ' ').title()}",
                    message=f"{metric.metric_type.value.replace('_', ' ').title()} is {metric.value:.1f}{metric.unit}, exceeding threshold of {threshold}{metric.unit}",
                    metric_type=metric.metric_type,
                    current_value=metric.value,
                    threshold=threshold,
                    timestamp=metric.timestamp,
                    metadata=metric.metadata
                )
                
                self.active_alerts.append(alert)
                self.alert_history.append(alert)
                
                # Notify callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        logger.error(f"Error in alert callback: {e}")
        else:
            # Check if we should clear an existing alert
            existing_alert = self._find_active_alert(metric.metric_type)
            if existing_alert:
                self.acknowledge_alert(existing_alert.id)
    
    def _find_active_alert(self, metric_type: MetricType) -> Optional[Alert]:
        """Find active alert for metric type."""
        for alert in self.active_alerts:
            if alert.metric_type == metric_type and not alert.acknowledged:
                return alert
        return None
    
    def _determine_severity(self, value: float, threshold: float) -> AlertSeverity:
        """Determine alert severity based on how much threshold is exceeded."""
        ratio = value / threshold
        if ratio >= 1.5:
            return AlertSeverity.CRITICAL
        elif ratio >= 1.2:
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.INFO
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert."""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                break
    
    def clear_acknowledged_alerts(self):
        """Remove acknowledged alerts from active list."""
        self.active_alerts = [a for a in self.active_alerts if not a.acknowledged]
    
    def get_active_alerts(self) -> List[Alert]:
        """Get list of active (unacknowledged) alerts."""
        return [a for a in self.active_alerts if not a.acknowledged]

class PerformanceChart:
    """Interactive performance chart widget using tkinter Canvas."""
    
    def __init__(self, parent, width: int = 400, height: int = 200, 
                 metric_type: MetricType = MetricType.CPU_PERCENT,
                 theme_manager: ThemeManager = None):
        self.parent = parent
        self.width = width
        self.height = height
        self.metric_type = metric_type
        self.theme_manager = theme_manager
        
        # Chart data
        self.data_points: List[PerformanceMetric] = []
        self.max_points = 60  # Show last 60 points
        
        # Chart styling
        self.colors = {
            'background': '#ffffff',
            'grid': '#e0e0e0',
            'line': '#2196F3',
            'critical': '#F44336',
            'warning': '#FF9800',
            'text': '#333333'
        }
        
        if theme_manager and theme_manager.current_theme == 'dark':
            self.colors.update({
                'background': '#2d2d2d',
                'grid': '#404040',
                'text': '#ffffff'
            })
        
        self._create_chart()
    
    def _create_chart(self):
        """Create the chart canvas and initial elements."""
        self.canvas = tk.Canvas(self.parent, width=self.width, height=self.height,
                               bg=self.colors['background'], highlightthickness=0)
        self.canvas.pack(padx=5, pady=5)
        
        # Draw initial grid and axes
        self._draw_grid()
        self._draw_axes()
    
    def _draw_grid(self):
        """Draw chart grid lines."""
        # Horizontal grid lines
        for i in range(5):
            y = (self.height - 40) * i / 4 + 20
            self.canvas.create_line(40, y, self.width - 20, y,
                                  fill=self.colors['grid'], width=1, tags='grid')
        
        # Vertical grid lines
        for i in range(6):
            x = (self.width - 60) * i / 5 + 40
            self.canvas.create_line(x, 20, x, self.height - 20,
                                  fill=self.colors['grid'], width=1, tags='grid')
    
    def _draw_axes(self):
        """Draw chart axes and labels."""
        # Y-axis
        self.canvas.create_line(40, 20, 40, self.height - 20,
                              fill=self.colors['text'], width=2, tags='axes')
        
        # X-axis
        self.canvas.create_line(40, self.height - 20, self.width - 20, self.height - 20,
                              fill=self.colors['text'], width=2, tags='axes')
        
        # Y-axis labels (0-100%)
        for i in range(5):
            value = 100 - (i * 25)
            y = (self.height - 40) * i / 4 + 20
            self.canvas.create_text(35, y, text=f"{value}%", fill=self.colors['text'],
                                  font=('Arial', 8), anchor='e', tags='labels')
        
        # Chart title
        title = self.metric_type.value.replace('_', ' ').title()
        self.canvas.create_text(self.width // 2, 10, text=title,
                              fill=self.colors['text'], font=('Arial', 10, 'bold'),
                              tags='title')
    
    def update_data(self, new_metric: PerformanceMetric):
        """Update chart with new data point."""
        if new_metric.metric_type != self.metric_type:
            return
        
        self.data_points.append(new_metric)
        
        # Keep only recent points
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        
        self._redraw_chart()
    
    def _redraw_chart(self):
        """Redraw the chart with current data."""
        # Clear old data
        self.canvas.delete('data_line', 'data_points')
        
        if len(self.data_points) < 2:
            return
        
        # Calculate chart dimensions
        chart_width = self.width - 60
        chart_height = self.height - 40
        
        # Find data range
        values = [p.value for p in self.data_points]
        max_value = max(values) if values else 100
        min_value = min(values) if values else 0
        
        # Ensure reasonable scale
        if max_value - min_value < 10:
            max_value = min_value + 10
        
        # Draw line chart
        points = []
        for i, metric in enumerate(self.data_points):
            x = 40 + (chart_width * i / (len(self.data_points) - 1))
            y = self.height - 20 - ((metric.value - min_value) / (max_value - min_value) * chart_height)
            points.extend([x, y])
        
        if len(points) >= 4:
            # Determine line color based on latest value
            latest_value = self.data_points[-1].value
            line_color = self.colors['line']
            
            if latest_value > 80:
                line_color = self.colors['critical']
            elif latest_value > 60:
                line_color = self.colors['warning']
            
            # Draw line
            self.canvas.create_line(points, fill=line_color, width=2,
                                  smooth=True, tags='data_line')
            
            # Draw points
            for i in range(0, len(points), 2):
                x, y = points[i], points[i + 1]
                self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2,
                                      fill=line_color, outline=line_color, tags='data_points')
    
    def clear_data(self):
        """Clear all chart data."""
        self.data_points.clear()
        self.canvas.delete('data_line', 'data_points')

class PerformanceDashboard:
    """Main Real-Time Performance Dashboard component."""
    
    def __init__(self, parent, db_connection=None, schema_analyzer: SchemaAnalyzer = None,
                 theme_manager: ThemeManager = None, status_manager: StatusManager = None):
        self.parent = parent
        self.db_connection = db_connection
        self.schema_analyzer = schema_analyzer
        self.theme_manager = theme_manager or ThemeManager()
        self.status_manager = status_manager
        
        # Components
        self.metrics_collector = None
        self.alert_manager = AlertManager()
        self.charts: Dict[MetricType, PerformanceChart] = {}
        
        # UI Elements
        self.main_frame = None
        self.metrics_frame = None
        self.charts_frame = None
        self.alerts_frame = None
        self.controls_frame = None
        
        # Update tracking
        self.last_update = datetime.now()
        self.update_timer = None
        
        # Create interface
        self._create_interface()
        
        # Initialize if we have a connection
        if self.db_connection and self.schema_analyzer:
            self._initialize_dashboard()
    
    def _create_interface(self):
        """Create the main dashboard interface."""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Header with controls
        self._create_header()
        
        # Main content area with notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(10, 0))
        
        # Overview tab
        self._create_overview_tab()
        
        # Detailed metrics tab
        self._create_metrics_tab()
        
        # Alerts tab
        self._create_alerts_tab()
        
        # Query analysis tab
        self._create_query_analysis_tab()
    
    def _create_header(self):
        """Create dashboard header with controls."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="Real-Time Performance Dashboard",
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.pack(side='left')
        
        # Status indicator
        self.status_label = ttk.Label(header_frame, text="Disconnected",
                                     foreground='red')
        self.status_label.pack(side='right', padx=(10, 0))
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right', padx=(0, 10))
        
        self.start_button = ttk.Button(controls_frame, text="Start Monitoring",
                                      command=self._start_monitoring)
        self.start_button.pack(side='left', padx=(0, 5))
        
        self.stop_button = ttk.Button(controls_frame, text="Stop Monitoring",
                                     command=self._stop_monitoring, state='disabled')
        self.stop_button.pack(side='left', padx=(0, 5))
        
        ttk.Button(controls_frame, text="Refresh", 
                  command=self._manual_refresh).pack(side='left')
    
    def _create_overview_tab(self):
        """Create overview tab with key metrics."""
        overview_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(overview_frame, text="Overview")
        
        # Key metrics cards
        metrics_grid = ttk.Frame(overview_frame)
        metrics_grid.pack(fill='both', expand=True)
        
        # Create metric cards
        self.metric_cards = {}
        key_metrics = [
            (MetricType.CPU_PERCENT, "CPU Usage"),
            (MetricType.DTU_PERCENT, "DTU Usage"),
            (MetricType.MEMORY_PERCENT, "Memory Usage"),
            (MetricType.IO_PERCENT, "I/O Usage"),
            (MetricType.ACTIVE_CONNECTIONS, "Active Connections"),
            (MetricType.STORAGE_PERCENT, "Storage Usage")
        ]
        
        for i, (metric_type, title) in enumerate(key_metrics):
            row = i // 3
            col = i % 3
            
            card_frame = ttk.LabelFrame(metrics_grid, text=title, padding=10)
            card_frame.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
            
            # Value display
            value_label = ttk.Label(card_frame, text="--",
                                   font=('TkDefaultFont', 24, 'bold'))
            value_label.pack()
            
            # Unit label
            unit_label = ttk.Label(card_frame, text="",
                                  font=('TkDefaultFont', 10))
            unit_label.pack()
            
            # Status indicator
            status_label = ttk.Label(card_frame, text="No Data",
                                   foreground='gray')
            status_label.pack(pady=(5, 0))
            
            self.metric_cards[metric_type] = {
                'frame': card_frame,
                'value': value_label,
                'unit': unit_label,
                'status': status_label
            }
        
        # Configure grid weights
        for i in range(3):
            metrics_grid.columnconfigure(i, weight=1)
        for i in range(2):
            metrics_grid.rowconfigure(i, weight=1)
    
    def _create_metrics_tab(self):
        """Create detailed metrics tab with charts."""
        metrics_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(metrics_frame, text="Detailed Metrics")
        
        # Charts container
        charts_container = ttk.Frame(metrics_frame)
        charts_container.pack(fill='both', expand=True)
        
        # Create performance charts
        chart_metrics = [
            MetricType.CPU_PERCENT,
            MetricType.MEMORY_PERCENT,
            MetricType.IO_PERCENT,
            MetricType.ACTIVE_CONNECTIONS
        ]
        
        for i, metric_type in enumerate(chart_metrics):
            row = i // 2
            col = i % 2
            
            chart_frame = ttk.LabelFrame(charts_container, 
                                        text=metric_type.value.replace('_', ' ').title(),
                                        padding=5)
            chart_frame.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
            
            chart = PerformanceChart(chart_frame, width=350, height=200,
                                   metric_type=metric_type, theme_manager=self.theme_manager)
            self.charts[metric_type] = chart
        
        # Configure grid weights
        for i in range(2):
            charts_container.columnconfigure(i, weight=1)
            charts_container.rowconfigure(i, weight=1)
    
    def _create_alerts_tab(self):
        """Create alerts tab."""
        alerts_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(alerts_frame, text="Alerts")
        
        # Alerts header
        alerts_header = ttk.Frame(alerts_frame)
        alerts_header.pack(fill='x', pady=(0, 10))
        
        ttk.Label(alerts_header, text="Performance Alerts",
                 font=('TkDefaultFont', 12, 'bold')).pack(side='left')
        
        # Clear alerts button
        ttk.Button(alerts_header, text="Clear All",
                  command=self._clear_all_alerts).pack(side='right')
        
        # Alerts list
        self.alerts_tree = ttk.Treeview(alerts_frame, 
                                       columns=('time', 'severity', 'metric', 'value'),
                                       show='headings', height=12)
        
        # Configure columns
        self.alerts_tree.heading('#1', text='Time')
        self.alerts_tree.heading('#2', text='Severity')
        self.alerts_tree.heading('#3', text='Metric')
        self.alerts_tree.heading('#4', text='Value')
        
        self.alerts_tree.column('#1', width=120)
        self.alerts_tree.column('#2', width=80)
        self.alerts_tree.column('#3', width=150)
        self.alerts_tree.column('#4', width=100)
        
        # Scrollbar for alerts
        alerts_scroll = ttk.Scrollbar(alerts_frame, orient='vertical',
                                     command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=alerts_scroll.set)
        
        self.alerts_tree.pack(side='left', fill='both', expand=True)
        alerts_scroll.pack(side='right', fill='y')
    
    def _create_query_analysis_tab(self):
        """Create query analysis tab."""
        query_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(query_frame, text="Query Analysis")
        
        # Top queries section
        top_queries_frame = ttk.LabelFrame(query_frame, text="Top Resource Consuming Queries", padding=5)
        top_queries_frame.pack(fill='both', expand=True)
        
        self.queries_tree = ttk.Treeview(top_queries_frame,
                                       columns=('query', 'cpu', 'duration', 'reads'),
                                       show='headings', height=10)
        
        self.queries_tree.heading('#1', text='Query')
        self.queries_tree.heading('#2', text='CPU Time (ms)')
        self.queries_tree.heading('#3', text='Duration (ms)')
        self.queries_tree.heading('#4', text='Logical Reads')
        
        self.queries_tree.column('#1', width=400)
        self.queries_tree.column('#2', width=100)
        self.queries_tree.column('#3', width=100)
        self.queries_tree.column('#4', width=100)
        
        queries_scroll = ttk.Scrollbar(top_queries_frame, orient='vertical',
                                     command=self.queries_tree.yview)
        self.queries_tree.configure(yscrollcommand=queries_scroll.set)
        
        self.queries_tree.pack(side='left', fill='both', expand=True)
        queries_scroll.pack(side='right', fill='y')
        
        # Refresh button for queries
        ttk.Button(query_frame, text="Refresh Query Analysis",
                  command=self._refresh_query_analysis).pack(pady=(10, 0))
    
    def _initialize_dashboard(self):
        """Initialize dashboard with database connection."""
        try:
            # Create metrics collector
            self.metrics_collector = MetricsCollector(self.db_connection, self.schema_analyzer)
            
            # Set up alert callbacks
            self.alert_manager.add_alert_callback(self._on_new_alert)
            
            # Update status
            self.status_label.config(text="Connected", foreground='green')
            self.start_button.config(state='normal')
            
            if self.status_manager:
                self.status_manager.show_message("Performance Dashboard initialized", "success")
                
        except Exception as e:
            logger.error(f"Failed to initialize dashboard: {e}")
            if self.status_manager:
                self.status_manager.show_message(f"Dashboard initialization failed: {e}", "error")
    
    def _start_monitoring(self):
        """Start real-time monitoring."""
        if not self.metrics_collector:
            return
        
        self.metrics_collector.start_collection()
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        # Start UI update timer
        self._schedule_ui_update()
        
        if self.status_manager:
            self.status_manager.show_message("Performance monitoring started", "success")
    
    def _stop_monitoring(self):
        """Stop real-time monitoring."""
        if self.metrics_collector:
            self.metrics_collector.stop_collection()
        
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        # Cancel UI update timer
        if self.update_timer:
            self.parent.after_cancel(self.update_timer)
        
        if self.status_manager:
            self.status_manager.show_message("Performance monitoring stopped", "info")
    
    def _schedule_ui_update(self):
        """Schedule periodic UI updates."""
        self._update_ui()
        if self.metrics_collector and self.metrics_collector.is_collecting:
            self.update_timer = self.parent.after(2000, self._schedule_ui_update)  # Update every 2 seconds
    
    def _update_ui(self):
        """Update UI with latest metrics."""
        if not self.metrics_collector:
            return
        
        # Process queued metrics
        while not self.metrics_collector.metrics_queue.empty():
            try:
                metric = self.metrics_collector.metrics_queue.get_nowait()
                
                # Update metric cards
                self._update_metric_card(metric)
                
                # Update charts
                if metric.metric_type in self.charts:
                    self.charts[metric.metric_type].update_data(metric)
                
                # Check for alerts
                self.alert_manager.check_metrics([metric])
                
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error updating UI: {e}")
    
    def _update_metric_card(self, metric: PerformanceMetric):
        """Update a metric card with new data."""
        if metric.metric_type not in self.metric_cards:
            return
        
        card = self.metric_cards[metric.metric_type]
        
        # Update value
        if metric.unit == "%":
            card['value'].config(text=f"{metric.value:.1f}")
        else:
            card['value'].config(text=f"{metric.value:.0f}")
        
        card['unit'].config(text=metric.unit)
        
        # Update status and color
        if metric.value > 80:
            status_text = "Critical"
            color = 'red'
        elif metric.value > 60:
            status_text = "Warning"
            color = 'orange'
        else:
            status_text = "Normal"
            color = 'green'
        
        card['status'].config(text=status_text, foreground=color)
    
    def _on_new_alert(self, alert: Alert):
        """Handle new alert."""
        # Add to alerts tree
        severity_colors = {
            AlertSeverity.CRITICAL: 'red',
            AlertSeverity.WARNING: 'orange',
            AlertSeverity.INFO: 'blue'
        }
        
        time_str = alert.timestamp.strftime("%H:%M:%S")
        
        item = self.alerts_tree.insert('', 0, values=(
            time_str,
            alert.severity.value.title(),
            alert.metric_type.value.replace('_', ' ').title(),
            f"{alert.current_value:.1f}"
        ))
        
        # Color code by severity
        color = severity_colors.get(alert.severity, 'black')
        self.alerts_tree.set(item, 'severity', alert.severity.value.title())
    
    def _clear_all_alerts(self):
        """Clear all alerts."""
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)
        
        self.alert_manager.clear_acknowledged_alerts()
    
    def _manual_refresh(self):
        """Manual refresh of dashboard."""
        if self.metrics_collector:
            # Force a metrics collection
            try:
                metrics = self.metrics_collector._collect_all_metrics()
                for metric in metrics:
                    self.metrics_collector.metrics_queue.put(metric)
                self._update_ui()
                
                if self.status_manager:
                    self.status_manager.show_message("Dashboard refreshed", "success")
            except Exception as e:
                logger.error(f"Manual refresh failed: {e}")
                if self.status_manager:
                    self.status_manager.show_message(f"Refresh failed: {e}", "error")
    
    def _refresh_query_analysis(self):
        """Refresh query analysis data."""
        if not self.db_connection:
            return
        
        try:
            # Clear existing data
            for item in self.queries_tree.get_children():
                self.queries_tree.delete(item)
            
            # Query for top resource consuming queries
            query = """
            SELECT TOP 10
                SUBSTRING(qt.text, (qs.statement_start_offset/2)+1,
                    ((CASE qs.statement_end_offset
                        WHEN -1 THEN DATALENGTH(qt.text)
                        ELSE qs.statement_end_offset
                    END - qs.statement_start_offset)/2)+1) AS query_text,
                qs.total_worker_time / qs.execution_count AS avg_cpu_time,
                qs.total_elapsed_time / qs.execution_count AS avg_duration,
                qs.total_logical_reads / qs.execution_count AS avg_logical_reads,
                qs.execution_count
            FROM sys.dm_exec_query_stats qs
            CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
            WHERE qs.execution_count > 1
            ORDER BY qs.total_worker_time DESC
            """
            
            results = self.db_connection.execute_query(query)
            
            for row in results:
                query_text = row['query_text'][:60] + "..." if len(row['query_text']) > 60 else row['query_text']
                
                self.queries_tree.insert('', 'end', values=(
                    query_text.strip(),
                    f"{row['avg_cpu_time']:.0f}",
                    f"{row['avg_duration']:.0f}",
                    f"{row['avg_logical_reads']:.0f}"
                ))
            
            if self.status_manager:
                self.status_manager.show_message("Query analysis refreshed", "success")
                
        except Exception as e:
            logger.error(f"Query analysis refresh failed: {e}")
            if self.status_manager:
                self.status_manager.show_message(f"Query analysis failed: {e}", "error")


def create_performance_dashboard_panel(parent, db_connection=None, schema_analyzer=None, 
                                     theme_manager=None, status_manager=None) -> PerformanceDashboard:
    """
    Factory function to create a Performance Dashboard panel.
    
    Args:
        parent: Parent tkinter widget
        db_connection: Database connection object
        schema_analyzer: SchemaAnalyzer instance
        theme_manager: ThemeManager instance
        status_manager: StatusManager instance
    
    Returns:
        PerformanceDashboard instance
    """
    return PerformanceDashboard(parent, db_connection, schema_analyzer, theme_manager, status_manager)


# Example usage and testing
if __name__ == "__main__":
    import sys
    import os
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    def test_performance_dashboard():
        """Test the performance dashboard with mock data."""
        root = tk.Tk()
        root.title("Performance Dashboard Test")
        root.geometry("1200x800")
        
        # Create theme manager
        theme_manager = ThemeManager()
        
        # Create dashboard without database connection for testing
        dashboard = PerformanceDashboard(root, None, None, theme_manager)
        
        # Test with mock metrics
        mock_metrics = [
            PerformanceMetric(MetricType.CPU_PERCENT, 45.5, datetime.now(), "%"),
            PerformanceMetric(MetricType.MEMORY_PERCENT, 62.3, datetime.now(), "%"),
            PerformanceMetric(MetricType.IO_PERCENT, 28.7, datetime.now(), "%"),
            PerformanceMetric(MetricType.ACTIVE_CONNECTIONS, 12, datetime.now(), "connections"),
        ]
        
        # Simulate metrics updates
        def update_mock_data():
            import random
            for metric_type in [MetricType.CPU_PERCENT, MetricType.MEMORY_PERCENT, 
                              MetricType.IO_PERCENT, MetricType.ACTIVE_CONNECTIONS]:
                value = random.uniform(20, 90)
                metric = PerformanceMetric(metric_type, value, datetime.now(), 
                                         "%" if "percent" in metric_type.value else "")
                
                if metric_type in dashboard.charts:
                    dashboard.charts[metric_type].update_data(metric)
                
                dashboard._update_metric_card(metric)
            
            # Schedule next update
            root.after(2000, update_mock_data)
        
        # Start mock updates
        update_mock_data()
        
        print("Performance Dashboard test running - close window to exit")
        root.mainloop()
    
    test_performance_dashboard()