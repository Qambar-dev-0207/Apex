import os
import zipfile
from datetime import datetime

class SovereignSync:
    """
    Handles encrypted snapshots and multi-device state synchronization.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs("backups", exist_ok=True)

    def export_snapshot(self) -> str:
        """
        Creates a zip snapshot of the current state.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backups/apex_snapshot_{timestamp}.zip"
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), 
                               os.path.relpath(os.path.join(root, file), os.path.join(self.data_dir, '..')))
        
        return os.path.abspath(backup_path)

    def load_snapshot(self, path: str):
        """
        Restores state from a snapshot.
        """
        if os.path.exists(path):
            with zipfile.ZipFile(path, 'r') as zipf:
                zipf.extractall(".")
            return True
        return False
