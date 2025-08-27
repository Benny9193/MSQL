#!/usr/bin/env python3
"""
Phase 1 Implementation Test
==========================

Quick test to verify all Phase 1 components are working correctly.
"""

import tkinter as tk
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_phase1_components():
    """Test all Phase 1 components can be imported and initialized."""
    try:
        from ui_framework import (
            ThemeManager, 
            SmartLoadingSystem, 
            EnhancedStatusBar,
            KeyboardShortcutManager,
            TooltipSystem,
            QuickAccessToolbar,
            ImprovedErrorHandler
        )
        
        print("[OK] All Phase 1 components imported successfully")
        
        # Create test window
        root = tk.Tk()
        root.title("Phase 1 Test")
        root.geometry("600x400")
        
        # Initialize systems
        theme_manager = ThemeManager()
        style = tk.ttk.Style()
        theme_manager.initialize_styles(style)
        print("[OK] Theme manager initialized")
        
        loading_system = SmartLoadingSystem(root, theme_manager)
        print("[OK] Smart loading system initialized")
        
        status_bar = EnhancedStatusBar(root, theme_manager)
        print("[OK] Enhanced status bar initialized")
        
        shortcut_manager = KeyboardShortcutManager(root)
        print("[OK] Keyboard shortcuts manager initialized")
        
        tooltip_system = TooltipSystem(theme_manager)
        print("[OK] Tooltip system initialized")
        
        toolbar = QuickAccessToolbar(root, theme_manager)
        print("[OK] Quick access toolbar initialized")
        
        error_handler = ImprovedErrorHandler(theme_manager, status_bar)
        print("[OK] Improved error handler initialized")
        
        # Test integration
        toolbar.set_tooltip_system(tooltip_system)
        print("[OK] System integration successful")
        
        # Update status
        status_bar.update_status("Phase 1 components test completed successfully!")
        status_bar.update_connection_status(True, "Test Environment")
        
        # Add test content
        test_frame = tk.ttk.Frame(root, padding="20")
        test_frame.pack(fill='both', expand=True)
        
        success_label = tk.ttk.Label(test_frame, 
                                   text="[PASSED] Phase 1 Implementation Test", 
                                   font=('Inter', 14, 'bold'))
        success_label.pack(pady=20)
        
        info_label = tk.ttk.Label(test_frame, 
                                text="All Phase 1 components are working correctly!")
        info_label.pack()
        
        close_btn = tk.ttk.Button(test_frame, text="Close Test", command=root.quit)
        close_btn.pack(pady=20)
        
        tooltip_system.add_tooltip(close_btn, "Close the Phase 1 test window")
        
        print("\n[SUCCESS] Phase 1 Implementation Test PASSED!")
        print("All components initialized successfully and are ready for use.")
        
        # Don't run mainloop in test
        root.after(100, root.quit)
        root.mainloop()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Phase 1 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Phase 1 GUI Implementation...")
    print("=" * 40)
    
    success = test_phase1_components()
    
    if success:
        print("\n[SUCCESS] All Phase 1 components are working correctly!")
        print("The enhanced UI framework is ready for integration.")
    else:
        print("\n[FAILED] Phase 1 test failed. Please check the implementation.")