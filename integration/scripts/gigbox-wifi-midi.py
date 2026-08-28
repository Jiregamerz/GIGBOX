#!/usr/bin/python3
# -*- coding: utf-8 -*-
# GIGBOX WiFi UDP MIDI Receiver
# SPOOKI INSTRUMENTS - GIGBOX
# Receives MIDI over WiFi UDP and injects into Zynthian MIDI system
# Runs as systemd service, starts automatically on boot
#
# PROTOCOL SPECIFICATION:
# =======================
# UDP Port: 4210 (GIGBOX legacy compatibility)
# 
# Packet Format: Raw MIDI messages (no RTP-MIDI header)
#   - Channel Voice Messages (0x80-0xEF): 3 bytes (Note Off, Note On, CC, etc.)
#     Note Off:      0x80 | channel, note, velocity
#     Note On:       0x90 | channel, note, velocity
#     Poly Pressure: 0xA0 | channel, note, pressure
#     Control Change: 0xB0 | channel, controller, value
#     Program Change: 0xC0 | channel, program
#     Channel Press:  0xD0 | channel, pressure
#     Pitch Bend:     0xE0 | channel, LSB, MSB
#   - System Common (0xF0-0xF7): Variable length
#     SysEx Start:    0xF0 ... 0xF7
#     MTC Quarter:    0xF1, time
#     Song Position:  0xF2, LSB, MSB
#     Song Select:    0xF3, song
#     Tune Request:   0xF6
#   - System Real-Time (0xF8-0xFF): 1 byte
#     Clock:          0xF8
#     Start:          0xFA
#     Continue:       0xFB
#     Stop:           0xFC
#     Active Sense:   0xFE
#     Reset:          0xFF
#
# Multiple MIDI messages can be packed in a single UDP packet.
# Running status is supported.
#
# MIDI Injection Method:
#   1. Primary: lib_zyncore (Zynthian's native MIDI system)
#   2. Fallback: rtmidi virtual port "GIGBOX WiFi MIDI In"
#
# Compatibility:
#   - GIGBOX legacy transmitter (UDP 4210)
#   - Generic UDP MIDI senders (raw MIDI bytes)
#   - RTP-MIDI not supported (use raw MIDI over UDP)

import socket
import struct
import threading
import time
import logging
import sys
import os
import select

# Add Zynthian to path
sys.path.insert(0, '/zynthian/zynthian-ui')
sys.path.insert(0, '/zynthian/zynthian-ui/zyngui')

try:
    from zyncoder.zyncore import lib_zyncore_init
    ZYNCORE_AVAILABLE = True
except ImportError:
    ZYNCORE_AVAILABLE = False
    logging.warning("lib_zyncore not available - MIDI injection limited")

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False
    logging.warning("rtmidi not available - using fallback")

# Configuration
UDP_PORT = 4210                     # GIGBOX legacy compatibility port
BUFFER_SIZE = 1024
MIDI_BUFFER_SIZE = 256

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/gigbox-wifi-midi.log')
    ]
)
logger = logging.getLogger('GIGBOX-WiFi-MIDI')

