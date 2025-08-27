#!/usr/bin/env python3
"""
Connection Profile Manager
=========================

Handles saving, loading, and managing connection profiles for the Azure SQL Database
Documentation Generator. Provides functionality to store multiple database
connection configurations for quick access.

Features:
- Save/load connection profiles
- Connection history tracking
- Profile validation
- Secure password handling
- Profile import/export
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConnectionProfileManager:
    """Manages connection profiles and history."""
    
    def __init__(self, profiles_dir: str = "profiles"):
        """Initialize the profile manager.
        
        Args:
            profiles_dir: Directory to store profile files
        """
        self.profiles_dir = Path(profiles_dir)
        self.profiles_file = self.profiles_dir / "connection_profiles.json"
        self.history_file = self.profiles_dir / "connection_history.json"
        
        # Create profiles directory if it doesn't exist
        self.profiles_dir.mkdir(exist_ok=True)
        
        # Initialize profile storage
        self._profiles = self._load_profiles()
        self._history = self._load_history()
    
    def _load_profiles(self) -> Dict[str, Any]:
        """Load profiles from file."""
        if not self.profiles_file.exists():
            return {}
        
        try:
            with open(self.profiles_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
            return {}
    
    def _save_profiles(self):
        """Save profiles to file."""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self._profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
            raise
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load connection history from file."""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return []
    
    def _save_history(self):
        """Save connection history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self._history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
    
    def save_profile(self, name: str, connection_config: Dict[str, Any], 
                    documentation_config: Optional[Dict[str, Any]] = None) -> bool:
        """Save a connection profile.
        
        Args:
            name: Profile name (must be unique)
            connection_config: Connection configuration dictionary
            documentation_config: Optional documentation configuration
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Validate profile name
            if not name or not name.strip():
                raise ValueError("Profile name cannot be empty")
            
            # Create profile data
            profile_data = {
                'name': name.strip(),
                'connection': connection_config.copy(),
                'documentation': documentation_config.copy() if documentation_config else {},
                'created_at': datetime.now().isoformat(),
                'last_used': None
            }
            
            # Remove sensitive data for display purposes but keep for connection
            display_config = connection_config.copy()
            if 'password' in display_config:
                display_config['password'] = '***masked***'
            if 'client_secret' in display_config:
                display_config['client_secret'] = '***masked***'
            
            profile_data['display_connection'] = display_config
            
            # Save profile
            self._profiles[name.strip()] = profile_data
            self._save_profiles()
            
            logger.info(f"Profile '{name}' saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save profile '{name}': {e}")
            return False
    
    def load_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a connection profile.
        
        Args:
            name: Profile name
            
        Returns:
            Profile data dictionary or None if not found
        """
        profile = self._profiles.get(name)
        if profile:
            # Update last used timestamp
            profile['last_used'] = datetime.now().isoformat()
            self._save_profiles()
            logger.info(f"Profile '{name}' loaded successfully")
        
        return profile
    
    def delete_profile(self, name: str) -> bool:
        """Delete a connection profile.
        
        Args:
            name: Profile name
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if name in self._profiles:
                del self._profiles[name]
                self._save_profiles()
                logger.info(f"Profile '{name}' deleted successfully")
                return True
            else:
                logger.warning(f"Profile '{name}' not found")
                return False
        except Exception as e:
            logger.error(f"Failed to delete profile '{name}': {e}")
            return False
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """Get list of all profiles with metadata.
        
        Returns:
            List of profile metadata (without sensitive connection details)
        """
        profiles = []
        for name, data in self._profiles.items():
            profile_info = {
                'name': name,
                'server': data['connection'].get('server', 'Unknown'),
                'database': data['connection'].get('database', 'Unknown'),
                'method': data['connection'].get('method', 'Unknown'),
                'created_at': data.get('created_at'),
                'last_used': data.get('last_used')
            }
            profiles.append(profile_info)
        
        # Sort by last used (most recent first), then by name
        profiles.sort(key=lambda x: (x['last_used'] or '0000-00-00', x['name']), reverse=True)
        return profiles
    
    def add_to_history(self, connection_config: Dict[str, Any], 
                      success: bool = True, error_message: str = None):
        """Add a connection attempt to history.
        
        Args:
            connection_config: Connection configuration used
            success: Whether the connection was successful
            error_message: Error message if connection failed
        """
        try:
            # Create history entry
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'server': connection_config.get('server', 'Unknown'),
                'database': connection_config.get('database', 'Unknown'),
                'method': connection_config.get('method', 'Unknown'),
                'username': connection_config.get('username', 'Unknown'),
                'success': success,
                'error_message': error_message
            }
            
            # Add to history (keep only last 50 entries)
            self._history.append(history_entry)
            self._history = self._history[-50:]  # Keep last 50 entries
            
            self._save_history()
            
        except Exception as e:
            logger.error(f"Failed to add to history: {e}")
    
    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get connection history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent connection history entries
        """
        return list(reversed(self._history[-limit:]))
    
    def get_recent_connections(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent successful connections for quick access.
        
        Args:
            limit: Maximum number of connections to return
            
        Returns:
            List of recent successful connection configurations
        """
        recent = []
        seen_connections = set()
        
        for entry in reversed(self._history):
            if not entry.get('success'):
                continue
                
            # Create unique identifier for connection
            conn_id = f"{entry['server']}|{entry['database']}|{entry['method']}|{entry['username']}"
            
            if conn_id not in seen_connections:
                seen_connections.add(conn_id)
                recent.append({
                    'server': entry['server'],
                    'database': entry['database'],
                    'method': entry['method'],
                    'username': entry['username'],
                    'last_used': entry['timestamp']
                })
                
                if len(recent) >= limit:
                    break
        
        return recent
    
    def export_profiles(self, file_path: str, profile_names: List[str] = None) -> bool:
        """Export profiles to a file.
        
        Args:
            file_path: Path to export file
            profile_names: List of profile names to export (None = all)
            
        Returns:
            True if exported successfully, False otherwise
        """
        try:
            profiles_to_export = {}
            
            if profile_names is None:
                profiles_to_export = self._profiles.copy()
            else:
                for name in profile_names:
                    if name in self._profiles:
                        profiles_to_export[name] = self._profiles[name]
            
            # Remove sensitive data from export
            sanitized_profiles = {}
            for name, profile in profiles_to_export.items():
                sanitized = profile.copy()
                if 'connection' in sanitized:
                    conn = sanitized['connection'].copy()
                    if 'password' in conn:
                        conn['password'] = ''
                    if 'client_secret' in conn:
                        conn['client_secret'] = ''
                    sanitized['connection'] = conn
                sanitized_profiles[name] = sanitized
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sanitized_profiles, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(sanitized_profiles)} profiles to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export profiles: {e}")
            return False
    
    def import_profiles(self, file_path: str, overwrite: bool = False) -> Dict[str, Any]:
        """Import profiles from a file.
        
        Args:
            file_path: Path to import file
            overwrite: Whether to overwrite existing profiles
            
        Returns:
            Dictionary with import results {'imported': int, 'skipped': int, 'errors': []}
        """
        result = {'imported': 0, 'skipped': 0, 'errors': []}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_profiles = json.load(f)
            
            for name, profile in imported_profiles.items():
                try:
                    if name in self._profiles and not overwrite:
                        result['skipped'] += 1
                        continue
                    
                    # Validate profile structure
                    if 'connection' not in profile:
                        result['errors'].append(f"Profile '{name}' missing connection config")
                        continue
                    
                    self._profiles[name] = profile
                    result['imported'] += 1
                    
                except Exception as e:
                    result['errors'].append(f"Failed to import '{name}': {e}")
            
            if result['imported'] > 0:
                self._save_profiles()
            
            logger.info(f"Import completed: {result['imported']} imported, {result['skipped']} skipped")
            
        except Exception as e:
            result['errors'].append(f"Failed to read import file: {e}")
            logger.error(f"Failed to import profiles: {e}")
        
        return result
    
    def validate_profile(self, profile_data: Dict[str, Any]) -> List[str]:
        """Validate a profile configuration.
        
        Args:
            profile_data: Profile data to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        if 'connection' not in profile_data:
            errors.append("Missing connection configuration")
            return errors
        
        connection = profile_data['connection']
        
        # Validate based on connection method
        method = connection.get('method', '')
        
        if method == 'credentials':
            required = ['server', 'database', 'username', 'password']
            for field in required:
                if not connection.get(field):
                    errors.append(f"Missing required field: {field}")
        
        elif method == 'azure_ad':
            required = ['server', 'database']
            for field in required:
                if not connection.get(field):
                    errors.append(f"Missing required field: {field}")
        
        elif method == 'service_principal':
            required = ['server', 'database', 'client_id', 'client_secret', 'tenant_id']
            for field in required:
                if not connection.get(field):
                    errors.append(f"Missing required field: {field}")
        
        elif method == 'connection_string':
            if not connection.get('connection_string'):
                errors.append("Missing connection string")
        
        else:
            errors.append(f"Unknown connection method: {method}")
        
        return errors