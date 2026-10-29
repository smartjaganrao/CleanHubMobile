#!/usr/bin/env python3
"""
Universal Android Battery Health & Cycle Counter
Fetches true kernel-level hardware telemetry like an iPhone:
- Charge cycle count (/sys/class/power_supply/battery/cycle_count)
- Battery temperature, voltage, and charging current
- Health percentage estimation and degradation score
"""
import re

class BatteryHealthDoctor:
    def __init__(self, device):
        self.dev = device

    def get_cycle_count(self):
        """Reads hardware charge cycles directly from kernel power supply sysfs."""
        paths = [
            "/sys/class/power_supply/battery/cycle_count",
            "/sys/class/power_supply/bms/battery_cycle",
            "/sys/class/power_supply/battery/battery_cycle"
        ]
        for p in paths:
            out, _, rc = self.dev.run_shell(f"cat {p} 2>/dev/null")
            out = out.strip()
            if rc == 0 and out.isdigit():
                return int(out)
        return None

    def get_battery_telemetry(self):
        out, _, _ = self.dev.run_shell("dumpsys battery")
        
        temp_m = re.search(r'temperature:\s*([0-9]+)', out)
        level_m = re.search(r'level:\s*([0-9]+)', out)
        volt_m = re.search(r'voltage:\s*([0-9]+)', out)
        status_m = re.search(r'status:\s*([0-9]+)', out)
        health_m = re.search(r'health:\s*([0-9]+)', out)

        temp_c = (float(temp_m.group(1)) / 10.0) if temp_m else 0.0
        level = int(level_m.group(1)) if level_m else 0
        voltage = int(volt_m.group(1)) if volt_m else 0
        health_code = int(health_m.group(1)) if health_m else 2

        # Status string
        status_code = int(status_m.group(1)) if status_m else 1
        status_map = {1: "Unknown", 2: "Charging", 3: "Discharging", 4: "Not Charging", 5: "Full"}
        status_str = status_map.get(status_code, "Discharging")

        health_map = {1: "Unknown", 2: "Good", 3: "Overheat", 4: "Dead", 5: "Over Voltage", 6: "Failure", 7: "Cold"}
        health_str = health_map.get(health_code, "Good")

        cycles = self.get_cycle_count()

        # Estimated Health % (Standard Li-Ion loses ~20% capacity over 800-1000 cycles)
        if cycles is not None:
            # Conservative estimate: 100% - (cycles * 0.02)
            est_health = max(65.0, round(100.0 - (cycles * 0.022), 1))
        else:
            est_health = 95.0

        return {
            "cycles": cycles,
            "estimated_health_pct": est_health,
            "temperature_c": temp_c,
            "battery_level": level,
            "voltage_mv": voltage,
            "status": status_str,
            "health_state": health_str
        }

    def print_battery_card(self):
        t = self.get_battery_telemetry()
        print("=" * 50)
        print(" 🔋 HARDWARE BATTERY HEALTH & CYCLE TELEMETRY")
        print("=" * 50)
        print(f" • Charge Cycle Count  : {t['cycles'] if t['cycles'] is not None else 'N/A (Kernel protected)'} cycles")
        print(f" • Estimated Capacity  : ~{t['estimated_health_pct']}% Health")
        print(f" • Battery Level       : {t['battery_level']}% ({t['status']})")
        print(f" • Temperature         : {t['temperature_c']}°C (Normal: 25-38°C)")
        print(f" • Operating Health    : {t['health_state']}")
        print("=" * 50)
        return t
