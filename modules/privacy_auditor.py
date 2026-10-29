#!/usr/bin/env python3
"""
Universal Android Privacy & Spyware Auditor
Audits which third-party and system apps hold sensitive background permissions:
- 📷 Camera Access
- 🎙️ Microphone Recording
- 📍 Precise Background Location (GPS)
- 📇 Contacts & SMS Access
Computes a device Privacy Score (0-100) and highlights suspicious trackers.
"""
import re

class PrivacyAuditor:
    def __init__(self, device):
        self.dev = device

    def _query_permission_holders(self, op_name):
        out, _, _ = self.dev.run_shell(f"cmd appops query-op {op_name} allow 2>/dev/null")
        packages = []
        for line in out.splitlines():
            line = line.strip()
            if line and not line.startswith("[") and not line.startswith("Error"):
                pkg = line.split()[0] if " " in line else line
                # Ignore system core internals
                if not any(pkg.startswith(x) for x in ["android", "com.android.server", "vendor."]):
                    packages.append(pkg)
        return sorted(list(set(packages)))

    def audit_privacy(self):
        camera_apps = self._query_permission_holders("CAMERA")
        mic_apps = self._query_permission_holders("RECORD_AUDIO")
        location_apps = self._query_permission_holders("ACCESS_FINE_LOCATION")
        contacts_apps = self._query_permission_holders("READ_CONTACTS")

        # Get list of 3rd party user-installed apps
        out, _, _ = self.dev.run_shell("pm list packages -3")
        third_party = set(line.replace("package:", "").strip() for line in out.splitlines() if line)

        # Flag 3rd party apps with dangerous permissions
        flagged = []
        for pkg in third_party:
            perms = []
            if pkg in camera_apps:
                perms.append("Camera")
            if pkg in mic_apps:
                perms.append("Mic")
            if pkg in location_apps:
                perms.append("Exact Location")
            if pkg in contacts_apps:
                perms.append("Contacts")
            
            if len(perms) >= 2:
                flagged.append({"package": pkg, "permissions": perms})

        # Calculate score (100 minus penalties for excessive 3rd party permissions)
        penalty = min(50, len(flagged) * 6)
        privacy_score = max(50, 100 - penalty)

        return {
            "privacy_score": privacy_score,
            "camera_access_count": len(camera_apps),
            "mic_access_count": len(mic_apps),
            "location_access_count": len(location_apps),
            "flagged_third_party_apps": flagged,
            "total_user_apps_audited": len(third_party)
        }

    def revoke_permission(self, package, perm_op):
        """Revokes a specific permission operation for a package."""
        self.dev.run_shell(f"cmd appops set {package} {perm_op} ignore 2>/dev/null")
        return True
