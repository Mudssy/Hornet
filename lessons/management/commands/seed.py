"""
Database seeder for Lessons app.

Seeds database with example users including a director, an administrator, a
teacher and a student

version 2022.12.07
"""


from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from lessons.models import User, LessonRequest
from lessons.helpers import create_invoice, create_booked_lessons, update_invoice
import random

class Command(BaseCommand):
    PASSWORD = "Password123"
    SEED_COUNT = 20
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



        # Student for seeder requirement
        johndoe = User.objects.create_user(
            username='@JohnDoe',
            first_name='John',
            last_name='Doe',
            email='john.doe@example.org',
            password=Command.PASSWORD,
            account_type=1
        )

        # Approved and paid for request of John Doe
        johndoe_request = LessonRequest.objects.create(
            days_available=1,
            num_lessons=2,
            lesson_gap_weeks=LessonRequest.LessonGap.WEEKLY,
            lesson_duration_hours=3,
            requestor=johndoe,
            extra_requests="Music theory, and some cello please.",
        )
        johndoe_invoice = self._approve_request(johndoe_request)
        update_invoice(johndoe_invoice, johndoe_invoice.amount_outstanding)


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

        # Second admin for seeder requirement
        addisonadmin = User.objects.create_user(
            username='@AddisonAdmin',
            first_name='Addison',
            last_name='Admin',
            email='addison.admin@example.org',
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

    #function to create randomised request(s) for a given user
    def _create_request(self, user, count):

        POSSIBLE_GAPS = [LessonRequest.LessonGap.BIWEEKLY, LessonRequest.LessonGap.WEEKLY, LessonRequest.LessonGap.FORTNIGHTLY, LessonRequest.LessonGap.MONTHLY]
        while count > 0:
            #creating the request with random numbers and faker data
            request_temp = LessonRequest.objects.create(
                days_available=random.randint(1,7),
                num_lessons=random.randint(1,5),
                lesson_gap_weeks=POSSIBLE_GAPS[random.randint(0,3)],
                lesson_duration_hours=random.randint(1,3),
                requestor=user,
                extra_requests=self.faker.sentence(),
            )
            #80% of the time, the requests are approved
            if random.randint(1,10) < 8:
                invoice_temp = self._approve_request(request_temp)
                #equal chances of full, partial and no payment on the invoices of all approved requests
                prob_var = random.randint(1,3)
                if prob_var == 1:
                    update_invoice(invoice_temp, invoice_temp.amount_outstanding)
                elif prob_var == 2:
                    update_invoice(invoice_temp, invoice_temp.amount_outstanding/random.randint(1,10))

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

    def _approve_request(self, request):
        request.is_booked = True
        return_invoice = create_invoice(request)
        create_booked_lessons(request)
        request.save()
        return return_invoice
