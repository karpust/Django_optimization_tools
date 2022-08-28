from django.utils.functional import cached_property
from django.db import models
from django.conf import settings
from mainapp.models import Product


# class BasketQuerySet(models.QuerySet):
#
#     def delete(self, *args, **kwargs):
#         for obj in self:
#             obj.product.quantity += obj.quantity
#             obj.product.save()
#         super(BasketQuerySet, self).delete(*args, **kwargs)


class Basket(models.Model):

    # objects = BasketQuerySet.as_manager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='количество', default=0)
    add_datetime = models.DateTimeField(verbose_name='время добавления', auto_now_add=True)

    @cached_property
    def get_items_cached(self):
        return Basket.objects.filter(user__id=self.user.id).select_related()

    @staticmethod
    def get_items(user):
        return Basket.objects.filter(user__id=user).select_related()

    @staticmethod
    def get_item(pk):
        return Basket.objects.filter(pk=pk).select_related().first()

    def _get_product_cost(self):
        "return cost of all products this type"
        return self.product.price * self.quantity
    product_cost = property(_get_product_cost)

    def _get_total_quantity(self):
        "return total quantity for user"
        # _items = Basket.objects.filter(user=self.user).select_related('product')
        _items = self.get_items_cached
        return sum(list(map(lambda x: x.quantity, _items)))
    total_quantity = property(_get_total_quantity)

    def _get_total_cost(self):
        "return total cost for user"
        # _items = Basket.objects.filter(user=self.user).select_related('product')
        _items = self.get_items_cached
        return sum(list(map(lambda x: x.product_cost, _items)))
    total_cost = property(_get_total_cost)

    # def save(self, *args, **kwargs):
    #     # если в корзине уже есть такой товар:
    #     if self.pk:
    #         # товары в базе -= кол-во одного товара в корзине - кол-во одного товара кот было в корзине:
    #         self.product.quantity -= self.quantity - self.__class__.get_item(self.pk).quantity
    #     else:
    #         # товары в базе -= товары в корзине
    #         self.product.quantity -= self.quantity
    #     self.product.save()
    #     super(self.__class__, self).save(*args, **kwargs)

