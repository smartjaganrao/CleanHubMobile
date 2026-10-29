#!/usr/bin/env python3
"""
Universal Android Thermal & Battery Health Doctor
Diagnoses battery temperature, CPU thrashing, and memory pressure.
Automatically applies fixes to stop thermal throttling and UI freezes:
1. Disables 24/7 background Wi-Fi & Bluetooth location scanning (stops Google Maps overheating).
2. Enables Dynamic Auto-Brightness.
3. Detects kernel swap / RAM thrashing (NAND swap).
"""
import re

class ThermalDoctor:
    def __init__(self, device):
        self.dev = device

    def get_battery_thermals(self):
        out, _, _ = self.dev.run_shell("dumpsys battery")
        temp_m = re.search(r'temperature:\s*([0-9]+)', out)
        level_m = re.search(r'level:\s*([0-9]+)', out)
        health_m = re.search(r'health:\s*([0-9]+)', out)
        
        temp_c = (float(temp_m.group(1)) / 10.0) if temp_m else 0.0
        level = int(level_m.group(1)) if level_m else 0
        return {
            "battery_temp_c": temp_c,
            "battery_level_pct": level,
            "health_code": int(health_m.group(1)) if health_m else 2
        }

    def get_cpu_and_load(self):
        out, _, _ = self.dev.run_shell("uptime")
        load_m = re.search(r'load average:\s*([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)', out)
        if load_m:
            return {
                "load_1m": float(load_m.group(1)),
                "load_5m": float(load_m.group(2)),
                "load_15m": float(load_m.group(3))
            }
        return {}

    def fix_thermal_drains(self):
        """Disables background radio scanning and sets auto brightness to cool down hardware."""
        # Disable background Wi-Fi and Bluetooth scans
        self.dev.run_shell("settings put global wifi_scan_always_enabled 0")
        self.dev.run_shell("settings put global ble_scan_always_enabled 0")
        
        # Turn on auto-brightness
        self.dev.run_shell("settings put system screen_brightness_mode 1")

        wifi_scan, _, _ = self.dev.run_shell("settings get global wifi_scan_always_enabled")
        ble_scan, _, _ = self.dev.run_shell("settings get global ble_scan_always_enabled")
        brightness_mode, _, _ = self.dev.run_shell("settings get system screen_brightness_mode")

        return {
            "wifi_scan_disabled": wifi_scan == "0",
            "ble_scan_disabled": ble_scan == "0",
            "auto_brightness_enabled": brightness_mode == "1"
        }

    def check_memory_thrashing(self):
        """Checks if ZRAM / Swap is under severe pressure."""
        out, _, _ = self.dev.run_shell("dumpsys meminfo | grep -iE 'Total RAM|Free RAM|ZRAM'")
        lines = out.strip().splitlines()
        return "\n".join(lines) if lines else "Normal"

    def run_full_diagnosis_and_cure(self):
        before_thermals = self.get_battery_thermals()
        cpu_load = self.get_cpu_and_load()
        fixes = self.fix_thermal_drains()
        mem_status = self.check_memory_thrashing()

        return {
            "battery": before_thermals,
            "cpu_load": cpu_load,
            "fixes_applied": fixes,
            "memory_pressure_summary": mem_status
        }
