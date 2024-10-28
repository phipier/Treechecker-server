from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from api.models import Country  # Ensure this matches the location of your Country model

# file used to create a list of users and passwords (for training purposes)

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with dummy users for BTSF training'

    def add_arguments(self, parser):
        parser.add_argument('num_users', type=int, help='Number of dummy users to create')

    def handle(self, *args, **kwargs):
        num_users = kwargs['num_users']
        password = 'PASSWORD'
        
        # Assuming 'Country' model exists and has at least one entry
        default_country = Country.objects.first()
        if not default_country:
            self.stdout.write(self.style.ERROR('No country found in database. Please add countries first.'))
            return

        # Retrieve or create the 'Team' group
        team_group, created = Group.objects.get_or_create(name='Team')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Group "Team" was created.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Group "Team" already exists.'))

        for i in range(1, num_users + 1):
            username = f'user{i}'
            email = f'user{i}@btsf.eu'
            name = f'User {i}'
            occupation = 'Developer'  # Example occupation, adjust as needed
            language = 'English'  # Example language, adjust as needed

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'name': name,
                    'password': password,
                    'occupation': occupation,
                    'country': default_country,
                    'language': language,
                    'is_staff': True,  # Set is_staff within defaults
                }
            )

            if created:
                user.set_password(password)
                user.save()
                user.groups.add(team_group)  # Add the user to the 'Team' group
                self.stdout.write(self.style.SUCCESS(f'Successfully created user {username} with staff access and added to "Team" group.'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already exists'))

