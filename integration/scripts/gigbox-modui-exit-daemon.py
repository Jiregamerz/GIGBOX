#!/usr/bin/python3
# -*- coding: utf-8 -*-
# GIGBOX MOD-UI Exit Daemon
# SPOOKI INSTRUMENTS - GIGBOX
# Integrates with Zynthian's input system to detect encoder/nav long-press
# and exit MOD-UI Chromium kiosk session

import sys
import os
import signal
import time
import subprocess
import threading
import logging

# Add Zynthian paths
sys.path.insert(0, '/zynthian/zynthian-ui')
sys.path.insert(0, '/zynthian/zynthian-ui/zyngui')

try:
    from zyncoder.zyncore import lib_zyncore_init
    ZYNCORE_AVAILABLE = True
except ImportError:
    ZYNCORE_AVAILABLE = False

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False

# Configuration
MOD_UI_URL = "http://localhost:8888"
EXIT_TRIGGER_FILE = "/tmp/gigbox_modui_exit_request"
LONG_PRESS_MS = 500
POLL_INTERVAL = 0.05  # 50ms

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('GIGBOX-MODUI-EXIT')

class ModUIExitDaemon:
    """Daemon that monitors Zynthian input events for MOD-UI exit conditions"""
    
    def __init__(self):
        self.running = False
        self.mod_ui_active = False
        self.chromium_pid = None
        self.exit_overlay_pid = None
        self.lib_zyncore = None
        self.last_encoder_press_time = 0
        self.last_nav_click_press_time = 0
        self.encoder_pressed = False
        self.nav_click_pressed = False
        
        # Switch indices (from gigbox_wiring.py)
        self.ENCODER_SW_IDX = 0
        self.NAV_CLICK_IDX = 8
        
    def init_zyncore(self):
        """Initialize lib_zyncore for direct GPIO reading"""
        if not ZYNCORE_AVAILABLE:
            logger.warning("lib_zyncore not available - using fallback")
            return False
        
        try:
            self.lib_zyncore = lib_zyncore_init()
            logger.info("lib_zyncore initialized for MOD-UI exit monitoring")
            return True
        except Exception as e:
            logger.error(f"Failed to init lib_zyncore: {e}")
            return False
    
    def read_switch_state(self, switch_idx):
        """Read a switch state directly from lib_zyncore"""
        if not self.lib_zyncore:
            return None
        try:
            # lib_zyncore has get_switch method
            return self.lib_zyncore.get_switch(switch_idx)
        except Exception as e:
            logger.debug(f"Error reading switch {switch_idx}: {e}")
            return None
    
    def read_all_switches(self):
        """Read all switch states"""
        if not self.lib_zyncore:
            return {}
        try:
            return self.lib_zyncore.get_switches()
        except Exception as e:
            logger.debug(f"Error reading switches: {e}")
            return {}
    
    def check_long_press(self):
        """Check for long press on encoder switch or nav click"""
        now = time.time() * 1000  # ms
        
        # Read switches
        switches = self.read_all_switches()
        
        # Check encoder switch (index 0)
        encoder_state = switches.get(self.ENCODER_SW_IDX, 1)  # 1 = released (active low)
        if encoder_state == 0:  # Pressed
            if not self.encoder_pressed:
                self.encoder_pressed = True
                self.last_encoder_press_time = now
            elif now - self.last_encoder_press_time >= LONG_PRESS_MS:
                if self.mod_ui_active:
                    logger.info("Encoder long press detected - exiting MOD-UI")
                    self.trigger_modui_exit()
                    self.encoder_pressed = False  # Prevent re-trigger
        else:
            self.encoder_pressed = False
        
        # Check nav click (index 8)
        nav_click_state = switches.get(self.NAV_CLICK_IDX, 1)
        if nav_click_state == 0:  # Pressed
            if not self.nav_click_pressed:
                self.nav_click_pressed = True
                self.last_nav_click_press_time = now
            elif now - self.last_nav_click_press_time >= LONG_PRESS_MS:
                if self.mod_ui_active:
                    logger.info("Nav CLICK long press detected - exiting MOD-UI")
                    self.trigger_modui_exit()
                    self.nav_click_pressed = False
        else:
            self.nav_click_pressed = False
    
    def trigger_modui_exit(self):
        """Trigger MOD-UI exit via trigger file and direct process kill"""
        # Write trigger file (for launcher script compatibility)
        try:
            with open(EXIT_TRIGGER_FILE, 'w') as f:
                f.write(str(time.time()))
        except Exception as e:
            logger.error(f"Failed to write trigger file: {e}")
        
        # Direct process termination
        self.kill_modui_processes()
        
        self.mod_ui_active = False
    
    def kill_modui_processes(self):
        """Kill Chromium and exit overlay processes"""
        # Kill Chromium MOD-UI session
        try:
            subprocess.run(['pkill', '-f', f'chromium.*{MOD_UI_URL}'], 
                         capture_output=True, timeout=2)
        except Exception as e:
            logger.debug(f"pkill chromium: {e}")
        
        # Kill exit overlay
        try:
            subprocess.run(['pkill', '-f', 'gigbox_modui_exit'], 
                         capture_output=True, timeout=2)
        except Exception as e:
            logger.debug(f"pkill exit overlay: {e}")
        
        # Clean up trigger file
        try:
            os.unlink(EXIT_TRIGGER_FILE)
        except:
            pass
    
    def start_modui_session(self):
        """Called when MOD-UI is launched"""
        self.mod_ui_active = True
        self.encoder_pressed = False
        self.nav_click_pressed = False
        logger.info("MOD-UI session started - monitoring for exit")
    
    def end_modui_session(self):
        """Called when MOD-UI ends normally"""
        self.mod_ui_active = False
        logger.info("MOD-UI session ended")
    
    def run(self):
        """Main monitoring loop"""
        if not self.init_zyncore():
            logger.error("Cannot start without lib_zyncore")
            return
        
        self.running = True
        logger.info("MOD-UI Exit Daemon started - monitoring encoder/nav long press")
        
        while self.running:
            try:
                self.check_long_press()
                time.sleep(POLL_INTERVAL)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(1)
        
        logger.info("MOD-UI Exit Daemon stopped")


class ModUIExitDaemonGTK:
    """Alternative: GTK-based daemon that integrates with Zynthian's UI event loop"""
    
    def __init__(self):
        self.mod_ui_active = False
        self.timeout_id = None
        
    def start_monitoring(self):
        """Start GTK timeout monitoring"""
        if GTK_AVAILABLE:
            self.timeout_id = Gtk.timeout_add(int(POLL_INTERVAL * 1000), self._gtk_check_long_press)
            logger.info("GTK-based MOD-UI exit monitor started")
    
    def stop_monitoring(self):
        if self.timeout_id:
            Gtk.source_remove(self.timeout_id)
            self.timeout_id = None
    
    def _gtk_check_long_press(self):
        """GTK timeout callback"""
        # This would be called from Zynthian's main loop
        # Requires integration with Zynthian's input handling
        return True  # Continue timeout


def main():
    """Main entry point for systemd service"""
    logger.info("=" * 50)
    logger.info("GIGBOX MOD-UI Exit Daemon")
    logger.info("SPOOKI INSTRUMENTS")
    logger.info("=" * 50)
    
    daemon = ModUIExitDaemon()
    
    # Handle signals
    def signal_handler(signum, frame):
        logger.info("Shutdown signal received")
        daemon.running = False
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        daemon.run()
    except Exception as e:
        logger.error(f"Daemon error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())