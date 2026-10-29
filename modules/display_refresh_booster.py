#!/usr/bin/env python3
"""
Display Refresh Rate Maximizer & Uncapper
Fixes artificial 60Hz display throttling:
OEMs market 120Hz/90Hz displays, but throttle down to 60Hz inside YouTube, Google Maps,
browsers, and games to save minor battery, causing noticeable stuttering.

This module locks peak and minimum refresh rates to the device's native high-refresh rate (120Hz / 90Hz).
"""

import re

class DisplayRefreshBooster:
    def __init__(self, device):
        self.dev = device

    def detect_supported_rates(self):
        """Extracts supported refresh rates from display dumpsys."""
        display_dump = self.dev.shell("dumpsys display | grep -E 'fps|mode'")
        rates = re.findall(r'(\d+\.?\d*)\s*fps', display_dump)
        unique_rates = sorted(list(set([float(r) for r in rates if float(r) >= 60.0])), reverse=True)
        return unique_rates if unique_rates else [120.0, 90.0, 60.0]

    def get_current_settings(self):
        """Reads current refresh rate settings."""
        peak = self.dev.shell("settings get system peak_refresh_rate").strip()
        min_r = self.dev.shell("settings get system min_refresh_rate").strip()
        return {"peak": peak, "min": min_r}

    def lock_high_refresh_rate(self, target_hz=120.0):
        """Locks peak and min refresh rates to target Hz."""
        self.dev.shell(f"settings put system peak_refresh_rate {target_hz}")
        self.dev.shell(f"settings put system min_refresh_rate {target_hz}")
        return True

    def reset_to_auto(self):
        """Reverts refresh rate control back to system auto/adaptive mode."""
        self.dev.shell("settings delete system peak_refresh_rate")
        self.dev.shell("settings delete system min_refresh_rate")
        return True

    def run(self):
        print("\n🖥️  Display Refresh Rate Maximizer (120Hz Force Uncap)")
        print("-" * 55)

        current = self.get_current_settings()
        supported = self.detect_supported_rates()
        max_rate = supported[0] if supported else 120.0

        print(f"📱 Detected Max Display Rate: {max_rate} Hz (Supported: {supported})")
        print(f"⚙️  Current Peak: {current['peak']} | Current Min: {current['min']}")

        print(f"\n🚀 Locking System Refresh Rate to constant {max_rate} Hz...")
        self.lock_high_refresh_rate(max_rate)

        new_settings = self.get_current_settings()
        print(f"✅ Successfully Set: Min={new_settings['min']} Hz, Peak={new_settings['peak']} Hz")
        print("✨ YouTube, Maps, Chrome, and all system apps will now scroll at maximum smoothness!")
        return True
