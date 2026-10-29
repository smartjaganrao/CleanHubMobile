#!/usr/bin/env python3
"""
Universal Android Ad-Blocker & OEM Bloatware Disabler
Enforces system-wide encrypted ad-blocking and disables brand-specific lockscreen / notification ads:
- Samsung OneUI (Glance, Samsung Free)
- Xiaomi / Poco / Redmi (MSA, MiuiDaemon, GetApps)
- OPPO / Realme / OnePlus (HeyTap Pictorial, App Market)
- Vivo / iQOO (Lock Screen Magazine, V-Appstore)
"""

class AdBlocker:
    def __init__(self, device):
        self.dev = device

    def enable_private_dns(self, hostname="dns.adguard-dns.com"):
        """Forces Android to route all DNS queries through encrypted DoT to block ads in apps & browsers."""
        self.dev.run_shell("settings put global private_dns_mode hostname")
        self.dev.run_shell(f"settings put global private_dns_specifier {hostname}")
        
        mode, _, _ = self.dev.run_shell("settings get global private_dns_mode")
        spec, _, _ = self.dev.run_shell("settings get global private_dns_specifier")
        return mode == "hostname" and spec == hostname

    def disable_ad_tracking(self):
        """Disables Google / Android advertising service telemetry."""
        self.dev.run_shell("settings put global ad_services_enabled 0 2>/dev/null")
        self.dev.run_shell("settings put secure ad_services_enabled 0 2>/dev/null")
        return True

    def disable_oem_bloat_ads(self):
        """Detects phone brand and disables built-in sponsored lockscreen & store notification bloatware."""
        oem = self.dev.info.get("oem", "generic")
        
        # OEM targeted bloatware packages
        oem_bloat_map = {
            "samsung": [
                "com.samsung.android.app.spage",        # Samsung Free / Daily
                "com.glance.internet",                  # Glance Lockscreen
                "com.samsung.android.mateagent"         # Galaxy Store agent
            ],
            "xiaomi": [
                "com.miui.msa.global",                  # MIUI System Ads
                "com.xiaomi.mipicks",                   # GetApps push store
                "com.miui.analytics",                   # MIUI Analytics
                "com.miui.daemon"                       # Daemon tracking
            ],
            "bbk_oplus": [
                "com.heytap.pictorial",                 # Lock Screen Magazine Ads
                "com.heytap.market",                    # App Market spam
                "com.heytap.browser"                    # Native browser clickbait
            ],
            "bbk_vivo": [
                "com.vivo.magazine",                    # Lockscreen magazine
                "com.bbk.appstore",                     # V-Appstore recommendations
                "com.vivo.browser"                      # Push notifications
            ]
        }

        # Check installed packages
        out, _, _ = self.dev.run_shell("pm list packages")
        installed = set(line.replace("package:", "").strip() for line in out.splitlines() if line)

        disabled = []
        targets = oem_bloat_map.get(oem, [])
        # Add common glance targets if present on any OEM
        targets.extend(["com.glance.internet", "com.heytap.pictorial"])

        for pkg in targets:
            if pkg in installed:
                res, _, _ = self.dev.run_shell(f"pm disable-user --user 0 {pkg} 2>/dev/null")
                if "disabled-user" in res or "new state" in res:
                    disabled.append(pkg)

        return disabled

    def run_full_ad_shield(self, dns_host="dns.adguard-dns.com"):
        dns_ok = self.enable_private_dns(dns_host)
        tracking_ok = self.disable_ad_tracking()
        disabled_bloat = self.disable_oem_bloat_ads()

        return {
            "private_dns_active": dns_ok,
            "ad_tracking_disabled": tracking_ok,
            "disabled_oem_bloatware": disabled_bloat
        }
