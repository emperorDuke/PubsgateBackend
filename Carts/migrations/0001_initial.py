# Generated by Django 4.0.3 on 2022-05-17 23:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
            ],
            options={
                'verbose_name': 'cart',
                'verbose_name_plural': 'carts',
                'db_table': 'carts',
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, null=True, verbose_name='quantity')),
                ('added_at', models.DateTimeField(auto_now_add=True, verbose_name='added_at')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='Carts.cart')),
            ],
            options={
                'verbose_name': 'cart_item',
                'verbose_name_plural': 'cart_items',
                'db_table': 'cart_items',
                'ordering': ['-added_at'],
            },
        ),
    ]
