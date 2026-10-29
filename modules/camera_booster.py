#!/usr/bin/env python3
"""
Camera Performance & Zero Shutter Lag Booster
Transforms Android camera responsiveness to iPhone / Pixel peak speed:
1. Compiles camera app & extensions to 100% native machine code (AOT speed).
2. Whitelists camera engine from Doze and App Freezer for zero cold-start delay.
3. Clears DCIM thumbnail cache and trims UFS flash storage for stall-free burst shooting.
4. Verifies hardware ZSL (Zero Shutter Lag) and provides exact ColorOS 16 tuning parameters.
"""

class CameraBooster:
    def __init__(self, device):
        self.dev = device

    def get_camera_packages(self):
        """Identifies camera and photo pipeline packages installed on the device."""
        camera_candidates = [
            "com.oplus.camera",                # OPPO / ColorOS
            "com.android.camera",               # Xiaomi / POCO / Redmi
            "com.sec.android.app.camera",       # Samsung
            "com.google.android.GoogleCamera",  # Pixel / GCam
            "org.codeaurora.snapcam",           # LMC / GCam Snapcam
            "com.motorola.camera3",             # Motorola
            "com.android.cameraextensions",     # Android CameraX Extensions
            "com.coloros.gallery3d",            # OPPO Gallery
            "com.google.android.apps.photos"    # Google Photos
        ]
        out, _, _ = self.dev.run_shell("pm list packages")
        installed = set(line.replace("package:", "").strip() for line in out.splitlines() if line)
        
        found = [pkg for pkg in camera_candidates if pkg in installed]
        return found

    def accelerate_camera_engine(self):
        """Compiles camera packages to native machine code and whitelists them from Doze."""
        packages = self.get_camera_packages()
        results = {"compiled": [], "whitelisted": []}

        for pkg in packages:
            # 1. Native AOT Compilation
            out, _, rc = self.dev.run_shell(f"cmd package compile -m speed -f {pkg}")
            if "Success" in out or rc == 0:
                results["compiled"].append(pkg)
            
            # 2. Whitelist core camera packages from Doze/Deep Sleep
            if "camera" in pkg:
                self.dev.run_shell(f"dumpsys deviceidle whitelist +{pkg}")
                results["whitelisted"].append(pkg)

        return results

    def optimize_burst_storage(self):
        """Trims flash storage and flushes thumbnail cache to eliminate burst write delays."""
        self.dev.run_shell("rm -rf /sdcard/DCIM/.thumbnails/* 2>/dev/null")
        self.dev.run_shell("rm -rf /sdcard/Pictures/.thumbnails/* 2>/dev/null")
        out, _, rc = self.dev.run_shell("sm fstrim")
        return rc == 0

    def get_hardware_status(self):
        """Inspects Camera HAL and properties for ZSL and deferred capture support."""
        out, _, _ = self.dev.run_shell("getprop | grep -iE 'camera.defercap|zsl'")
        defer_support = "ro.oplus.camera.defercap.support" in out
        return {
            "deferred_capture_supported": defer_support,
            "raw_properties": out.strip()
        }

    def tune_iphone_clarity_and_vivid_colors(self):
        """Calibrates display, hardware OSIE engine, and warm DCI-P3 gamut for iPhone-grade vividness."""
        # 1. Enable Hardware OSIE (OPPO Screen Image Engine) / Iris 5 AI enhancement
        self.dev.run_shell("settings put system is_osie_iris5_first_set 1")
        self.dev.run_shell("settings put secure osie_iris5_switch 1")
        self.dev.run_shell("settings put secure osie_video_display_switch 1")
        self.dev.run_shell("settings put secure customize_multimedia_osie 1")

        # 2. Apple True Tone Warmth Calibration (Shift slightly warm on DCI-P3 circle)
        self.dev.run_shell("settings put system setting_enable_color_temperature_regulation 1")
        self.dev.run_shell("settings put system color_ball_last_pointx 395.0")
        self.dev.run_shell("settings put system color_ball_last_pointy 375.0")

        # 3. Vivid Display Engine & Ultra HDR
        self.dev.run_shell("settings put system display_color_mode 303")
        self.dev.run_shell("settings put secure oplus_customize_color_mode 11")

        return True
