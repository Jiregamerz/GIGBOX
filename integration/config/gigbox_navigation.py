#!/usr/bin/python3
# -*- coding: utf-8 -*-
# GIGBOX On-Screen Navigation Controls
# SPOOKI INSTRUMENTS - GIGBOX
# Removes on-screen directional arrows (UP/DOWN/LEFT/RIGHT)
# Reflows remaining controls for clean 800x480 layout
# Physical navigation module is primary directional input

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Tuple, Callable
import logging

logger = logging.getLogger(__name__)

class GigboxNavigation:
    """Manages on-screen navigation controls for GIGBOX
    
    REMOVES: On-screen UP/DOWN/LEFT/RIGHT arrow buttons
    KEEPS:   SELECT, BACK, MENU, and other functional controls
    REFLOWS: Remaining controls to use freed space cleanly
    """
    
    # GIGBOX color constants
    BG_DARK = "#030303"
    BG_PANEL = "#080808"
    NEON_RED = "#ff1744"
    NEON_RED_GLOW = "#ff3355"
    NEON_RED_DIM = "#2a0508"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b0b0b0"
    BORDER_NORM = "#2a2a2a"
    PCB_TRACE = "#2a0808"
    
    def __init__(self, parent: tk.Widget, screen_width: int = 800, screen_height: int = 480):
        self.parent = parent
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Navigation button references (to be removed/hidden)
        self.nav_buttons = {}  # 'up', 'down', 'left', 'right' -> widget
        self.nav_container = None
        
        # Remaining control buttons
        self.control_buttons = {}  # name -> widget
        self.control_container = None
        
        # Layout configuration
        self.layout_config = self._get_layout_config()
        
    def _get_layout_config(self) -> Dict:
        """Get GIGBOX-specific layout configuration"""
        return {
            # Button dimensions (optimized for 800x480)
            'button_width': 80,
            'button_height': 48,
            'button_spacing': 8,
            'button_font_size': 10,
            
            # Container positioning
            'control_area_bottom': 60,  # Height reserved for bottom controls
            'control_area_sides': 120,  # Width reserved for side controls
            
            # Colors
            'bg': self.BG_DARK,
            'panel_bg': self.BG_PANEL,
            'accent': self.NEON_RED,
            'accent_glow': self.NEON_RED_GLOW,
            'accent_dim': self.NEON_RED_DIM,
            'text': self.TEXT_PRIMARY,
            'text_dim': self.TEXT_SECONDARY,
            'border': self.BORDER_NORM,
            'pcb': self.PCB_TRACE,
        }
    
    def remove_on_screen_arrows(self, zyngui_instance):
        """Remove the four directional arrow buttons from Zynthian UI
        
        This is the key function - it finds and removes/hides the
        on-screen directional navigation arrows that are redundant
        with the physical navigation module.
        """
        logger.info("Removing on-screen directional arrows...")
        
        # Method 1: Find and destroy arrow widgets in zyngui
        arrow_attrs = [
            'up_button', 'down_button', 'left_button', 'right_button',
            'nav_up', 'nav_down', 'nav_left', 'nav_right',
            'arrow_up', 'arrow_down', 'arrow_left', 'arrow_right',
        ]
        
        for attr in arrow_attrs:
            if hasattr(zyngui_instance, attr):
                widget = getattr(zyngui_instance, attr)
                if widget and hasattr(widget, 'destroy'):
                    try:
                        widget.destroy()
                        logger.info(f"Destroyed {attr}")
                    except:
                        pass
                setattr(zyngui_instance, attr, None)
        
        # Method 2: Find arrow buttons in control frame
        if hasattr(zyngui_instance, 'control_frame'):
            self._remove_arrows_from_container(zyngui_instance.control_frame)
        
        # Method 3: Search all widgets for arrow-like buttons
        self._remove_arrows_recursive(zyngui_instance.root if hasattr(zyngui_instance, 'root') else self.parent)
        
        logger.info("On-screen directional arrows removed")
    
    def _remove_arrows_from_container(self, container):
        """Remove arrow buttons from a specific container"""
        if not container:
            return
            
        for child in container.winfo_children():
            # Check if it's an arrow button
            if self._is_arrow_button(child):
                try:
                    child.destroy()
                    logger.info(f"Destroyed arrow button: {child}")
                except:
                    pass
            elif hasattr(child, 'winfo_children'):
                # Recurse into sub-containers
                self._remove_arrows_from_container(child)
    
    def _remove_arrows_recursive(self, widget):
        """Recursively search and remove arrow buttons"""
        if not widget:
            return
            
        try:
            children = widget.winfo_children()
        except:
            return
            
        for child in children:
            if self._is_arrow_button(child):
                try:
                    child.destroy()
                    logger.info(f"Destroyed arrow button: {child}")
                except:
                    pass
            elif hasattr(child, 'winfo_children'):
                self._remove_arrows_recursive(child)
    
    def _is_arrow_button(self, widget) -> bool:
        """Check if a widget is an on-screen arrow navigation button"""
        try:
            # Check widget class/text
            widget_class = widget.winfo_class()
            widget_text = ""
            if hasattr(widget, 'cget'):
                try:
                    widget_text = widget.cget('text') or ""
                except:
                    pass
            
            # Arrow indicators
            arrow_indicators = ['↑', '↓', '←', '→', 'UP', 'DOWN', 'LEFT', 'RIGHT']
            
            # Check text
            if any(ind in str(widget_text).upper() for ind in arrow_indicators):
                # Additional check: small button, likely navigation
                width = widget.winfo_width()
                height = widget.winfo_height()
                if width < 100 and height < 100:
                    return True
            
            # Check image/file name if it's an image button
            if hasattr(widget, 'image') and widget.image:
                img_str = str(widget.image)
                if any(x in img_str.lower() for x in ['arrow', 'up', 'down', 'left', 'right', 'nav']):
                    return True
                    
        except:
            pass
            
        return False
    
    def create_reflowed_controls(self, zyngui_instance, 
                                  on_select: Callable = None,
                                  on_back: Callable = None,
                                  on_menu: Callable = None,
                                  on_mod_ui: Callable = None):
        """Create reflowed on-screen controls without directional arrows
        
        Layout for 800x480:
        ┌─────────────────────────────────────────────────────────┐
        │  Top Bar (status, CPU, etc.)                            │
        ├─────────────┬───────────────────────────┬───────────────┤
        │             │                           │  Side Controls│
        │  Main List  │    Parameter/Edit Area    │  [MIXER]      │
        │             │                           │  [MOD UI]     │
        │             │                           │  [QUICK EDIT] │
        ├─────────────┴───────────────────────────┴───────────────┤
        │  Bottom Controls (reflowed - no arrows)                 │
        │  [BACK]    [SELECT]    [SNAPSHOT]   [LAYER]   [PANIC]  │
        └─────────────────────────────────────────────────────────┘
        """
        config = self.layout_config
        
        # Remove old control frame if exists
        if hasattr(zyngui_instance, 'control_frame') and zyngui_instance.control_frame:
            try:
                zyngui_instance.control_frame.destroy()
            except:
                pass
        
        # Create new control frame at bottom
        control_frame = tk.Frame(
            zyngui_instance.root if hasattr(zyngui_instance, 'root') else self.parent,
            bg=config['bg'],
            height=config['control_area_bottom'],
            highlightthickness=0
        )
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
        control_frame.pack_propagate(False)
        
        # Add PCB trace decoration at top of control frame
        pcb_line = tk.Frame(control_frame, bg=config['pcb'], height=1)
        pcb_line.pack(fill=tk.X, padx=20, pady=(0, 4))
        
        # Button container
        btn_container = tk.Frame(control_frame, bg=config['bg'])
        btn_container.pack(expand=True, fill=tk.BOTH, padx=16, pady=8)
        
        # Define reflowed buttons (NO directional arrows!)
        buttons = [
            # (name, text, command, style_variant)
            ('back', 'BACK', on_back or self._default_back, 'secondary'),
            ('select', 'SELECT', on_select or self._default_select, 'primary'),
            ('snapshot', 'SNAPSHOT', lambda: self._trigger_action(zyngui_instance, 'SNAPSHOT_MENU'), 'secondary'),
            ('layer', 'LAYER', lambda: self._trigger_action(zyngui_instance, 'LAYER_MENU'), 'secondary'),
            ('panic', 'PANIC', lambda: self._trigger_action(zyngui_instance, 'PANIC'), 'destructive'),
        ]
        
        # Calculate button width to fill space evenly
        num_buttons = len(buttons)
        spacing = config['button_spacing']
        total_spacing = spacing * (num_buttons - 1)
        available_width = self.screen_width - 32 - total_spacing  # 16px padding each side
        button_width = max(60, available_width // num_buttons)
        
        for i, (name, text, command, style) in enumerate(buttons):
            btn = self._create_styled_button(
                btn_container,
                text=text,
                command=command,
                style=style,
                width=button_width,
                height=config['button_height'],
                font_size=config['button_font_size']
            )
            btn.pack(side=tk.LEFT, padx=(0 if i == num_buttons - 1 else spacing), pady=0)
            self.control_buttons[name] = btn
        
        # Store reference
        self.control_container = control_frame
        zyngui_instance.gigbox_control_frame = control_frame
        
        logger.info(f"Created {num_buttons} reflowed control buttons (no arrows)")
        return control_frame
    
    def _create_styled_button(self, parent, text: str, command: Callable,
                              style: str = 'secondary', width: int = 80,
                              height: int = 48, font_size: int = 10) -> tk.Button:
        """Create a GIGBOX-styled button"""
        config = self.layout_config
        
        if style == 'primary':
            bg = config['accent_dim']
            fg = config['accent_glow']
            active_bg = config['accent']
            active_fg = config['text']
            border_color = config['accent']
        elif style == 'destructive':
            bg = "#2a0508"
            fg = "#ff6677"
            active_bg = config['accent']
            active_fg = config['text']
            border_color = "#aa0011"
        else:  # secondary
            bg = config['panel_bg']
            fg = config['text']
            active_bg = config['bg_highlight']
            active_fg = config['accent_glow']
            border_color = config['border']
        
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Audiowide", font_size),
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=active_fg,
            bd=1,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=border_color,
            highlightcolor=config['accent'],
            cursor="hand2" if config.get('force_cursor', False) else "none",
            width=max(6, width // 8),  # Approximate character width
            height=1
        )
        
        # Bind hover effects
        def on_enter(e):
            if style == 'primary':
                e.widget.configure(bg=config['accent'], fg=config['text'])
            elif style == 'destructive':
                e.widget.configure(bg="#3a0808", fg=config['accent_glow'])
            else:
                e.widget.configure(bg=config['bg_highlight'], fg=config['accent'])
            e.widget.configure(highlightbackground=config['accent'])
            
        def on_leave(e):
            if style == 'primary':
                e.widget.configure(bg=config['accent_dim'], fg=config['accent_glow'])
            elif style == 'destructive':
                e.widget.configure(bg="#2a0508", fg="#ff6677")
            else:
                e.widget.configure(bg=config['panel_bg'], fg=config['text'])
            e.widget.configure(highlightbackground=border_color)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def _trigger_action(self, zyngui_instance, action: str):
        """Trigger a Zynthian UI action"""
        if hasattr(zyngui_instance, 'trigger_action'):
            zyngui_instance.trigger_action(action)
        elif hasattr(zyngui_instance, 'zyngui') and hasattr(zyngui_instance.zyngui, 'trigger_action'):
            zyngui_instance.zyngui.trigger_action(action)
        else:
            logger.warning(f"Could not trigger action: {action}")
    
    def _default_select(self):
        logger.debug("SELECT pressed")
    
    def _default_back(self):
        logger.debug("BACK pressed")
    
    def update_button_states(self, states: Dict[str, bool]):
        """Update button enabled/disabled states"""
        for name, enabled in states.items():
            if name in self.control_buttons:
                btn = self.control_buttons[name]
                if enabled:
                    btn.configure(state=tk.NORMAL)
                else:
                    btn.configure(state=tk.DISABLED)
    
    def set_button_text(self, name: str, text: str):
        """Update button text dynamically"""
        if name in self.control_buttons:
            self.control_buttons[name].configure(text=text)
    
    def add_side_controls(self, zyngui_instance, controls: List[Tuple[str, Callable]]):
        """Add vertical side control buttons (MIXER, MOD UI, QUICK EDIT, etc.)"""
        config = self.layout_config
        
        # Create side panel on right side
        if hasattr(zyngui_instance, 'gigbox_side_panel'):
            try:
                zyngui_instance.gigbox_side_panel.destroy()
            except:
                pass
        
        side_panel = tk.Frame(
            zyngui_instance.root if hasattr(zyngui_instance, 'root') else self.parent,
            bg=config['bg'],
            width=config['control_area_sides'],
            highlightthickness=0
        )
        side_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)
        side_panel.pack_propagate(False)
        
        # PCB trace line
        pcb_line = tk.Frame(side_panel, bg=config['pcb'], width=1)
        pcb_line.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 0), pady=20)
        
        # Button container
        btn_container = tk.Frame(side_panel, bg=config['bg'])
        btn_container.pack(expand=True, fill=tk.BOTH, padx=8, pady=16)
        
        for i, (text, command) in enumerate(controls):
            btn = self._create_styled_button(
                btn_container,
                text=text,
                command=command,
                style='secondary',
                width=config['control_area_sides'] - 16,
                height=48,
                font_size=9
            )
            btn.pack(fill=tk.X, pady=4)
            self.control_buttons[f'side_{i}'] = btn
        
        zyngui_instance.gigbox_side_panel = side_panel
        return side_panel


