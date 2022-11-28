from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from lessons.models import User, LessonRequest

class Command(BaseCommand):
    PASSWORD = "Password123"
    SEED_COUNT = 5
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

        teacher = User.objects.create_user(
            username="@teacher",
            first_name="teacher",
            last_name="teacher",
            email="teacher@gmail.com",
            password=Command.PASSWORD,
            account_type=2
        )

        director = User.objects.create_user(
            username="@director",
            first_name="director",
            last_name="director",
            email="director@gmail.com",
            password=Command.PASSWORD,
            account_type=3
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

        print("The seed command is under construction, and may be unstable due to changing fields")





    def _create_request(self, user, count):
        day = count,
        lessons = 10 - count
        while count > 0:
            LessonRequest.objects.create(
                days_available=str(count%7+1),
                num_lessons=4,
                lesson_gap_weeks=LessonRequest.LessonGap.FORTNIGHTLY,
                lesson_duration_hours=1,
                requestor=user,
                extra_requests='I like music',
                is_booked=(count % 2 == 0),
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
