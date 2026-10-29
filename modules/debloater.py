#!/usr/bin/env python3
"""
Universal Android Bloatware Remover & Safe Debloater
Safely removes pre-installed OEM bloatware, adware stubs, and telemetry trackers across any Android brand:
- Samsung OneUI
- Xiaomi / Poco / Redmi (HyperOS / MIUI)
- OPPO / Realme / OnePlus (ColorOS / Realme UI / OxygenOS)
- Vivo / iQOO (Funtouch OS / OriginOS)
- Motorola & Carrier Bloatware (Jio, Airtel, AT&T, Verizon)
- Universal Facebook / Meta background tracking stubs

Safe by design: Uses Android's native `pm disable-user --user 0` and `pm uninstall -k --user 0`.
Never bricks or bootloops the phone. Reversible at any time.
"""

class UniversalDebloater:
    def __init__(self, device):
        self.dev = device

    # Curated, community-tested bloatware database
    BLOATWARE_DATABASE = {
        # Universal pre-installed trackers & stubs (Meta, diagnostic loggers)
        "universal": [
            "com.facebook.katana",            # Facebook app (if pre-installed)
            "com.facebook.system",            # Facebook App Installer stub
            "com.facebook.appmanager",        # Facebook App Manager
            "com.facebook.services",          # Facebook Background Services
            "com.netflix.partner.activation", # Netflix partner activation stub
            "com.amazon.appmanager"           # Amazon Shopping background updater
        ],

        # Samsung OneUI Bloatware
        "samsung": [
            "com.samsung.android.app.spage",          # Samsung Free / Bixby Home
            "com.samsung.android.mateagent",          # Galaxy Store agent
            "com.samsung.android.bixby.agent",        # Bixby Voice Agent
            "com.samsung.android.bixby.wakeup",       # Bixby Wakeup
            "com.samsung.android.app.routines",       # Bixby Routines stub
            "com.samsung.android.arzone",             # AR Zone emoji/doodle
            "com.samsung.android.kidsinstaller",      # Samsung Kids Installer
            "com.samsung.android.dynamiclock",        # Samsung Dynamic Lockscreen
            "com.glance.internet",                    # Glance Lockscreen Ads
            "com.samsung.android.visionintelligence", # Bixby Vision
            "com.samsung.android.service.livedrawing",# Live Drawing
            "com.sec.android.app.samsungapps",        # Galaxy Store push notifications
            "com.samsung.android.globalgoals",        # Samsung Global Goals ads
            "com.samsung.android.allshare.service.mediashare"
        ],

        # Xiaomi / Poco / Redmi (HyperOS & MIUI)
        "xiaomi": [
            "com.miui.msa.global",            # MIUI System Ads daemon
            "com.xiaomi.mipicks",             # GetApps store & notification spam
            "com.miui.analytics",             # Xiaomi Telemetry & Analytics
            "com.miui.daemon",                # MIUI Background Daemon
            "com.miui.bugreport",             # Bug report telemetry
            "com.miui.yellowpage",            # Yellow Pages caller tracking
            "com.miui.browser",               # Mi Browser (clickbait news)
            "com.miui.videoplayer",           # Mi Video (ad-supported player)
            "com.miui.player",                # Mi Music (ad-supported music)
            "com.xiaomi.glgm",                # Xiaomi Games push store
            "com.xiaomi.payment",             # Mi Pay (if unused)
            "com.miui.hybrid",                # Quick Apps
            "com.miui.hybrid.accessory",
            "com.miui.cleanmaster",           # CleanMaster ad SDK
            "com.sohu.inputmethod.sogou.xiaomi"
        ],

        # OPPO / Realme / OnePlus (ColorOS, Realme UI, OxygenOS)
        "bbk_oplus": [
            "com.heytap.pictorial",           # Lock Screen Magazine (Sponsored ads)
            "com.heytap.market",              # HeyTap App Market push spam
            "com.heytap.browser",             # ColorOS Native Browser clickbaits
            "com.nearme.gamecenter",          # OPPO Game Center
            "com.heytap.mcs",                 # Push marketing notification service
            "com.heytap.themestore",          # Theme store commercial popups
            "com.oplus.cosa",                 # Games Assistant promotional pushes
            "com.redteamobile.roaming",       # Redtea Mobile Roaming stub
            "com.coloros.gamespace",          # Game Space store ads
            "com.glance.internet"             # Glance Lockscreen
        ],

        # Vivo / iQOO (Funtouch OS & OriginOS)
        "bbk_vivo": [
            "com.vivo.magazine",              # Lock Screen Magazine ads
            "com.bbk.appstore",               # V-Appstore recommendations
            "com.vivo.browser",               # Vivo Browser clickbaits
            "com.vivo.easyshare",             # EasyShare promotional pushes
            "com.iqoo.engineermode",          # Engineering logs
            "com.vivo.game",                  # Vivo Game Center
            "com.vivo.unionpay",              # Vivo Pay
            "com.vivo.assistant",             # Jovi Assistant tracking
            "com.glance.internet"
        ],

        # Motorola
        "motorola": [
            "com.motorola.ccc.notification",  # Motorola Survey & Notification pushes
            "com.motorola.motoappbox",        # IronSource sponsored apps installer
            "com.motorola.genie",             # Moto Tips & ads
            "com.glance.internet"
        ],

        # Telecom Carrier Bloatware (India & Global)
        "carrier": [
            "com.jio.myjio",                  # MyJio stub ads
            "com.myairtelapp",                # Airtel Thanks push stub
            "com.mizmoweb.vcompanion",        # Vi companion
            "com.att.dh",                     # AT&T Device Help
            "com.vzw.hss.myverizon"           # Verizon stub
        ]
    }

    def get_installed_packages(self):
        out, _, _ = self.dev.run_shell("pm list packages --user 0")
        return set(line.replace("package:", "").strip() for line in out.splitlines() if line)

    def scan_bloatware(self):
        """Scans the phone for installed bloatware matching universal, OEM, and carrier lists."""
        installed = self.get_installed_packages()
        oem = self.dev.info.get("oem", "generic")

        detected = {
            "universal": [],
            "oem_specific": [],
            "carrier": []
        }

        # Check universal
        for pkg in self.BLOATWARE_DATABASE.get("universal", []):
            if pkg in installed:
                detected["universal"].append(pkg)

        # Check OEM specific
        oem_targets = self.BLOATWARE_DATABASE.get(oem, [])
        for pkg in oem_targets:
            if pkg in installed:
                detected["oem_specific"].append(pkg)

        # Check carrier
        for pkg in self.BLOATWARE_DATABASE.get("carrier", []):
            if pkg in installed:
                detected["carrier"].append(pkg)

        return detected

    def remove_package(self, pkg):
        """Safely disables/uninstalls the package for user 0."""
        # Try disable first
        res, _, rc = self.dev.run_shell(f"pm disable-user --user 0 {pkg} 2>/dev/null")
        if "disabled" in res or rc == 0:
            return True
        # Fallback to uninstall -k --user 0
        res2, _, rc2 = self.dev.run_shell(f"pm uninstall -k --user 0 {pkg} 2>/dev/null")
        return "Success" in res2 or rc2 == 0

    def debloat_all(self):
        """Scans and removes all detected bloatware on the phone."""
        scan = self.scan_bloatware()
        all_targets = scan["universal"] + scan["oem_specific"] + scan["carrier"]

        removed = []
        failed = []

        for pkg in all_targets:
            ok = self.remove_package(pkg)
            if ok:
                removed.append(pkg)
            else:
                failed.append(pkg)

        return {
            "total_detected": len(all_targets),
            "removed": removed,
            "failed": failed,
            "by_category": scan
        }