def integrate_gigbox_navigation(zyngui_instance):
    """Main integration function - call during Zynthian GUI initialization"""
    
    # Create navigation manager
    nav = GigboxNavigation(
        zyngui_instance.root if hasattr(zyngui_instance, 'root') else None,
        screen_width=800,
        screen_height=480
    )
    
    # Remove on-screen directional arrows
    nav.remove_on_screen_arrows(zyngui_instance)
    
    # Create reflowed bottom controls
    def on_select():
        if hasattr(zyngui_instance, 'trigger_action'):
            zyngui_instance.trigger_action('SELECT')
    
    def on_back():
        if hasattr(zyngui_instance, 'trigger_action'):
            zyngui_instance.trigger_action('BACK')
    
    def on_mod_ui():
        if hasattr(zyngui_instance, 'trigger_action'):
            zyngui_instance.trigger_action('MOD_UI')
    
    nav.create_reflowed_controls(
        zyngui_instance,
        on_select=on_select,
        on_back=on_back,
        on_menu=None,
        on_mod_ui=on_mod_ui
    )
    
    # Add side controls
    nav.add_side_controls(zyngui_instance, [
        ('MIXER', lambda: zyngui_instance.trigger_action('MIXER') if hasattr(zyngui_instance, 'trigger_action') else None),
        ('MOD UI', on_mod_ui),
        ('QUICK EDIT', lambda: zyngui_instance.trigger_action('QUICK_EDIT') if hasattr(zyngui_instance, 'trigger_action') else None),
    ])
    
    # Store reference
    zyngui_instance.gigbox_navigation = nav
    
    logger.info("GIGBOX navigation integrated - arrows removed, controls reflowed")
    return nav


