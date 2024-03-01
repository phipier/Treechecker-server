from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class Command(BaseCommand):
    help = 'Delete dummy users created for BTSF training'

    def handle(self, *args, **kwargs):
        # Filter users by email domain or username pattern
        users_to_delete = User.objects.filter(
            Q(email__endswith='@btsf.eu') |
            Q(username__startswith='user')
        )

        count = users_to_delete.count()
        
        if count > 0:
            # Confirm before deletion
            self.stdout.write(f'{count} users found that match the criteria and will be deleted.')
            confirm = input('Are you sure you want to delete these users? [y/N]: ')
            
            if confirm.lower() == 'y':
                users_to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} users.'))
            else:
                self.stdout.write(self.style.WARNING('Deletion cancelled.'))
        else:
            self.stdout.write(self.style.WARNING('No matching users found to delete.'))
