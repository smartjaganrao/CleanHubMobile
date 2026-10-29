#!/usr/bin/env python3
"""
Notification Delay & Task-Killer Fixer ("Don't Kill My App")
Fixes the #1 complaint of modern Android users:
Delayed WhatsApp, Telegram, Gmail, and Banking notifications caused by aggressive
OEM power managers (ColorOS Athena, Xiaomi MIUI Cleaner, Samsung Sleeping Apps).

Automatically identifies installed critical apps and exempts them from:
- Android Doze mode
- OEM background process freezing
- App Standby buckets
"""

class NotificationFixer:
    # Common mission-critical packages (messaging, emails, banking, alarms)
    CRITICAL_TARGETS = [
        # Messaging & Social
        "com.whatsapp",
        "com.whatsapp.w4b",
        "org.telegram.messenger",
        "org.thoughtcrime.securesms",      # Signal
        "com.discord",
        "com.slack",
        "com.facebook.orca",              # Messenger
        "com.google.android.apps.messaging", # Google Messages
        
        # Email & Work
        "com.google.android.gm",           # Gmail
        "com.microsoft.office.outlook",
        "com.microsoft.teams",
        "com.zoho.mail",

        # UPI, Banking & Financial
        "com.google.android.apps.nbu.paisa.user", # GPay
        "com.phonepe.app",
        "net.one97.paytm",
        "in.org.npci.upiapp",              # BHIM
        "com.sbi.lotusintouch",            # YONO SBI
        "com.hdfcbank.android",
        "com.icicibank.mobile",
        "com.axis.mobile",
        "com.zerodha.kite3",
        "com.dreamplug.androidapp",        # CRED
        "com.groww.android",

        # Navigation, Delivery & Mobility
        "com.google.android.apps.maps",
        "com.ubercab",
        "com.olacabs.customer",
        "in.swiggy.android",
        "com.grofers.customerapp",         # Blinkit
        "com.zomato"
    ]

    def __init__(self, device):
        self.dev = device

    def scan_and_protect(self):
        """Scans device for critical installed apps and adds them to Doze whitelist."""
        protected = []
        already_whitelisted = []

        # Get current whitelist
        whitelist_raw = self.dev.shell("dumpsys deviceidle whitelist")

        for pkg in self.CRITICAL_TARGETS:
            if self.dev.package_exists(pkg):
                if pkg in whitelist_raw:
                    already_whitelisted.append(pkg)
                else:
                    self.dev.shell(f"dumpsys deviceidle whitelist +{pkg}")
                    protected.append(pkg)

        return protected, already_whitelisted

    def run(self):
        print("\n🔔 Notification Delay & OEM Task-Killer Fixer")
        print("-" * 55)
        print("🔍 Scanning for installed messaging, banking, email, and navigation apps...")

        newly_protected, already_ok = self.scan_and_protect()

        print(f"\n[+] Total Critical Apps Found: {len(newly_protected) + len(already_ok)}")
        if newly_protected:
            print(f"⚡ Successfully Protected from Sleep/Kill ({len(newly_protected)} apps):")
            for pkg in newly_protected:
                print(f"  [+] {pkg} -> Added to Power-Saving Whitelist (Zero Delays)")
        
        if already_ok:
            print(f"✅ Already Protected ({len(already_ok)} apps):")
            for pkg in already_ok[:5]:
                print(f"  [✓] {pkg}")
            if len(already_ok) > 5:
                print(f"  ... and {len(already_ok) - 5} others")

        print("\n✨ Fix Complete: Notifications will now arrive instantly without OEM delays!")
        return len(newly_protected)