# Monkey-patch Zynthian GUI to disable arrow creation
def patch_zyngui_arrow_creation(zyngui_module):
    """Patch Zynthian GUI module to prevent arrow button creation"""
    
    # Store original methods
    original_init_controls = getattr(zyngui_module, 'init_controls', None)
    
    def patched_init_controls(self, *args, **kwargs):
        result = original_init_controls(self, *args, **kwargs) if original_init_controls else None
        
        # After init, remove arrows
        try:
            nav = GigboxNavigation(self.root)
            nav.remove_on_screen_arrows(self)
        except Exception as e:
            logging.warning(f"Could not remove arrows: {e}")
        
        return result
    
    if original_init_controls:
        zyngui_module.init_controls = patched_init_controls
    
    return zyngui_module


if __name__ == "__main__":
    # Demo
    root = tk.Tk()
    root.geometry("800x480")
    root.configure(bg="#030303")
    
    nav = GigboxNavigation(root)
    
    # Create mock control frame with arrows (to demonstrate removal)
    control_frame = tk.Frame(root, bg="#030303")
    control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
    
    # Add some arrow buttons (simulating original Zynthian)
    for name, text in [('up', '↑'), ('down', '↓'), ('left', '←'), ('right', '→')]:
        btn = tk.Button(control_frame, text=text, font=("Arial", 16), 
                       bg="#1a1a1a", fg="#ffffff", width=3, height=1)
        btn.pack(side=tk.LEFT, padx=10)
        setattr(nav, f'{name}_button', btn)
    
    # Add some regular buttons
    for text in ['SELECT', 'BACK', 'MENU']:
        btn = tk.Button(control_frame, text=text, font=("Audiowide", 10),
                       bg="#080808", fg="#ffffff", width=10, height=1)
        btn.pack(side=tk.LEFT, padx=10)
    
    print("Before removal - arrows visible")
    print("Press 'R' to remove arrows and reflow")
    
    def remove_and_reflow():
        nav.remove_on_screen_arrows(type('MockZyn', (), {'control_frame': control_frame, 'root': root})())
        nav.create_reflowed_controls(type('MockZyn', (), {'root': root, 'trigger_action': lambda x: print(x)})())
    
    root.bind('<r>', lambda e: remove_and_reflow())
    
    root.mainloop()