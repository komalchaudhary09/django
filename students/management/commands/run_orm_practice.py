import pprint
from django.core.management.base import BaseCommand
from students.orm_practice import run_all_orm_exercises


class Command(BaseCommand):
    help = 'Executes and prints results for all 10 Django ORM practice topics + Bonus tasks.'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.MIGRATE_HEADING("DJANGO ORM PRACTICE & DEMONSTRATION SUITE"))
        self.stdout.write("=" * 80 + "\n")

        sections = run_all_orm_exercises()

        for idx, section in enumerate(sections, 1):
            self.stdout.write(self.style.SUCCESS(f"\n[{section['title']}]"))
            self.stdout.write(f"Description: {section['description']}")
            self.stdout.write("-" * 80)

            for ex in section['examples']:
                self.stdout.write(self.style.WARNING(f"  • {ex['subtitle']}"))
                self.stdout.write("    Query Code:")
                for line in ex['code'].split('\n'):
                    self.stdout.write(f"      {line}")

                if 'explanation' in ex:
                    self.stdout.write(f"    Explanation: {ex['explanation']}")

                if 'sql' in ex:
                    self.stdout.write(f"    Generated SQL: {ex['sql']}")

                self.stdout.write("    Output / Result:")
                if isinstance(ex['result'], (list, dict)):
                    formatted = pprint.pformat(ex['result'], indent=6)
                    self.stdout.write(f"{formatted}")
                else:
                    self.stdout.write(f"      {ex['result']}")
                self.stdout.write("")

        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("All 10 ORM Practice Modules & Bonus Tasks executed successfully!"))
        self.stdout.write("=" * 80)
