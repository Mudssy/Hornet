"""
Database seeder for Lessons app.

Seeds database with example users including a director, an administrator, a
teacher and a student

version 2022.12.07
"""


from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from lessons.models import User, LessonRequest
import random

class Command(BaseCommand):
    PASSWORD = "Password123"
    SEED_COUNT = 2
    REQUESTS_PER_USER = 2
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
    def handle(self, *args, **options):
        user_count=0
        while user_count < Command.SEED_COUNT:
            print(f'Seeding user {user_count}', end='\r')
            curr_user = self._create_student()
            self._create_request(curr_user, count=Command.REQUESTS_PER_USER)
            user_count += 1
        print('User seeding complete')


        first_name = 'John'
        last_name = 'Smith'
        email = self._email(first_name, last_name)
        username = self._username(first_name, last_name)

        # Seed data handbook accounts
        self.user = User.objects.create_user(
            username=self._username(first_name, last_name),
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.PASSWORD,
            account_type=1
        )

        self._create_request(user=self.user, count=Command.REQUESTS_PER_USER)

        # Student for seeder requirement
        johndoe = User.objects.create_user(
            username='@JohnDoe',
            first_name='John',
            last_name='Doe',
            email='john.doe@example.org',
            password=Command.PASSWORD,
            account_type=1
        )

        # Admin for seeder requirement
        petrapickles = User.objects.create_user(
            username='@PetraPickles',
            first_name='Petra',
            last_name='Pickles',
            email='petra.pickles@example.org',
            password=Command.PASSWORD,
            account_type=3,
            is_staff=True,
            is_superuser=False
        )

        #Director for seeder requirement
        martymajor = User.objects.create_user(
            username='@MartyMajor',
            first_name='Marty',
            last_name='Major',
            email='marty.major@example.org',
            password=Command.PASSWORD,
            account_type=4,
            is_staff=True,
            is_superuser=True
        )

        print("The seed command is under construction, and may be unstable due to changing fields")

    def _create_request(self, user, count):
        day = count,
        lessons = 10 - count
        POSSIBLE_GAPS = [LessonRequest.LessonGap.BIWEEKLY, LessonRequest.LessonGap.WEEKLY, LessonRequest.LessonGap.FORTNIGHTLY, LessonRequest.LessonGap.MONTHLY]
        while count > 0:
            LessonRequest.objects.create(
                days_available=random.randint(1,7),
                num_lessons=random.randint(1,5),
                lesson_gap_weeks=POSSIBLE_GAPS[random.randint(0,3)],
                lesson_duration_hours=random.randint(1,3),
                requestor=user,
                extra_requests=self.faker.sentence(),
            )
            count -= 1
    # seeder creating student accounts
    def _create_student(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name, last_name)
        username = self._username(first_name, last_name)
        user = User.objects.create_user(
            username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.PASSWORD,
        )
        return user

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email

    def _username(self, first_name, last_name):
        username = f'@{first_name}{last_name}'
        return username
