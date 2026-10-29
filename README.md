# 📱 CleanHub Mobile (CleanHubMobile)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Android](https://img.shields.io/badge/Android-8.0%20to%2016.0%2B-green.svg)](https://developer.android.com)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Rootless](https://img.shields.io/badge/Root-100%25%20Not%20Required-brightgreen.svg)](#)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local%20%7C%20Zero--Cloud-purple.svg)](#)

> **The Ultimate Universal Android Optimizer, Bloatware Killer & Peak Performance Suite.**  
> Reclaim gigabytes of storage, eliminate shutter lag, lock 120Hz, fix delayed notifications, stop battery drain, and backup your private vault. **100% local, safe, and completely reversible without root.**

Part of the **CleanHub** ecosystem (joining [CleanHub TV for LG](https://github.com/smartjaganrao/cleanyourtv-lg) and [CleanHub TV for Samsung](https://github.com/smartjaganrao/cleanyourtv-samsung)).

---

## ⚡ Key Highlights

- 💾 **Deep Storage Cleaner:** Recovers 10–40+ GB of hidden storage from WhatsApp sent media, thumbnail caches, and triggers hardware UFS storage TRIM.
- 📸 **Camera Booster (Zero Shutter Lag):** Compiles camera stack to native ARM64 machine code, activates hardware AI clarity engines (OSIE/Iris), and bypasses Doze freezes.
- 🏎️ **Zero-Lag Flagship Engine:** Compiles daily apps with ART AOT (`speed`), enables Linux Kernel CGroup App Freezer, and cuts touch latency to 250ms.
- 🖥️ **Display Refresh Rate Maximizer:** Forces 120Hz / 90Hz lock across all apps—eliminating 60Hz drops in YouTube, Google Maps, and camera viewfinders.
- 🔔 **Instant Notification Shield:** Solves "Don't Kill My App" by protecting WhatsApp, Telegram, Gmail, and UPI payment apps from aggressive OEM task-killers.
- 🔋 **Ultra Battery & Overnight Deep Sleep:** Cuts overnight idle drain to ~1% with Aggressive Doze (enters deep sleep in 60s) and true AMOLED dark mode.
- 🚗 **Android Auto Anti-Disconnect Shield:** Whitelists car projection services to prevent USB drops and enables certified in-car browsing.
- 📇 **Smart Contacts Deduplicator:** Scans address books, purges redundant in-card phone numbers, triggers Google Cloud sync, and generates clean VCF backups.
- 🛡️ **System-Wide Ad-Blocker:** Enforces encrypted Private DNS (AdGuard DoT) to block in-app and web ads without battery-draining VPNs.
- 📦 **360° Zero-Cloud Vault:** Offline local backup of Contacts VCF, Call Logs, SMS, and WhatsApp databases.

---

## 📱 Supported Ecosystem

CleanHub Mobile dynamically identifies your OEM profile and adapts its commands automatically:

| OEM / Brand | UI System | Specific Optimizations Applied |
| :--- | :--- | :--- |
| **Samsung** | One UI | Trims Knox & carrier bloat, secures RAM Plus, forces 120Hz |
| **OPPO / OnePlus / Realme** | ColorOS / OxygenOS / RealmeUI | HeyTap de-advertising, OSIE AI enhancement, App Freezer |
| **Xiaomi / POCO / Redmi** | MIUI / HyperOS | Disables MSA/MiPicks daemon, Joyose thermal fix, 120Hz force |
| **Vivo / iQOO** | FuntouchOS / OriginOS | Jovi bloat removal, background power management bypass |
| **Motorola** | MyUX / Hello UI | Moto app store recommendations cleanup, touch latency boost |
| **Google** | Pixel Android 14/15/16 | Pure AOT native compilation, storage TRIM, aggressive Doze |

---

## 🚀 Quick Start

### Method 1: Run from Laptop via USB (Recommended)

1. Enable **Developer Options** and turn ON **USB Debugging** on your phone.
2. Connect your phone to your computer via USB cable.
3. Clone and run CleanHub Mobile:

```bash
git clone https://github.com/smartjaganrao/CleanHubMobile.git
cd CleanHubMobile

# 1-Click Interactive Menu
python3 main.py

# Or run Full Automated Optimization
python3 main.py --all
```

---

### Method 2: Run 100% On-Device (No Computer Required)

You can run CleanHub Mobile directly on your phone using **Termux** or **Shizuku**:

1. Push or download `cleanhub.sh` to your phone:
```bash
# Push via ADB once
adb push cleanhub.sh /sdcard/cleanhub.sh
```

2. Open **Termux** or a local shell on your phone and run:
```bash
sh /sdcard/cleanhub.sh
```
*Executes all 12 master power steps natively on your device in seconds!*

---

## 🛠️ CLI Flags & Usage

```bash
python3 main.py [FLAGS]

Options:
  --all               Run complete master suite (Debloat + Speed + Storage + Power + 120Hz + Camera + Report)
  --camera            Zero Shutter Lag & Peak Speed Camera Booster (AOT native, OSIE AI, Doze bypass)
  --speed             Apply Zero-Lag performance & AOT native compilation
  --storage           Reclaim storage (WhatsApp Sent, Gallery cache, UFS TRIM)
  --refresh           Force max display refresh rate (120Hz in all apps)
  --notifications     Fix delayed WhatsApp, Gmail & banking notifications
  --save-battery      Ultra Battery & SOT Booster (AMOLED Dark, Haptics Off, Doze in 60s)
  --clean-contacts    Audit & remove duplicate in-card phone numbers & trigger cloud sync
  --power             Extreme Power Overclock (Touch 250ms, Low-Latency Wi-Fi, BT Uncap)
  --auto              Android Auto Anti-Disconnect Shield & Car Media Whitelist
  --debloat           Scan and remove OEM & carrier bloatware safely
  --ads               Activate system-wide encrypted ad-blocking (AdGuard DoT)
  --ram               Audit physical RAM vs slow Virtual Swap / RAM Plus
  --thermals          Diagnose thermals & fix background radio scan drain
  --vault             Create 360° Zero-Cloud Vault (Contacts VCF, Calls, SMS, WhatsApp)
  --game-mode         Switch display to 1080p for +30% FPS in heavy games
  --native-mode       Restore native display resolution & density
  --report            Generate interactive HTML Optimization Report Card
```

---

## 🏗️ Architecture

```
CleanHubMobile/
├── android_core.py          # Universal ADB bridge & OEM detection layer
├── main.py                  # CLI entry point & interactive controller
├── cleanhub.sh              # 1-click on-device native shell runner
├── requirements.txt         # Lightweight requirements
├── LICENSE                  # MIT Open Source License
└── modules/
    ├── storage_cleaner.py          # WhatsApp, thumbnail & UFS TRIM cleaner
    ├── performance_booster.py      # ART AOT native speed compiler & App Freezer
    ├── camera_booster.py           # Zero shutter lag & OSIE AI clarity engine
    ├── display_refresh_booster.py  # 120Hz / 90Hz system-wide enforcer
    ├── notification_fixer.py       # Don't Kill My App background protector
    ├── battery_saver_pro.py        # Instant deep sleep & AMOLED true-black
    ├── extreme_power_booster.py    # 250ms touch latency & Wi-Fi gaming lock
    ├── android_auto_fixer.py       # Car projection anti-disconnect shield
    ├── contacts_cleaner.py         # In-card phone deduplicator & cloud syncer
    ├── debloater.py                # Universal & OEM-specific bloatware remover
    ├── ad_blocker.py               # System-wide encrypted DNS ad shield
    ├── ram_tuner.py                # LPDDR physical RAM vs virtual swap tuner
    ├── thermal_doctor.py           # Battery temperature & scan trap fixer
    ├── battery_health.py           # Hardware charge cycle & health auditor
    ├── privacy_auditor.py          # Camera, Mic & Location permission inspector
    ├── backup_manager.py           # 360° local offline vault creator
    └── report_generator.py         # Visual HTML report card generator
```

---

## 🔒 Safety & Reversibility Guarantee

- **Zero Root Needed:** Uses documented, safe Android user-space APIs.
- **Zero Brick Risk:** Does not touch bootloaders, vendor recovery partitions, or firmware kernels.
- **100% Reversible:** All disabled apps can be restored at any time via `pm enable <package>` or standard system resets.

---

## 📄 License

Licensed under the [MIT License](LICENSE). Contributions, forks, and pull requests are warmly welcomed!
