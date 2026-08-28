#!/usr/bin/python3
# -*- coding: utf-8 -*-
# GIGBOX Screen Transition Animations
# SPOOKI INSTRUMENTS - GIGBOX
# Fade in/out transitions between screens
# Integrates with Zynthian GUI (tkinter)

import tkinter as tk
from tkinter import ttk
import time
import threading
from typing import Callable, Optional

class GigboxTransitions:
    """Manages screen transition animations for GIGBOX UI"""
    
    # Transition durations (ms)
    FADE_IN_DURATION = 150
    FADE_OUT_DURATION = 100
    CROSSFADE_DURATION = 200
    
    # Easing functions
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        return t * t * t
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
    
    def __init__(self, root: tk.Tk, duration: int = None):
        self.root = root
        self.duration = duration or self.FADE_IN_DURATION
        self.overlay = None
        self.animating = False
        self._animation_id = None
        
    def create_overlay(self) -> tk.Frame:
        """Create full-screen overlay for transitions"""
        if self.overlay:
            self.overlay.destroy()
            
        self.overlay = tk.Frame(
            self.root,
            bg="#030303",  # GIGBOX near-black
            highlightthickness=0
        )
        self.overlay.place(x=0, y=0, relwidth=1, relheight=1)
        self.overlay.lower()  # Start behind everything
        return self.overlay
    
    def fade_in(self, callback: Callable = None, duration: int = None):
        """Fade in from black (screen appearing)"""
        if self.animating:
            return
            
        duration = duration or self.FADE_IN_DURATION
        self.animating = True
        
        overlay = self.create_overlay()
        overlay.lift()  # Bring to front
        overlay.configure(bg="#030303")
        
        # Start fully opaque
        overlay.tk.call('tk', 'scaling', 1.0)  # Ensure proper scaling
        
        steps = 30
        step_duration = duration // steps
        
        def animate_step(step: int):
            if not self.animating or step > steps:
                self._finish_fade_in(callback)
                return
                
            progress = step / steps
            eased = self.ease_out_cubic(progress)
            alpha = 1.0 - eased  # 1.0 -> 0.0
            
            # Tkinter doesn't support alpha on frames directly
            # Use a workaround: gradually change bg color toward transparent
            # Since we can't do true alpha, we simulate by lifting overlay down
            if step == steps:
                overlay.lower()  # Move behind content
                
            self._animation_id = self.root.after(step_duration, lambda: animate_step(step + 1))
        
        animate_step(0)
    
    def fade_out(self, callback: Callable = None, duration: int = None):
        """Fade out to black (screen disappearing)"""
        if self.animating:
            return
            
        duration = duration or self.FADE_OUT_DURATION
        self.animating = True
        
        overlay = self.create_overlay()
        overlay.lift()
        overlay.configure(bg="#030303")
        
        steps = 20
        step_duration = duration // steps
        
        def animate_step(step: int):
            if not self.animating or step > steps:
                self._finish_fade_out(callback)
                return
                
            progress = step / steps
            eased = self.ease_in_cubic(progress)
            
            # Simulate fade by overlay becoming visible
            if step == 1:
                overlay.lift()  # Bring to front at start
                
            self._animation_id = self.root.after(step_duration, lambda: animate_step(step + 1))
        
        animate_step(0)
    
    def crossfade(self, old_widget: tk.Widget, new_widget: tk.Widget, 
                  callback: Callable = None, duration: int = None):
        """Crossfade between two widgets"""
        if self.animating:
            return
            
        duration = duration or self.CROSSFADE_DURATION
        self.animating = True
        
        # Position new widget behind old one
        new_widget.place(x=0, y=0, relwidth=1, relheight=1)
        new_widget.lower(old_widget)
        
        overlay = self.create_overlay()
        overlay.lift()
        overlay.configure(bg="#030303")
        
        steps = 25
        step_duration = duration // steps
        
        def animate_step(step: int):
            if not self.animating or step > steps:
                self._finish_crossfade(old_widget, new_widget, callback)
                return
                
            progress = step / steps
            eased = self.ease_in_out_cubic(progress)
            
            # At halfway, swap widgets
            if step == steps // 2:
                old_widget.lower(new_widget)
                new_widget.lift()
                
            self._animation_id = self.root.after(step_duration, lambda: animate_step(step + 1))
        
        animate_step(0)
    
    def _finish_fade_in(self, callback: Callable):
        self.animating = False
        if self.overlay:
            self.overlay.lower()
        if callback:
            self.root.after_idle(callback)
    
    def _finish_fade_out(self, callback: Callable):
        self.animating = False
        if self.overlay:
            self.overlay.lift()  # Keep black screen
        if callback:
            self.root.after_idle(callback)
    
    def _finish_crossfade(self, old_widget: tk.Widget, new_widget: tk.Widget, callback: Callable):
        self.animating = False
        if self.overlay:
            self.overlay.lower()
        old_widget.place_forget()
        new_widget.lift()
        if callback:
            self.root.after_idle(callback)
    
    def cancel(self):
        """Cancel any running animation"""
        self.animating = False
        if self._animation_id:
            self.root.after_cancel(self._animation_id)
            self._animation_id = None
        if self.overlay:
            self.overlay.lower()
    
    def instant_switch(self, old_widget: tk.Widget, new_widget: tk.Widget):
        """Instant switch without animation"""
        self.cancel()
        old_widget.place_forget()
        new_widget.place(x=0, y=0, relwidth=1, relheight=1)
        new_widget.lift()


