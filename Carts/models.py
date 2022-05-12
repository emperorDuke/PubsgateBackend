from django.conf import settings
from django.db import models

from Contents.models import Manuscript

# Create your models here.


class Cart(models.Model):
    """
    The user / buyer cart
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='cart',
        on_delete=models.CASCADE
    )

    updated_at = models.DateTimeField('updated_at', auto_now=True)

    class Meta:
        verbose_name = 'cart'
        verbose_name_plural = 'carts'
        db_table = 'carts'


class CartItem(models.Model):
    """
    The item in the cart, in this case the item is a manuscript
    """

    cart = models.ForeignKey(
        Cart,
        related_name='cart_items',
        on_delete=models.CASCADE
    )

    manuscript = models.ForeignKey(
        Manuscript,
        related_name='cart_items',
        null=True,
        on_delete=models.SET_NULL
    )

    quantity = models.PositiveIntegerField('quantity', default=1, null=True)
    added_at = models.DateTimeField('added_at', auto_now_add=True)

    class Meta:
        verbose_name = 'cart_item'
        verbose_name_plural = 'cart_items'
        ordering = ['-added_at']
        db_table = 'cart_items'
