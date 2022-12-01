# Generated by Django 4.1.3 on 2022-11-28 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0003_alter_user_balance_invoice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessonrequest',
            name='extra_requests',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='user',
            name='account_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Student'), (2, 'Teacher'), (3, 'Administrator'), (4, 'Director')], default=1),
        ),
    ]