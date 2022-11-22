# Generated by Django 4.1.3 on 2022-11-22 11:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0002_user_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='balance',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('invoice_id', models.CharField(blank=True, max_length=7)),
                ('number_of_lessons', models.PositiveIntegerField(default=1)),
                ('lesson_duration', models.PositiveIntegerField(default=1)),
                ('hourly_cost', models.PositiveIntegerField(default=1)),
                ('total_price', models.PositiveIntegerField(blank=True)),
                ('associated_student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
