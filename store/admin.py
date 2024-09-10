from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from .models import *
admin.site.register(Promotion)


class ProductInventoryFilter(admin.SimpleListFilter):
    title = 'Inventory'
    parameter_name = 'inventory'
    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ('<10', 'Low'),
            ('>30', 'Ok'), 
        ]
    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        elif self.value() == '>30':
            return queryset.filter(inventory__gt=30)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    list_display = ['title', 'unit_price', 'collection', 'inventory_status', 'inventory']    
    list_per_page = 20
    list_select_related = ['collection']
    list_filter = ['collection', 'last_update', ProductInventoryFilter]
    search_fields = ['title']

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'

    @admin.display(description='Clear Inventory.')
    def clear_inventory(self, request, queryset):
        inventory_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{inventory_count} products were successfully updated.',
            messages.SUCCESS
        )
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_count'] # second field: to find out how many products we have related to collection.
    list_per_page = 20
    search_fields = ['title']
    autocomplete_fields = ['featured_product']

    @admin.display(ordering='product_count')
    def product_count(self, collection):
        # reverse('admin:app_model_page') target page links:
        related_url = reverse('admin:store_product_changelist')\
        + '?' + urlencode({
            'collection_id': str(collection.pk)
        })
        # make a value of a field to clickable and ralate to links.
        return format_html(f'<a href="{related_url}">{collection.product_count}</a>')

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            product_count = Count('products')
        )
    

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'order_count']
    list_editable = ['membership']
    list_per_page = 20
    search_fields = ['first_name', 'last_name', 'first_name__istartswith', 'last_name__istartswith']
    
    @admin.display(ordering='order_count')
    def order_count(self, customer):
        related_url = reverse('admin:store_order_changelist')\
        + '?' + urlencode({
            'customer_id': str(customer.pk)
        })
        return format_html(f'<a href="{related_url}">{customer.order_count}</a>')
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            order_count = Count('order')
        )


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'placed_at', 'payment_status']
    list_editable = ['payment_status']
    search_fields = ['payment_status']
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_per_page = 20


@admin.register(Address)
class AdressAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']