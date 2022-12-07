"""
Database unseeder for Lessons app.

Deletes from the database all users that are not superusers.

version 2022.12.07
"""

from django.core.management.base import BaseCommand, CommandError
from lessons.models import User

from lessons.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter(is_superuser=False).delete()
        print("The unseed command has not been implemented yet!")
        print("TO DO: Create an unseed command following the instructions of the assignment carefully.")