class MidiProcessor:
    """Process and route MIDI messages to Zynthian"""
    
    def __init__(self):
        self.running = False
        self.midi_queue = []
        self.queue_lock = threading.Lock()
        self.stats = {
            'packets_received': 0,
            'midi_messages': 0,
            'errors': 0,
            'bytes_received': 0
        }
        
        # Try to initialize Zynthian MIDI output
        self.zyncore = None
        self.rtmidi_out = None
        self.init_midi_output()
    
    def init_midi_output(self):
        """Initialize MIDI output to Zynthian system"""
        # Try zyncore first
        if ZYNCORE_AVAILABLE:
            try:
                self.zyncore = lib_zyncore_init()
                logger.info("Zynthian zyncore initialized for MIDI output")
            except Exception as e:
                logger.warning(f"Could not init zyncore: {e}")
        
        # Fallback to rtmidi virtual port
        if RTMIDI_AVAILABLE:
            try:
                self.rtmidi_out = rtmidi.MidiOut()
                # Try to open Zynthian's virtual MIDI port
                ports = self.rtmidi_out.get_ports()
                zynthian_port = None
                for i, port in enumerate(ports):
                    if 'zynthian' in port.lower() or 'virtual' in port.lower():
                        zynthian_port = i
                        break
                
                if zynthian_port is not None:
                    self.rtmidi_out.open_port(zynthian_port)
                    logger.info(f"Connected to MIDI port: {ports[zynthian_port]}")
                else:
                    # Create virtual port
                    self.rtmidi_out.open_virtual_port("GIGBOX WiFi MIDI In")
                    logger.info("Created virtual MIDI port: GIGBOX WiFi MIDI In")
            except Exception as e:
                logger.warning(f"Could not init rtmidi: {e}")
    
    def send_midi(self, message):
        """Send MIDI message to Zynthian"""
        if not message or len(message) < 1:
            return
        
        # Send via zyncore if available
        if self.zyncore:
            try:
                # zyncore expects list of bytes
                self.zyncore.midi_send_message(list(message))
                return
            except Exception as e:
                logger.debug(f"zyncore send failed: {e}")
        
        # Fallback to rtmidi
        if self.rtmidi_out:
            try:
                self.rtmidi_out.send_message(list(message))
                return
            except Exception as e:
                logger.debug(f"rtmidi send failed: {e}")
        
        logger.debug("No MIDI output available")
    
    def process_midi_packet(self, data, addr):
        """Process incoming UDP MIDI packet"""
        self.stats['packets_received'] += 1
        self.stats['bytes_received'] += len(data)
        
        # Handle raw MIDI stream (multiple messages per packet)
        i = 0
        running_status = None
        
        while i < len(data):
            status = data[i]
            
            # Determine message length
            if status >= 0xF0:
                # System messages
                if status == 0xF0:
                    # SysEx - find ending 0xF7
                    j = i + 1
                    while j < len(data) and data[j] != 0xF7:
                        j += 1
                    if j < len(data):
                        msg = data[i:j+1]
                        i = j + 1
                    else:
                        # Incomplete SysEx
                        running_status = None
                        break
                elif status == 0xF7:
                    # End of SysEx without start - skip
                    i += 1
                    running_status = None
                    continue
                else:
                    # Other system messages (F1-F6, F8-FF) - mostly 1 byte
                    msg = data[i:i+1]
                    i += 1
                    running_status = None
            elif status >= 0x80:
                # Channel messages - new status byte
                running_status = status
                if status in (0xC0, 0xD0):  # Program Change, Channel Pressure
                    msg_len = 2
                else:
                    msg_len = 3  # Note Off, Note On, CC, Pitch Bend, etc.
                
                if i + msg_len <= len(data):
                    msg = data[i:i+msg_len]
                    i += msg_len
                else:
                    # Incomplete message
                    break
            else:
                # Data byte - use running status
                if running_status is None:
                    # Invalid: data byte without status
                    i += 1
                    continue
                
                if running_status in (0xC0, 0xD0):
                    msg_len = 2
                else:
                    msg_len = 3
                
                # We have the status byte at i-1, need msg_len-1 data bytes
                if i + msg_len - 1 <= len(data):
                    msg = bytes([running_status]) + data[i:i+msg_len-1]
                    i += msg_len - 1
                else:
                    break
            
            # Queue message for processing
            with self.queue_lock:
                self.midi_queue.append(msg)
                self.stats['midi_messages'] += 1
    
    def process_queue(self):
        """Process queued MIDI messages"""
        with self.queue_lock:
            messages = self.midi_queue[:]
            self.midi_queue.clear()
        
        for msg in messages:
            self.send_midi(msg)

class UdpMidiReceiver:
    """UDP MIDI Receiver Service"""
    
    def __init__(self, port=UDP_PORT):
        self.port = port
        self.socket = None
        self.running = False
        self.processor = MidiProcessor()
        self.thread = None
    
    def start(self):
        """Start the UDP receiver"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.setblocking(False)
            
            self.running = True
            self.thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.thread.start()
            
            logger.info(f"GIGBOX WiFi MIDI Receiver started on UDP port {self.port}")
            logger.info("Protocol: Raw MIDI over UDP (GIGBOX legacy compatible)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start UDP receiver: {e}")
            return False
    
    def stop(self):
        """Stop the UDP receiver"""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("GIGBOX WiFi MIDI Receiver stopped")
    
    def _receive_loop(self):
        """Main receive loop"""
        while self.running:
            try:
                ready = select.select([self.socket], [], [], 0.1)
                if ready[0]:
                    data, addr = self.socket.recvfrom(BUFFER_SIZE)
                    self.processor.process_midi_packet(data, addr)
                
                # Process queued messages
                self.processor.process_queue()
                
            except socket.error as e:
                if self.running:
                    logger.error(f"Socket error: {e}")
                    self.processor.stats['errors'] += 1
            except Exception as e:
                logger.error(f"Receive loop error: {e}")
                self.processor.stats['errors'] += 1
    
    def get_stats(self):
        """Get receiver statistics"""
        return self.processor.stats.copy()

def main():
    """Main entry point for systemd service"""
    logger.info("=" * 50)
    logger.info("GIGBOX WiFi UDP MIDI Receiver")
    logger.info("SPOOKI INSTRUMENTS")
    logger.info(f"UDP Port: {UDP_PORT} (GIGBOX legacy compatible)")
    logger.info("Protocol: Raw MIDI over UDP")
    logger.info("=" * 50)
    
    receiver = UdpMidiReceiver(UDP_PORT)
    
    if not receiver.start():
        logger.error("Failed to start receiver")
        sys.exit(1)
    
    # Periodic stats logging
    try:
        while True:
            time.sleep(60)
            stats = receiver.get_stats()
            logger.info(f"Stats: {stats}")
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        receiver.stop()

if __name__ == "__main__":
    main()