from django.core.management.base import BaseCommand, CommandError
from lessons.models import Student

class Command(BaseCommand):
    def handle(self, *args, **options):
        Student.objects.filter(is_staff=False, is_superuser=False).delete()
        print("The unseed command has not been implemented yet!")
        print("TO DO: Create an unseed command following the instructions of the assignment carefully.")
