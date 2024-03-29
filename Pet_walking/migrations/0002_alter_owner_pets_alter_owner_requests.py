# Generated by Django 4.1.6 on 2023-02-14 19:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Pet_walking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='owner',
            name='pets',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pets', to='Pet_walking.pet'),
        ),
        migrations.AlterField(
            model_name='owner',
            name='requests',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='request', to='Pet_walking.request'),
        ),
    ]
