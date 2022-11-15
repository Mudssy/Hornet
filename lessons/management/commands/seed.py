from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from lessons.models import User

class Command(BaseCommand):
    PASSWORD = "Password123"
    SEED_COUNT = 100

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
    def handle(self, *args, **options):
        user_count=0
        while user_count < Command.SEED_COUNT:
            while user_count < Command.SEED_COUNT:
                print(f'Seeding user {user_count}', end='\r')
                self._create_student()
                user_count += 1
            print('User seeding complete')

        first_name = 'Teacher'
        last_name = 'FirstTeacher'
        email = self._email(first_name, last_name)
        username = self._username(first_name, last_name)

        # Seed data handbook accounts
        User.objects.create_user(
            username=self._username(first_name, last_name),
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.PASSWORD,
            account_type=2
        )

        # Administrator
        staff = User.objects.create_user(
            username='@petrapickles',
            first_name="Petra",
            last_name="Pickles",
            email="petra.pickles@example.org",
            password=Command.PASSWORD,
            is_staff=True
        )


        print("The seed command has not been implemented yet!")
        print("TO DO: Create a seed command following the instructions of the assignment carefully.")



    # seeder creating student accounts
    def _create_student(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name, last_name)
        username = self._username(first_name, last_name)
        User.objects.create_user(
            username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.PASSWORD,
        )
    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email

    def _username(self, first_name, last_name):
        username = f'@{first_name}{last_name}'
        return username

