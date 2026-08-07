# Week 4 - Backup Storage - July 20 - Athrva
# Backup and restore functionality for state storage

import sqlite3
import shutil
import os
from datetime import datetime
from pychronicle.storage import StateStorage

class BackupStorage:
    def __init__(self, db_path="pychronicle.db"):
        self.db_path = db_path
        self.storage = StateStorage(db_path)

    def create_backup(self):
        """Create a backup of the database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"pychronicle_backup_{timestamp}.db"
        if os.path.exists(self.db_path):
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Backup created: {backup_path}")
        else:
            print("⚠️ No database found to backup")
        return backup_path

    def get_record_count(self):
        """Get total records in database"""
        states = self.storage.get_all_states()
        return len(states)

    def clear_database(self):
        """Clear all states from database"""
        self.storage.conn.execute(
            'DELETE FROM variable_states'
        )
        self.storage.conn.commit()
        print("✅ Database cleared!")

    def display_info(self):
        print("\n=== Database Info ===")
        print(f"Path:    {self.db_path}")
        print(f"Records: {self.get_record_count()}")
        if os.path.exists(self.db_path):
            size = os.path.getsize(self.db_path)
            print(f"Size:    {size/1024:.2f} KB")

if __name__ == "__main__":
    backup = BackupStorage()
    backup.display_info()
    backup.create_backup()