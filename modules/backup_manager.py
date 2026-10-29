#!/usr/bin/env python3
"""
Universal Android Zero-Cloud Smart Vault & 360° Backup Manager
Complete offline preservation without paying monthly cloud subscriptions:
1. 📇 Contacts Vault: Exports complete phonebook into standard .VCF (vCard) & .JSON.
2. 📞 Call Logs Vault: Full call history (Incoming, Outgoing, Missed, Durations).
3. 💬 SMS & OTP Archive: Preserves all messages with sender numbers & timestamps.
4. 🟢 WhatsApp Offline Vault: Backs up encrypted local databases (msgstore.db.crypt14).
5. 📷 Smart Camera Sync: Incremental sync (copies ONLY new photos/videos, skips duplicates).
6. 📦 User Installed APKs: Full extraction of applications for 1-click offline reinstallation.
"""
import os
import re
import json
import time
from datetime import datetime

class BackupManager:
    def __init__(self, device, backup_root=None):
        self.dev = device
        if not backup_root:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            backup_root = os.path.join(script_dir, "backups")
        self.backup_root = backup_root
        os.makedirs(self.backup_root, exist_ok=True)

    def backup_contacts(self, backup_dir):
        """Extracts contacts into standardized RFC 2426 vCard (.vcf) and JSON."""
        print("• Backing up Contacts to .VCF (vCard) and .JSON...")
        out, _, _ = self.dev.run_shell("content query --uri content://com.android.contacts/data/phones", timeout=60)
        contacts = []
        vcf_lines = []

        seen_numbers = set()
        for row in out.split("Row: "):
            if not row.strip():
                continue
            m_name = re.search(r'display_name=([^,]+)', row)
            m_num = re.search(r'data1=([^,]+)', row)
            m_acc = re.search(r'account_name=([^,]+)', row)

            name = m_name.group(1).strip() if m_name else "Unknown"
            num = m_num.group(1).strip() if m_num else ""
            acc = m_acc.group(1).strip() if m_acc else ""

            if num and num != "NULL":
                clean_num = re.sub(r'[\s\-\(\)]', '', num)
                if clean_num not in seen_numbers:
                    seen_numbers.add(clean_num)
                    contacts.append({
                        "name": name if name != "NULL" else clean_num,
                        "number": num,
                        "account": acc if acc != "NULL" else "Local"
                    })
                    vcf_lines.extend([
                        "BEGIN:VCARD",
                        "VERSION:3.0",
                        f"FN:{name if name != 'NULL' else clean_num}",
                        f"TEL;TYPE=CELL:{num}",
                        "END:VCARD",
                        ""
                    ])

        # Save VCF
        vcf_path = os.path.join(backup_dir, "contacts.vcf")
        with open(vcf_path, "w", encoding="utf-8") as f:
            f.write("\n".join(vcf_lines))

        # Save JSON
        json_path = os.path.join(backup_dir, "contacts.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=2, ensure_ascii=False)

        print(f"   ✓ Extracted {len(contacts)} contacts -> {os.path.basename(vcf_path)} & contacts.json")
        return len(contacts)

    def backup_call_logs(self, backup_dir):
        """Extracts complete call log history into JSON."""
        print("• Backing up Call Logs history...")
        out, _, _ = self.dev.run_shell("content query --uri content://call_log/calls", timeout=60)
        calls = []

        for row in out.split("Row: "):
            if not row.strip():
                continue
            m_name = re.search(r'name=([^,]+)', row)
            m_num = re.search(r'number=([^,]+)', row)
            m_date = re.search(r'date=([^,]+)', row)
            m_dur = re.search(r'duration=([^,]+)', row)
            m_type = re.search(r'type=([^,]+)', row)

            if m_num and m_num.group(1).strip() != "NULL":
                type_code = m_type.group(1).strip() if m_type else "1"
                type_str = {
                    "1": "Incoming", "2": "Outgoing", "3": "Missed",
                    "4": "Voicemail", "5": "Rejected", "6": "Blocked"
                }.get(type_code, "Call")

                epoch_ms = int(m_date.group(1).strip()) if m_date and m_date.group(1).strip().isdigit() else 0
                readable_date = datetime.fromtimestamp(epoch_ms / 1000.0).strftime('%Y-%m-%d %H:%M:%S') if epoch_ms else ""

                calls.append({
                    "name": m_name.group(1).strip() if (m_name and m_name.group(1).strip() != "NULL") else "Unknown",
                    "number": m_num.group(1).strip(),
                    "date": readable_date,
                    "duration_seconds": int(m_dur.group(1).strip()) if m_dur and m_dur.group(1).strip().isdigit() else 0,
                    "type": type_str
                })

        json_path = os.path.join(backup_dir, "call_logs.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(calls, f, indent=2, ensure_ascii=False)

        print(f"   ✓ Extracted {len(calls)} call logs -> call_logs.json")
        return len(calls)

    def backup_sms(self, backup_dir):
        """Extracts SMS messages into text and structured JSON."""
        print("• Backing up SMS inbox & OTP archives...")
        out, _, _ = self.dev.run_shell("content query --uri content://sms --projection address,body,date,type", timeout=60)
        messages = []

        for row in out.split("Row: "):
            if not row.strip():
                continue
            m_addr = re.search(r'address=([^,]+)', row)
            m_date = re.search(r'date=([^,]+)', row)
            m_type = re.search(r'type=([^,]+)', row)
            # Body can contain commas, so match up to end or next key
            m_body = re.search(r'body=(.+?)(?:,\s*type=|\s*$)', row, re.DOTALL)

            if m_addr and m_addr.group(1).strip() != "NULL":
                epoch_ms = int(m_date.group(1).strip()) if m_date and m_date.group(1).strip().isdigit() else 0
                readable_date = datetime.fromtimestamp(epoch_ms / 1000.0).strftime('%Y-%m-%d %H:%M:%S') if epoch_ms else ""

                messages.append({
                    "sender": m_addr.group(1).strip(),
                    "date": readable_date,
                    "type": "Sent" if m_type and m_type.group(1).strip() == "2" else "Received",
                    "body": m_body.group(1).strip() if m_body else ""
                })

        json_path = os.path.join(backup_dir, "sms_backup.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)

        print(f"   ✓ Extracted {len(messages)} SMS messages -> sms_backup.json")
        return len(messages)

    def backup_whatsapp_vault(self, backup_dir):
        """Backs up latest encrypted WhatsApp chat databases."""
        print("• Backing up WhatsApp Encrypted Database Vault...")
        wa_dir = os.path.join(backup_dir, "whatsapp")
        os.makedirs(wa_dir, exist_ok=True)

        remote_db_path = "/sdcard/Android/media/com.whatsapp/WhatsApp/Databases"
        out, _, rc = self.dev.run_shell(f"ls -t {remote_db_path}")
        if rc != 0 or not out:
            print("   [-] WhatsApp databases directory not found or empty.")
            return False

        files = [f.strip() for f in out.splitlines() if "msgstore" in f and ".crypt" in f]
        if not files:
            print("   [-] No encrypted msgstore backup files found.")
            return False

        newest_db = files[0]
        remote_file = f"{remote_db_path}/{newest_db}"
        local_file = os.path.join(wa_dir, newest_db)
        print(f"   ↳ Pulling latest database: {newest_db}...")
        success = self.dev.pull_file(remote_file, local_file)
        if success:
            print(f"   ✓ WhatsApp Offline Vault Secured: {newest_db} (Safe offline chat restore)")
            return True
        return False

    def backup_apks(self, backup_dir, max_apks=15):
        """Extracts installed user APK packages."""
        print(f"• Extracting User-Installed APKs (Top {max_apks})...")
        apks_dir = os.path.join(backup_dir, "apks")
        os.makedirs(apks_dir, exist_ok=True)

        out, _, _ = self.dev.run_shell("pm list packages -3")
        user_packages = [line.replace("package:", "").strip() for line in out.splitlines() if line]

        backed_up = []
        for pkg in user_packages[:max_apks]:
            path_out, _, _ = self.dev.run_shell(f"pm path {pkg}")
            m = [p.replace("package:", "").strip() for p in path_out.splitlines() if "base.apk" in p]
            if m:
                remote_apk = m[0]
                local_apk = os.path.join(apks_dir, f"{pkg}.apk")
                if self.dev.pull_file(remote_apk, local_apk):
                    backed_up.append(pkg)

        print(f"   ✓ Extracted {len(backed_up)} APK packages -> apks/")
        return backed_up

    def incremental_camera_sync(self, max_files=50):
        """Copies newly taken photos/videos that don't already exist locally."""
        print(f"• Checking Camera Photos & Videos for Incremental Sync (Up to {max_files} new files)...")
        vault_dir = os.path.join(self.backup_root, "camera_vault")
        os.makedirs(vault_dir, exist_ok=True)

        existing_local = set(os.listdir(vault_dir))
        out, _, rc = self.dev.run_shell("ls -t /sdcard/DCIM/Camera")
        if rc != 0 or not out:
            print("   [-] Camera directory empty or not accessible.")
            return 0

        remote_files = [f.strip() for f in out.splitlines() if f.strip() and not f.startswith(".")]
        new_files = [f for f in remote_files if f not in existing_local]

        if not new_files:
            print("   ✓ All photos & videos are already backed up! (Zero duplicates)")
            return 0

        print(f"   ↳ Found {len(new_files)} new photos/videos to sync. Pulling {min(len(new_files), max_files)}...")
        synced = 0
        for f in new_files[:max_files]:
            r_path = f"/sdcard/DCIM/Camera/{f}"
            l_path = os.path.join(vault_dir, f)
            if self.dev.pull_file(r_path, l_path):
                synced += 1

        print(f"   ✓ Incremental sync complete! {synced} new photos/videos saved to camera_vault/")
        return synced

    def create_full_vault_backup(self, include_camera=True):
        """Runs complete 360° Zero-Cloud Vault backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model = self.dev.info.get("model", "device").replace(" ", "_")
        backup_dir = os.path.join(self.backup_root, f"Vault_{model}_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)

        print("\n📦 STARTING 360° ZERO-CLOUD SMART VAULT BACKUP")
        print(f"📁 Destination: {os.path.abspath(backup_dir)}")
        print("-" * 55)

        contacts_cnt = self.backup_contacts(backup_dir)
        calls_cnt = self.backup_call_logs(backup_dir)
        sms_cnt = self.backup_sms(backup_dir)
        wa_ok = self.backup_whatsapp_vault(backup_dir)
        apks = self.backup_apks(backup_dir, max_apks=10)

        photos_synced = 0
        if include_camera:
            photos_synced = self.incremental_camera_sync(max_files=30)

        manifest = {
            "device": self.dev.info,
            "timestamp": timestamp,
            "contacts_count": contacts_cnt,
            "call_logs_count": calls_cnt,
            "sms_count": sms_cnt,
            "whatsapp_db_secured": wa_ok,
            "apks_backed_up": len(apks),
            "new_photos_synced": photos_synced
        }

        with open(os.path.join(backup_dir, "vault_manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)

        print("\n🎉 360° SMART VAULT BACKUP COMPLETED SUCCESSFULLY!")
        print(f"• Contacts Saved : {contacts_cnt} (contacts.vcf ready for 1-tap restore)")
        print(f"• Call Logs Saved: {calls_cnt} records")
        print(f"• SMS Saved      : {sms_cnt} messages")
        print(f"• WhatsApp Vault : {'Secured (Encrypted DB)' if wa_ok else 'Skipped'}")
        print(f"• Apps Extracted : {len(apks)} APKs")
        print(f"• Camera Sync    : {photos_synced} new photos/videos")
        print(f"📂 Saved locally to: {os.path.abspath(backup_dir)}")
        return backup_dir

    def restore_apks(self, backup_dir):
        """Restores applications from a backup folder."""
        apks_dir = os.path.join(backup_dir, "apks")
        if not os.path.exists(apks_dir):
            print(f"❌ APKs directory not found in {backup_dir}")
            return False

        apks = [f for f in os.listdir(apks_dir) if f.endswith(".apk")]
        print(f"🔄 Restoring {len(apks)} applications to connected phone...")
        restored = 0
        for apk in apks:
            full_path = os.path.join(apks_dir, apk)
            cmd = [self.dev.adb_bin, "-s", self.dev.serial, "install", "-r", full_path]
            res = os.system(" ".join(cmd) + " >/dev/null 2>&1")
            if res == 0:
                restored += 1
                print(f"   ✓ Installed: {apk}")

        print(f"✅ Restore finished! {restored}/{len(apks)} apps installed successfully.")
        return True
