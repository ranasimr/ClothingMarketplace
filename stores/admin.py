from django.contrib import admin
from stores.models import  Product,Variation,ReviewRating,ProductGallery
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'description', 'price','stock', 'category', 'images', 'created_date', 'modified_date', 'is_available')
    prepopulated_fields={'slug':('product_name',)}
    inlines = [ProductGalleryInline]

# Register your models here.
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value','is_active')
    list_editable =('is_active',)
    list_filter= ('product', 'variation_category', 'variation_value')
admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery) 


