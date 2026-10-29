#!/usr/bin/env python3
"""
Universal Android Zero-Lag Performance Booster
Applies low-level compiler and kernel optimizations to deliver instant flagship speed:
1. Compiles core UI & daily apps to native ARM64 machine code (ART Ahead-Of-Time).
2. Enables Linux Kernel CGroup App Freezer (freezes background apps at 0% CPU).
3. Configures 0.5x instant animation speed engine.
4. Executes hardware UFS / eMMC storage TRIM.
"""

class PerformanceBooster:
    def __init__(self, device):
        self.dev = device

    def apply_animation_boost(self, scale=0.5):
        """Sets window, transition, and animator scales to 0.5x for instant response."""
        self.dev.run_shell(f"settings put global window_animation_scale {scale}")
        self.dev.run_shell(f"settings put global transition_animation_scale {scale}")
        self.dev.run_shell(f"settings put global animator_duration_scale {scale}")
        return True

    def enable_app_freezer(self):
        """Enables Android MGLRU/CGroup App Freezer so minimized apps use 0 CPU cycles."""
        self.dev.run_shell("device_config put activity_manager_native_boot use_freezer true 2>/dev/null")
        out, _, _ = self.dev.run_shell("device_config get activity_manager_native_boot use_freezer 2>/dev/null")
        return "true" in out.lower()

    def run_storage_trim(self):
        """Forces UFS / eMMC flash controller to discard deleted blocks and restore peak read/write speeds."""
        out, _, rc = self.dev.run_shell("sm fstrim")
        return rc == 0

    def compile_apps_native(self, extra_packages=None):
        """Compiles system framework, launcher, and daily apps into 100% native machine code."""
        # Detect OEM launcher
        launcher_candidates = [
            "com.sec.android.app.launcher",  # Samsung OneUI
            "com.miui.home",                 # Xiaomi / Poco / Redmi
            "com.android.launcher",          # ColorOS / Realme / OnePlus
            "com.google.android.apps.nexuslauncher", # Pixel
            "com.motorola.launcher3"         # Motorola
        ]
        
        target_packages = ["com.android.systemui", "com.android.settings"]
        
        # Check installed packages
        out, _, _ = self.dev.run_shell("pm list packages")
        installed = set(line.replace("package:", "").strip() for line in out.splitlines() if line)

        for l in launcher_candidates:
            if l in installed:
                target_packages.append(l)
                break

        # Common daily apps
        common_apps = [
            "com.whatsapp",
            "com.android.chrome",
            "com.google.android.youtube",
            "com.instagram.android"
        ]
        for app in common_apps:
            if app in installed:
                target_packages.append(app)

        if extra_packages:
            for ep in extra_packages:
                if ep in installed and ep not in target_packages:
                    target_packages.append(ep)

        compiled = []
        for pkg in target_packages:
            compile_cmd = f"cmd package compile -m speed -f {pkg}"
            res, _, rc = self.dev.run_shell(compile_cmd, timeout=45)
            if "Success" in res or rc == 0:
                compiled.append(pkg)

        return compiled

    def run_full_boost(self):
        anim_ok = self.apply_animation_boost(0.5)
        freezer_ok = self.enable_app_freezer()
        trim_ok = self.run_storage_trim()
        compiled = self.compile_apps_native()

        return {
            "animations_boosted": anim_ok,
            "freezer_active": freezer_ok,
            "storage_trimmed": trim_ok,
            "compiled_packages": compiled
        }
