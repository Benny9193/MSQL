from typing import Dict, List, Any, Optional, Tuple
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from db_connection import AzureSQLConnection

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health status levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class MetricType(Enum):
    """Types of health metrics."""
    PERFORMANCE = "performance"
    SECURITY = "security"
    STORAGE = "storage"
    CONNECTIONS = "connections"
    ERRORS = "errors"
    MAINTENANCE = "maintenance"

@dataclass
class HealthMetric:
    """Represents a single health metric."""
    name: str
    value: float
    unit: str
    status: HealthStatus
    threshold_warning: float
    threshold_critical: float
    description: str
    recommendation: str
    category: MetricType
    timestamp: datetime
    trend: str = "stable"  # "increasing", "decreasing", "stable"

@dataclass
class HealthAlert:
    """Represents a health alert."""
    id: str
    severity: HealthStatus
    title: str
    description: str
    metric_name: str
    value: float
    threshold: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False

class DatabaseHealthAnalyzer:
    """Comprehensive database health analysis and monitoring."""
    
    def __init__(self, db_connection: AzureSQLConnection):
        self.db = db_connection
        self.metrics_history = {}
        self.alerts = []
        self.last_analysis_time = None
        
        # Health thresholds configuration
        self.thresholds = {
            'cpu_percent': {'warning': 70.0, 'critical': 90.0},
            'memory_percent': {'warning': 80.0, 'critical': 95.0},
            'storage_percent': {'warning': 80.0, 'critical': 90.0},
            'connection_count': {'warning': 80.0, 'critical': 95.0},
            'blocked_processes': {'warning': 5.0, 'critical': 10.0},
            'deadlock_count': {'warning': 1.0, 'critical': 5.0},
            'failed_login_rate': {'warning': 10.0, 'critical': 25.0},
            'avg_wait_time': {'warning': 100.0, 'critical': 500.0},
            'index_fragmentation': {'warning': 30.0, 'critical': 50.0}
        }
    
    def analyze_database_health(self) -> Dict[str, Any]:
        """Perform comprehensive database health analysis."""
        logger.info("Starting comprehensive database health analysis...")
        
        try:
            # Collect all health metrics
            metrics = []
            
            # Performance metrics
            metrics.extend(self._analyze_performance_metrics())
            
            # Security metrics
            metrics.extend(self._analyze_security_metrics())
            
            # Storage metrics
            metrics.extend(self._analyze_storage_metrics())
            
            # Connection metrics
            metrics.extend(self._analyze_connection_metrics())
            
            # Error metrics
            metrics.extend(self._analyze_error_metrics())
            
            # Maintenance metrics
            metrics.extend(self._analyze_maintenance_metrics())
            
            # Calculate overall health score
            overall_score, overall_status = self._calculate_overall_health(metrics)
            
            # Generate alerts for critical metrics
            new_alerts = self._generate_alerts(metrics)
            self.alerts.extend(new_alerts)
            
            # Store metrics in history
            current_time = datetime.now()
            self.metrics_history[current_time] = metrics
            self.last_analysis_time = current_time
            
            # Cleanup old history (keep last 24 hours)
            self._cleanup_old_metrics()
            
            health_report = {
                'timestamp': current_time.isoformat(),
                'overall_score': overall_score,
                'overall_status': overall_status.value,
                'metrics': [self._metric_to_dict(m) for m in metrics],
                'metrics_by_category': self._group_metrics_by_category(metrics),
                'alerts': [self._alert_to_dict(a) for a in new_alerts],
                'active_alerts': [self._alert_to_dict(a) for a in self.alerts if not a.resolved],
                'trends': self._calculate_trends(),
                'recommendations': self._generate_recommendations(metrics)
            }
            
            logger.info(f"Health analysis completed. Overall status: {overall_status.value}")
            return health_report
            
        except Exception as e:
            logger.error(f"Failed to analyze database health: {str(e)}")
            return self._get_error_health_report(str(e))
    
    def _analyze_performance_metrics(self) -> List[HealthMetric]:
        """Analyze database performance metrics."""
        metrics = []
        
        try:
            # CPU utilization
            cpu_query = """
            SELECT TOP 10 
                AVG(signal_wait_time_ms * 1.0 / (signal_wait_time_ms + wait_time_ms)) * 100 as avg_cpu_percent
            FROM sys.dm_os_wait_stats 
            WHERE wait_time_ms > 0
            """
            
            cpu_result = self.db.execute_query(cpu_query)
            cpu_percent = cpu_result[0]['avg_cpu_percent'] if cpu_result else 0.0
            
            metrics.append(HealthMetric(
                name="cpu_percent",
                value=cpu_percent,
                unit="%",
                status=self._get_status_from_thresholds(cpu_percent, 'cpu_percent'),
                threshold_warning=self.thresholds['cpu_percent']['warning'],
                threshold_critical=self.thresholds['cpu_percent']['critical'],
                description="Database CPU utilization percentage",
                recommendation=self._get_cpu_recommendation(cpu_percent),
                category=MetricType.PERFORMANCE,
                timestamp=datetime.now()
            ))
            
            # Memory utilization
            memory_query = """
            SELECT 
                (total_physical_memory_kb - available_physical_memory_kb) * 100.0 / total_physical_memory_kb as memory_percent
            FROM sys.dm_os_sys_memory
            """
            
            memory_result = self.db.execute_query(memory_query)
            memory_percent = memory_result[0]['memory_percent'] if memory_result else 0.0
            
            metrics.append(HealthMetric(
                name="memory_percent",
                value=memory_percent,
                unit="%",
                status=self._get_status_from_thresholds(memory_percent, 'memory_percent'),
                threshold_warning=self.thresholds['memory_percent']['warning'],
                threshold_critical=self.thresholds['memory_percent']['critical'],
                description="System memory utilization percentage",
                recommendation=self._get_memory_recommendation(memory_percent),
                category=MetricType.PERFORMANCE,
                timestamp=datetime.now()
            ))
            
            # Average wait time
            wait_query = """
            SELECT TOP 5
                wait_type,
                AVG(wait_time_ms) as avg_wait_time_ms,
                SUM(waiting_tasks_count) as total_waiting_tasks
            FROM sys.dm_os_wait_stats 
            WHERE wait_time_ms > 0
              AND wait_type NOT LIKE 'CLR%'
              AND wait_type NOT LIKE 'SLEEP%'
              AND wait_type NOT LIKE 'LAZYWRITER%'
              AND wait_type NOT LIKE 'XE%'
            GROUP BY wait_type
            ORDER BY AVG(wait_time_ms) DESC
            """
            
            wait_result = self.db.execute_query(wait_query)
            avg_wait_time = wait_result[0]['avg_wait_time_ms'] if wait_result else 0.0
            
            metrics.append(HealthMetric(
                name="avg_wait_time",
                value=avg_wait_time,
                unit="ms",
                status=self._get_status_from_thresholds(avg_wait_time, 'avg_wait_time'),
                threshold_warning=self.thresholds['avg_wait_time']['warning'],
                threshold_critical=self.thresholds['avg_wait_time']['critical'],
                description="Average wait time for database operations",
                recommendation=self._get_wait_time_recommendation(avg_wait_time),
                category=MetricType.PERFORMANCE,
                timestamp=datetime.now()
            ))
            
            # Index fragmentation (sample check)
            fragmentation_query = """
            SELECT TOP 10
                AVG(avg_fragmentation_in_percent) as avg_fragmentation
            FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED')
            WHERE index_id > 0 
              AND page_count > 1000
            """
            
            frag_result = self.db.execute_query(fragmentation_query)
            avg_fragmentation = frag_result[0]['avg_fragmentation'] if frag_result else 0.0
            
            metrics.append(HealthMetric(
                name="index_fragmentation",
                value=avg_fragmentation,
                unit="%",
                status=self._get_status_from_thresholds(avg_fragmentation, 'index_fragmentation'),
                threshold_warning=self.thresholds['index_fragmentation']['warning'],
                threshold_critical=self.thresholds['index_fragmentation']['critical'],
                description="Average index fragmentation percentage",
                recommendation=self._get_fragmentation_recommendation(avg_fragmentation),
                category=MetricType.MAINTENANCE,
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            logger.error(f"Failed to analyze performance metrics: {str(e)}")
        
        return metrics
    
    def _analyze_security_metrics(self) -> List[HealthMetric]:
        """Analyze database security metrics."""
        metrics = []
        
        try:
            # Failed login attempts (last hour)
            failed_login_query = """
            SELECT COUNT(*) as failed_login_count
            FROM sys.fn_get_audit_file('C:\\AuditLogs\\*.sqlaudit', NULL, NULL)
            WHERE event_time >= DATEADD(hour, -1, GETDATE())
              AND action_id = 'LGIF'
            """
            
            try:
                failed_login_result = self.db.execute_query(failed_login_query)
                failed_logins = failed_login_result[0]['failed_login_count'] if failed_login_result else 0
            except:
                # Fallback if audit logs not available
                failed_logins = 0
            
            failed_login_rate = failed_logins  # per hour
            
            metrics.append(HealthMetric(
                name="failed_login_rate",
                value=failed_login_rate,
                unit="per hour",
                status=self._get_status_from_thresholds(failed_login_rate, 'failed_login_rate'),
                threshold_warning=self.thresholds['failed_login_rate']['warning'],
                threshold_critical=self.thresholds['failed_login_rate']['critical'],
                description="Failed login attempts in the last hour",
                recommendation=self._get_security_recommendation(failed_login_rate),
                category=MetricType.SECURITY,
                timestamp=datetime.now()
            ))
            
            # Check for users with excessive privileges
            privilege_query = """
            SELECT COUNT(*) as admin_user_count
            FROM sys.database_role_members rm
            JOIN sys.database_principals rp ON rm.role_principal_id = rp.principal_id
            JOIN sys.database_principals mp ON rm.member_principal_id = mp.principal_id
            WHERE rp.name IN ('db_owner', 'db_securityadmin', 'db_accessadmin')
              AND mp.type = 'S'
            """
            
            privilege_result = self.db.execute_query(privilege_query)
            admin_users = privilege_result[0]['admin_user_count'] if privilege_result else 0
            
            # Simple threshold for admin users
            admin_status = HealthStatus.GOOD if admin_users <= 5 else HealthStatus.WARNING if admin_users <= 10 else HealthStatus.CRITICAL
            
            metrics.append(HealthMetric(
                name="admin_users",
                value=admin_users,
                unit="count",
                status=admin_status,
                threshold_warning=5,
                threshold_critical=10,
                description="Number of users with administrative privileges",
                recommendation="Review administrative privileges and apply principle of least privilege",
                category=MetricType.SECURITY,
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            logger.error(f"Failed to analyze security metrics: {str(e)}")
        
        return metrics
    
    def _analyze_storage_metrics(self) -> List[HealthMetric]:
        """Analyze database storage metrics."""
        metrics = []
        
        try:
            # Database file space usage
            space_query = """
            SELECT 
                SUM(size * 8.0 / 1024) as allocated_mb,
                SUM(FILEPROPERTY(name, 'SpaceUsed') * 8.0 / 1024) as used_mb,
                (SUM(FILEPROPERTY(name, 'SpaceUsed') * 8.0 / 1024) / SUM(size * 8.0 / 1024)) * 100 as usage_percent
            FROM sys.database_files
            WHERE type IN (0,1)
            """
            
            space_result = self.db.execute_query(space_query)
            if space_result:
                allocated_mb = space_result[0]['allocated_mb'] or 0
                used_mb = space_result[0]['used_mb'] or 0
                usage_percent = space_result[0]['usage_percent'] or 0
                
                metrics.append(HealthMetric(
                    name="storage_percent",
                    value=usage_percent,
                    unit="%",
                    status=self._get_status_from_thresholds(usage_percent, 'storage_percent'),
                    threshold_warning=self.thresholds['storage_percent']['warning'],
                    threshold_critical=self.thresholds['storage_percent']['critical'],
                    description=f"Database storage utilization ({used_mb:.1f} MB of {allocated_mb:.1f} MB)",
                    recommendation=self._get_storage_recommendation(usage_percent),
                    category=MetricType.STORAGE,
                    timestamp=datetime.now()
                ))
            
            # Log file size check
            log_query = """
            SELECT 
                SUM(size * 8.0 / 1024) as log_size_mb,
                SUM(FILEPROPERTY(name, 'SpaceUsed') * 8.0 / 1024) as log_used_mb
            FROM sys.database_files
            WHERE type = 1
            """
            
            log_result = self.db.execute_query(log_query)
            if log_result:
                log_size_mb = log_result[0]['log_size_mb'] or 0
                log_used_mb = log_result[0]['log_used_mb'] or 0
                log_usage_percent = (log_used_mb / log_size_mb * 100) if log_size_mb > 0 else 0
                
                metrics.append(HealthMetric(
                    name="log_usage_percent",
                    value=log_usage_percent,
                    unit="%",
                    status=self._get_status_from_thresholds(log_usage_percent, 'storage_percent'),
                    threshold_warning=70.0,
                    threshold_critical=90.0,
                    description=f"Transaction log utilization ({log_used_mb:.1f} MB of {log_size_mb:.1f} MB)",
                    recommendation=self._get_log_recommendation(log_usage_percent),
                    category=MetricType.STORAGE,
                    timestamp=datetime.now()
                ))
                
        except Exception as e:
            logger.error(f"Failed to analyze storage metrics: {str(e)}")
        
        return metrics
    
    def _analyze_connection_metrics(self) -> List[HealthMetric]:
        """Analyze database connection metrics."""
        metrics = []
        
        try:
            # Active connections
            connection_query = """
            SELECT 
                COUNT(*) as active_connections,
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running_connections,
                COUNT(CASE WHEN status = 'sleeping' THEN 1 END) as sleeping_connections
            FROM sys.dm_exec_sessions
            WHERE is_user_process = 1
            """
            
            conn_result = self.db.execute_query(connection_query)
            if conn_result:
                active_connections = conn_result[0]['active_connections'] or 0
                running_connections = conn_result[0]['running_connections'] or 0
                sleeping_connections = conn_result[0]['sleeping_connections'] or 0
                
                # Assume max connections around 100 for percentage calculation
                max_connections = 100
                connection_percent = (active_connections / max_connections) * 100
                
                metrics.append(HealthMetric(
                    name="connection_count",
                    value=active_connections,
                    unit="count",
                    status=self._get_status_from_thresholds(connection_percent, 'connection_count'),
                    threshold_warning=self.thresholds['connection_count']['warning'],
                    threshold_critical=self.thresholds['connection_count']['critical'],
                    description=f"Active database connections ({running_connections} running, {sleeping_connections} sleeping)",
                    recommendation=self._get_connection_recommendation(active_connections),
                    category=MetricType.CONNECTIONS,
                    timestamp=datetime.now()
                ))
            
            # Blocked processes
            blocked_query = """
            SELECT COUNT(*) as blocked_process_count
            FROM sys.dm_exec_requests
            WHERE blocking_session_id > 0
            """
            
            blocked_result = self.db.execute_query(blocked_query)
            blocked_count = blocked_result[0]['blocked_process_count'] if blocked_result else 0
            
            metrics.append(HealthMetric(
                name="blocked_processes",
                value=blocked_count,
                unit="count",
                status=self._get_status_from_thresholds(blocked_count, 'blocked_processes'),
                threshold_warning=self.thresholds['blocked_processes']['warning'],
                threshold_critical=self.thresholds['blocked_processes']['critical'],
                description="Number of currently blocked processes",
                recommendation=self._get_blocking_recommendation(blocked_count),
                category=MetricType.PERFORMANCE,
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            logger.error(f"Failed to analyze connection metrics: {str(e)}")
        
        return metrics
    
    def _analyze_error_metrics(self) -> List[HealthMetric]:
        """Analyze database error metrics."""
        metrics = []
        
        try:
            # Recent errors from error log (if accessible)
            # This is a simplified version - in production, you'd query sys.fn_get_audit_file or error logs
            error_count = 0  # Placeholder
            
            metrics.append(HealthMetric(
                name="recent_errors",
                value=error_count,
                unit="count",
                status=HealthStatus.GOOD if error_count == 0 else HealthStatus.WARNING if error_count < 5 else HealthStatus.CRITICAL,
                threshold_warning=1,
                threshold_critical=5,
                description="Error count in the last hour",
                recommendation="Monitor error logs for patterns and investigate critical errors",
                category=MetricType.ERRORS,
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            logger.error(f"Failed to analyze error metrics: {str(e)}")
        
        return metrics
    
    def _analyze_maintenance_metrics(self) -> List[HealthMetric]:
        """Analyze database maintenance metrics."""
        metrics = []
        
        try:
            # Check statistics update status
            stats_query = """
            SELECT 
                COUNT(*) as total_stats,
                COUNT(CASE WHEN STATS_DATE(object_id, stats_id) < DATEADD(day, -7, GETDATE()) THEN 1 END) as outdated_stats
            FROM sys.stats s
            JOIN sys.objects o ON s.object_id = o.object_id
            WHERE o.type = 'U'
            """
            
            stats_result = self.db.execute_query(stats_query)
            if stats_result:
                total_stats = stats_result[0]['total_stats'] or 0
                outdated_stats = stats_result[0]['outdated_stats'] or 0
                outdated_percent = (outdated_stats / total_stats * 100) if total_stats > 0 else 0
                
                metrics.append(HealthMetric(
                    name="outdated_statistics",
                    value=outdated_percent,
                    unit="%",
                    status=HealthStatus.GOOD if outdated_percent < 10 else HealthStatus.WARNING if outdated_percent < 25 else HealthStatus.CRITICAL,
                    threshold_warning=10,
                    threshold_critical=25,
                    description=f"Percentage of outdated statistics ({outdated_stats} of {total_stats})",
                    recommendation="Update statistics to maintain optimal query performance",
                    category=MetricType.MAINTENANCE,
                    timestamp=datetime.now()
                ))
            
        except Exception as e:
            logger.error(f"Failed to analyze maintenance metrics: {str(e)}")
        
        return metrics
    
    def _get_status_from_thresholds(self, value: float, metric_name: str) -> HealthStatus:
        """Determine health status based on thresholds."""
        thresholds = self.thresholds.get(metric_name, {'warning': 80, 'critical': 90})
        
        if value >= thresholds['critical']:
            return HealthStatus.CRITICAL
        elif value >= thresholds['warning']:
            return HealthStatus.WARNING
        else:
            return HealthStatus.GOOD
    
    def _calculate_overall_health(self, metrics: List[HealthMetric]) -> Tuple[float, HealthStatus]:
        """Calculate overall health score and status."""
        if not metrics:
            return 0.0, HealthStatus.UNKNOWN
        
        # Weight different metric categories
        category_weights = {
            MetricType.PERFORMANCE: 0.3,
            MetricType.SECURITY: 0.2,
            MetricType.STORAGE: 0.2,
            MetricType.CONNECTIONS: 0.15,
            MetricType.ERRORS: 0.1,
            MetricType.MAINTENANCE: 0.05
        }
        
        # Score mapping
        status_scores = {
            HealthStatus.EXCELLENT: 100,
            HealthStatus.GOOD: 80,
            HealthStatus.WARNING: 50,
            HealthStatus.CRITICAL: 20,
            HealthStatus.UNKNOWN: 0
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for category in category_weights:
            category_metrics = [m for m in metrics if m.category == category]
            if category_metrics:
                category_score = sum(status_scores[m.status] for m in category_metrics) / len(category_metrics)
                weighted_score += category_score * category_weights[category]
                total_weight += category_weights[category]
        
        if total_weight > 0:
            overall_score = weighted_score / total_weight
        else:
            overall_score = 0.0
        
        # Determine overall status
        if overall_score >= 85:
            overall_status = HealthStatus.EXCELLENT
        elif overall_score >= 70:
            overall_status = HealthStatus.GOOD
        elif overall_score >= 50:
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.CRITICAL
        
        return overall_score, overall_status
    
    def _generate_alerts(self, metrics: List[HealthMetric]) -> List[HealthAlert]:
        """Generate alerts for metrics exceeding thresholds."""
        alerts = []
        
        for metric in metrics:
            if metric.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
                alert_id = f"{metric.name}_{int(time.time())}"
                threshold = metric.threshold_critical if metric.status == HealthStatus.CRITICAL else metric.threshold_warning
                
                alert = HealthAlert(
                    id=alert_id,
                    severity=metric.status,
                    title=f"{metric.name.replace('_', ' ').title()} {metric.status.value.title()}",
                    description=f"{metric.description}: {metric.value}{metric.unit} (threshold: {threshold}{metric.unit})",
                    metric_name=metric.name,
                    value=metric.value,
                    threshold=threshold,
                    timestamp=datetime.now()
                )
                
                alerts.append(alert)
        
        return alerts
    
    def _group_metrics_by_category(self, metrics: List[HealthMetric]) -> Dict[str, List[Dict]]:
        """Group metrics by category for dashboard display."""
        grouped = {}
        
        for metric in metrics:
            category_name = metric.category.value
            if category_name not in grouped:
                grouped[category_name] = []
            
            grouped[category_name].append(self._metric_to_dict(metric))
        
        return grouped
    
    def _calculate_trends(self) -> Dict[str, str]:
        """Calculate trends for key metrics."""
        trends = {}
        
        if len(self.metrics_history) < 2:
            return trends
        
        # Get last two data points
        timestamps = sorted(self.metrics_history.keys())
        if len(timestamps) >= 2:
            current_metrics = self.metrics_history[timestamps[-1]]
            previous_metrics = self.metrics_history[timestamps[-2]]
            
            # Create lookup for previous metrics
            prev_lookup = {m.name: m.value for m in previous_metrics}
            
            for metric in current_metrics:
                if metric.name in prev_lookup:
                    current_val = metric.value
                    previous_val = prev_lookup[metric.name]
                    
                    if current_val > previous_val * 1.1:  # 10% increase
                        trends[metric.name] = "increasing"
                    elif current_val < previous_val * 0.9:  # 10% decrease
                        trends[metric.name] = "decreasing"
                    else:
                        trends[metric.name] = "stable"
        
        return trends
    
    def _generate_recommendations(self, metrics: List[HealthMetric]) -> List[str]:
        """Generate health recommendations based on metrics."""
        recommendations = []
        
        critical_metrics = [m for m in metrics if m.status == HealthStatus.CRITICAL]
        warning_metrics = [m for m in metrics if m.status == HealthStatus.WARNING]
        
        if critical_metrics:
            recommendations.append("🚨 URGENT: Address critical issues immediately to prevent service degradation")
            
        if warning_metrics:
            recommendations.append("⚠️ Monitor warning-level metrics closely and plan remediation")
            
        # Specific recommendations based on metric patterns
        perf_metrics = [m for m in metrics if m.category == MetricType.PERFORMANCE and m.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]]
        if perf_metrics:
            recommendations.append("📈 Consider performance tuning: index optimization, query analysis, resource scaling")
            
        storage_metrics = [m for m in metrics if m.category == MetricType.STORAGE and m.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]]
        if storage_metrics:
            recommendations.append("💾 Storage attention needed: cleanup old data, archive logs, expand storage")
            
        security_metrics = [m for m in metrics if m.category == MetricType.SECURITY and m.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]]
        if security_metrics:
            recommendations.append("🔒 Security review required: audit failed logins, review privileges")
        
        if not recommendations:
            recommendations.append("✅ System health is good - maintain regular monitoring")
            
        return recommendations
    
    def _metric_to_dict(self, metric: HealthMetric) -> Dict[str, Any]:
        """Convert HealthMetric to dictionary."""
        return {
            'name': metric.name,
            'value': metric.value,
            'unit': metric.unit,
            'status': metric.status.value,
            'threshold_warning': metric.threshold_warning,
            'threshold_critical': metric.threshold_critical,
            'description': metric.description,
            'recommendation': metric.recommendation,
            'category': metric.category.value,
            'timestamp': metric.timestamp.isoformat(),
            'trend': metric.trend
        }
    
    def _alert_to_dict(self, alert: HealthAlert) -> Dict[str, Any]:
        """Convert HealthAlert to dictionary."""
        return {
            'id': alert.id,
            'severity': alert.severity.value,
            'title': alert.title,
            'description': alert.description,
            'metric_name': alert.metric_name,
            'value': alert.value,
            'threshold': alert.threshold,
            'timestamp': alert.timestamp.isoformat(),
            'acknowledged': alert.acknowledged,
            'resolved': alert.resolved
        }
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than 24 hours."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        timestamps_to_remove = [
            ts for ts in self.metrics_history.keys() 
            if ts < cutoff_time
        ]
        
        for ts in timestamps_to_remove:
            del self.metrics_history[ts]
    
    def _get_error_health_report(self, error_message: str) -> Dict[str, Any]:
        """Return error health report when analysis fails."""
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_score': 0.0,
            'overall_status': HealthStatus.UNKNOWN.value,
            'metrics': [],
            'metrics_by_category': {},
            'alerts': [],
            'active_alerts': [],
            'trends': {},
            'recommendations': [f"⚠️ Health analysis failed: {error_message}"],
            'error': error_message
        }
    
    # Recommendation helper methods
    def _get_cpu_recommendation(self, cpu_percent: float) -> str:
        if cpu_percent > 90:
            return "Critical: Investigate high CPU processes, consider scaling resources"
        elif cpu_percent > 70:
            return "Monitor CPU usage patterns, optimize queries, consider load balancing"
        else:
            return "CPU utilization is within acceptable range"
    
    def _get_memory_recommendation(self, memory_percent: float) -> str:
        if memory_percent > 95:
            return "Critical: Add more memory or optimize memory-intensive processes"
        elif memory_percent > 80:
            return "Monitor memory usage, check for memory leaks, optimize buffer pool"
        else:
            return "Memory utilization is healthy"
    
    def _get_storage_recommendation(self, storage_percent: float) -> str:
        if storage_percent > 90:
            return "Critical: Expand storage immediately or clean up old data"
        elif storage_percent > 80:
            return "Plan storage expansion, archive old data, implement retention policies"
        else:
            return "Storage utilization is acceptable"
    
    def _get_log_recommendation(self, log_percent: float) -> str:
        if log_percent > 90:
            return "Critical: Transaction log is nearly full - backup and shrink immediately"
        elif log_percent > 70:
            return "Schedule more frequent log backups, consider log file size adjustment"
        else:
            return "Transaction log size is manageable"
    
    def _get_connection_recommendation(self, connection_count: int) -> str:
        if connection_count > 80:
            return "High connection count - implement connection pooling and review connection lifecycle"
        elif connection_count > 50:
            return "Monitor connection patterns and optimize connection usage"
        else:
            return "Connection count is within normal range"
    
    def _get_blocking_recommendation(self, blocked_count: int) -> str:
        if blocked_count > 10:
            return "Critical: Multiple blocked processes - investigate locking issues immediately"
        elif blocked_count > 0:
            return "Some processes are blocked - review long-running transactions and indexing"
        else:
            return "No blocking issues detected"
    
    def _get_wait_time_recommendation(self, wait_time: float) -> str:
        if wait_time > 500:
            return "Critical: High wait times - investigate I/O, locking, and resource contention"
        elif wait_time > 100:
            return "Monitor wait statistics and optimize queries causing high wait times"
        else:
            return "Wait times are acceptable"
    
    def _get_fragmentation_recommendation(self, fragmentation: float) -> str:
        if fragmentation > 50:
            return "Critical: High index fragmentation - rebuild indexes immediately"
        elif fragmentation > 30:
            return "Plan index maintenance - reorganize or rebuild fragmented indexes"
        else:
            return "Index fragmentation is within acceptable limits"
    
    def _get_security_recommendation(self, failed_logins: float) -> str:
        if failed_logins > 25:
            return "Critical: High failed login rate - investigate potential brute force attacks"
        elif failed_logins > 10:
            return "Monitor failed login patterns and review security policies"
        else:
            return "Failed login rate is normal"
    
    def get_historical_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get historical metrics data for charting."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        historical_data = {
            'timestamps': [],
            'metrics': {}
        }
        
        for timestamp, metrics in sorted(self.metrics_history.items()):
            if timestamp >= cutoff_time:
                historical_data['timestamps'].append(timestamp.isoformat())
                
                for metric in metrics:
                    if metric.name not in historical_data['metrics']:
                        historical_data['metrics'][metric.name] = []
                    
                    historical_data['metrics'][metric.name].append({
                        'value': metric.value,
                        'status': metric.status.value
                    })
        
        return historical_data
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                return True
        return False