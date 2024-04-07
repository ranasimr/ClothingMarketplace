from django.contrib import admin
from stores.models import  Product,Variation,ReviewRating


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'description', 'price','stock', 'category', 'images', 'created_date', 'modified_date', 'is_available')
    prepopulated_fields={'slug':('product_name',)}
admin.site.register(Product,ProductAdmin)
# Register your models here.
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value','is_active')
    list_editable =('is_active',)
    list_filter= ('product', 'variation_category', 'variation_value')
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)