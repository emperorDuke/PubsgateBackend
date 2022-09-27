# Generated by Django 4.0.3 on 2022-09-18 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Carts', '0001_initial'),
        ('Contents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='manuscript',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cart_items', to='Contents.manuscript'),
        ),
    ]