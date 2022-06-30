from django.urls import path, re_path

from .views import OrderList, OrderDelete, OrderRead, OrderItemsCreate, OrderItemsUpdate, \
    order_forming_complete, get_product_price

app_name = 'ordersapp'


urlpatterns = [
    re_path(r'^$', OrderList.as_view(), name='orders_list'),
    re_path(r'^forming/complete/(?P<pk>\d+)/$',
            order_forming_complete, name='order_forming_complete'),
    re_path(r'^create/$', OrderItemsCreate.as_view(),
            name='order_create'),
    re_path(r'^read/(?P<pk>\d+)/$', OrderRead.as_view(),
            name='order_read'),
    re_path(r'^update/(?P<pk>\d+)/$', OrderItemsUpdate.as_view(),
            name='order_update'),
    re_path(r'^delete/(?P<pk>\d+)/$', OrderDelete.as_view(),
            name='order_delete'),
    re_path(r'^product/(?P<pk>\d+)/price/$', get_product_price)
]
