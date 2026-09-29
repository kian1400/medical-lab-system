from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from pathlib import Path
import shutil


class Command(BaseCommand):
    help = "Backup the SQLite database to a timestamped file for local lab app backups."

    def handle(self, *args, **options):
        db_path = Path(settings.DATABASES['default']['NAME'])
        if not db_path.exists():
            self.stdout.write(self.style.WARNING(f"Database file not found: {db_path}"))
            return

        backup_dir = Path(settings.BASE_DIR) / 'backups'
        backup_dir.mkdir(exist_ok=True)
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"{db_path.stem}_{timestamp}.sqlite3"
        shutil.copy2(db_path, backup_file)
        self.stdout.write(self.style.SUCCESS(f"Database backed up to {backup_file}"))