class GigboxScreenManager:
    """High-level screen manager with transitions"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.transitions = GigboxTransitions(root)
        self.current_screen = None
        self.screens = {}  # name -> widget
        self.screen_stack = []
        
    def register_screen(self, name: str, widget: tk.Widget):
        """Register a screen widget"""
        self.screens[name] = widget
        widget.place_forget()  # Hidden initially
        
    def show_screen(self, name: str, animate: bool = True, callback: Callable = None):
        """Show a registered screen with transition"""
        if name not in self.screens:
            raise ValueError(f"Screen '{name}' not registered")
            
        new_screen = self.screens[name]
        
        if self.current_screen is None:
            # First screen - just show it
            new_screen.place(x=0, y=0, relwidth=1, relheight=1)
            new_screen.lift()
            self.current_screen = name
            if callback:
                self.root.after_idle(callback)
            return
            
        if self.current_screen == name:
            return  # Already showing
            
        old_screen = self.screens[self.current_screen]
        
        if animate:
            self.transitions.crossfade(old_screen, new_screen, 
                lambda: self._on_transition_complete(name, callback))
        else:
            self.transitions.instant_switch(old_screen, new_screen)
            self.current_screen = name
            if callback:
                self.root.after_idle(callback)
    
    def _on_transition_complete(self, new_name: str, callback: Callable):
        self.current_screen = new_name
        if callback:
            callback()
    
    def push_screen(self, name: str, animate: bool = True):
        """Push screen onto stack (for modal dialogs, etc.)"""
        self.screen_stack.append(self.current_screen)
        self.show_screen(name, animate)
    
    def pop_screen(self, animate: bool = True):
        """Pop screen from stack"""
        if not self.screen_stack:
            return
        previous = self.screen_stack.pop()
        self.show_screen(previous, animate)
    
    def get_current_screen(self) -> Optional[str]:
        return self.current_screen


# Global instance for easy access
_gigbox_screen_manager = None

def get_screen_manager(root: tk.Tk = None) -> GigboxScreenManager:
    global _gigbox_screen_manager
    if _gigbox_screen_manager is None and root:
        _gigbox_screen_manager = GigboxScreenManager(root)
    return _gigbox_screen_manager


# Integration with Zynthian GUI
def integrate_with_zyngui(zyngui_instance):
    """Integrate transitions with Zynthian GUI"""
    if not hasattr(zyngui_instance, 'root'):
        return
        
    manager = get_screen_manager(zyngui_instance.root)
    
    # Wrap screen switching methods
    original_show_screen = getattr(zyngui_instance, 'show_screen', None)
    if original_show_screen:
        def wrapped_show_screen(screen_name, *args, **kwargs):
            manager.show_screen(screen_name, animate=True)
        zyngui_instance.show_screen = wrapped_show_screen
    
    return manager


if __name__ == "__main__":
    # Demo
    root = tk.Tk()
    root.geometry("800x480")
    root.configure(bg="#030303")
    
    manager = GigboxScreenManager(root)
    
    # Create test screens
    screen1 = tk.Frame(root, bg="#030303")
    tk.Label(screen1, text="SCREEN 1 - HOME", font=("Audiowide", 24), fg="#ff1744", bg="#030303").pack(expand=True)
    tk.Button(screen1, text="Go to Screen 2", command=lambda: manager.show_screen("screen2")).pack(pady=20)
    
    screen2 = tk.Frame(root, bg="#030303")
    tk.Label(screen2, text="SCREEN 2 - SETTINGS", font=("Audiowide", 24), fg="#ff1744", bg="#030303").pack(expand=True)
    tk.Button(screen2, text="Back to Home", command=lambda: manager.show_screen("screen1")).pack(pady=20)
    
    manager.register_screen("screen1", screen1)
    manager.register_screen("screen2", screen2)
    
    manager.show_screen("screen1")
    
    root.mainloop()