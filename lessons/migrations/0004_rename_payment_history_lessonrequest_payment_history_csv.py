# Generated by Django 4.1.3 on 2022-12-01 12:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0003_lessonrequest_payment_history'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lessonrequest',
            old_name='payment_history',
            new_name='payment_history_csv',
        ),
    ]
