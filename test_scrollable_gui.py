#!/usr/bin/env python3
"""
Test Scrollable GUI Components
==============================

Test the scrollable frame functionality and ensure all GUI components
are accessible with proper scrolling on different screen sizes.
"""

import tkinter as tk
from tkinter import ttk
from ui_framework import ScrollableFrame, ThemeManager, StatusManager

def test_scrollable_frame():
    """Test basic scrollable frame functionality."""
    root = tk.Tk()
    root.title("Scrollable Frame Test")
    root.geometry("600x400")
    
    # Create theme manager
    theme_manager = ThemeManager()
    theme_manager.initialize_styles(ttk.Style())
    
    # Create scrollable frame
    scrollable = ScrollableFrame(root)
    scrollable.pack(fill='both', expand=True)
    
    # Add content to test scrolling
    content_frame = scrollable.get_frame()
    
    # Add header
    ttk.Label(content_frame, text="Scrollable Content Test", 
             style='Title.TLabel').pack(pady=20)
    
    # Add multiple sections to force scrolling
    for i in range(20):
        section_frame = ttk.LabelFrame(content_frame, text=f"Section {i+1}", 
                                     style='TLabelFrame', padding="15")
        section_frame.pack(fill='x', pady=10, padx=20)
        
        ttk.Label(section_frame, text=f"This is section {i+1} content.", 
                 style='Body.TLabel').pack(anchor='w', pady=5)
        
        # Add some form elements
        form_frame = ttk.Frame(section_frame)
        form_frame.pack(fill='x', pady=5)
        
        ttk.Label(form_frame, text="Sample Field:", style='Body.TLabel').pack(anchor='w')
        entry = ttk.Entry(form_frame, style='TEntry')
        entry.pack(fill='x', pady=(2, 5))
        entry.insert(0, f"Sample data for section {i+1}")
        
        # Add buttons
        button_frame = ttk.Frame(section_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="Action 1", 
                  style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Action 2", 
                  style='Secondary.TButton').pack(side='left')
    
    # Add footer
    ttk.Label(content_frame, text="End of content - scrolling test complete", 
             style='Caption.TLabel').pack(pady=20)
    
    # Instructions
    instructions = ttk.Label(root, 
                           text="Use mouse wheel to scroll • Content should be fully accessible",
                           style='Caption.TLabel')
    instructions.pack(side='bottom', pady=5)
    
    print("Scrollable frame test started")
    print("Instructions:")
    print("• Use mouse wheel to scroll up and down")
    print("• Verify all content is accessible")
    print("• Test with different window sizes")
    print("• Check that scrollbars appear when needed")
    
    root.mainloop()

def test_modern_gui_import():
    """Test that the modern GUI can import with scrollable updates."""
    try:
        import modern_gui
        print("[OK] Modern GUI imports successfully with scrollable updates")
        return True
    except Exception as e:
        print(f"[FAIL] Modern GUI import failed: {e}")
        return False

def main():
    """Run scrollable GUI tests."""
    print("Testing Scrollable GUI Components")
    print("=" * 40)
    
    # Test modern GUI import
    gui_import_ok = test_modern_gui_import()
    
    if gui_import_ok:
        print("\n[OK] All import tests passed!")
        print("\nStarting interactive scrollable frame test...")
        print("Close the test window when finished.")
        
        # Start interactive test
        test_scrollable_frame()
    else:
        print("\n[FAIL] Cannot run interactive tests due to import failures")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())