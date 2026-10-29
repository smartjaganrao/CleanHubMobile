#!/usr/bin/env python3
"""
Android Core Connector
Dual-Mode Engine:
1. Remote Mode: Communicates via ADB from Mac, Linux, or Windows.
2. Local On-Device Mode: Runs directly on the phone (inside Termux or Android Terminal).
"""
import subprocess
import shutil
import sys
import os
import re

class AndroidDevice:
    def __init__(self, serial=None):
        self.is_on_device = self._check_if_on_device()
        self.adb_bin = self._find_adb() if not self.is_on_device else None
        self.serial = serial or (self._auto_detect_device() if not self.is_on_device else "localhost")
        self.info = self._fetch_device_info()

    def _check_if_on_device(self):
        """Checks if python is running natively on Android (e.g., inside Termux)."""
        return os.path.exists("/system/bin/sh") and (os.path.exists("/data/data/com.termux") or "ANDROID_ROOT" in os.environ)

    def _find_adb(self):
        adb = shutil.which("adb")
        if not adb:
            common_paths = [
                "/opt/homebrew/bin/adb",
                "/usr/local/bin/adb",
                "/usr/bin/adb",
                "C:\\platform-tools\\adb.exe"
            ]
            for p in common_paths:
                if shutil.which(p):
                    return p
        return adb or "adb"

    def _auto_detect_device(self):
        try:
            res = subprocess.run([self.adb_bin, "devices"], capture_output=True, text=True, check=True)
            devices = []
            for line in res.stdout.splitlines()[1:]:
                line = line.strip()
                if line and "\tdevice" in line:
                    devices.append(line.split("\t")[0])
            if not devices:
                return None
            return devices[0]
        except Exception:
            return None

    def run_shell(self, cmd_str, timeout=30):
        """Executes shell command either natively on Android or over ADB."""
        if self.is_on_device:
            # Native on-device execution
            try:
                res = subprocess.run(["sh", "-c", cmd_str], capture_output=True, text=True, timeout=timeout)
                return res.stdout.strip(), res.stderr.strip(), res.returncode
            except subprocess.TimeoutExpired:
                return "", "Command timed out", 1
        else:
            # Remote ADB execution
            if not self.serial:
                raise RuntimeError("No authorized Android device connected.")
            full_cmd = [self.adb_bin, "-s", self.serial, "shell", cmd_str]
            try:
                res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
                return res.stdout.strip(), res.stderr.strip(), res.returncode
            except subprocess.TimeoutExpired:
                return "", "Command timed out", 1

    def shell(self, cmd_str, timeout=30):
        """Helper that executes command and returns stdout directly."""
        stdout, _, _ = self.run_shell(cmd_str, timeout=timeout)
        return stdout

    def get_installed_packages(self):
        """Returns set of all installed packages on device."""
        out, _, _ = self.run_shell("pm list packages --user 0")
        if not out:
            out, _, _ = self.run_shell("pm list packages")
        return set(line.replace("package:", "").strip() for line in out.splitlines() if line and "package:" in line)

    def package_exists(self, package_name):
        """Checks if a package exists on device."""
        out, _, rc = self.run_shell(f"pm path {package_name}")
        return rc == 0 and bool(out)

    def push_file(self, local_path, remote_path):
        if self.is_on_device:
            shutil.copy2(local_path, remote_path)
            return True
        cmd = [self.adb_bin, "-s", self.serial, "push", local_path, remote_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode == 0

    def pull_file(self, remote_path, local_path):
        if self.is_on_device:
            shutil.copy2(remote_path, local_path)
            return True
        cmd = [self.adb_bin, "-s", self.serial, "pull", remote_path, local_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode == 0

    def _fetch_device_info(self):
        brand, _, _ = self.run_shell("getprop ro.product.brand")
        model, _, _ = self.run_shell("getprop ro.product.model")
        android_ver, _, _ = self.run_shell("getprop ro.build.version.release")
        soc, _, _ = self.run_shell("getprop ro.soc.model")
        if not soc:
            soc, _, _ = self.run_shell("getprop ro.board.platform")
        
        brand_lower = (brand or "").lower()
        if any(b in brand_lower for b in ["samsung"]):
            oem = "samsung"
        elif any(b in brand_lower for b in ["xiaomi", "redmi", "poco"]):
            oem = "xiaomi"
        elif any(b in brand_lower for b in ["oppo", "oneplus", "realme"]):
            oem = "bbk_oplus"
        elif any(b in brand_lower for b in ["vivo", "iqoo"]):
            oem = "bbk_vivo"
        elif any(b in brand_lower for b in ["google"]):
            oem = "google_pixel"
        elif any(b in brand_lower for b in ["motorola"]):
            oem = "motorola"
        else:
            oem = "generic"

        return {
            "serial": self.serial,
            "brand": brand.title() if brand else "Generic",
            "model": model or "Android Device",
            "android_version": android_ver or "Unknown",
            "soc": soc or "Unknown SoC",
            "oem": oem,
            "mode": "On-Device (Native)" if self.is_on_device else "Remote (ADB)"
        }

if __name__ == "__main__":
    dev = AndroidDevice()
    print(f"Connected to {dev.info['brand']} {dev.info['model']} in {dev.info['mode']} mode.")
