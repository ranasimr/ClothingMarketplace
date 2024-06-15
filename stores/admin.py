from django.contrib import admin
from django.db.models import Count
from stores.models import  Product,Variation,ReviewRating,ProductGallery
import admin_thumbnails
import xlsxwriter

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from django.http import HttpResponse

import xlsxwriter
def download_excel(model_admin, request, queryset):
    model_name = model_admin.model.__name__
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename={model_name}.xlsx'

    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()

    ordered_queryset = queryset.order_by('id')

    # Define excluded fields
    excluded_fields = ['slug', 'images', 'modified_date', 'created_date']

    # Define headers
    headers = [field.verbose_name for field in model_admin.model._meta.fields if field.name not in excluded_fields]
    headers.append('Orders')
    data = [headers]

    # Determine column widths based on content length
    column_widths = [len(header) for header in headers]

    for obj in ordered_queryset:
        data_row = [str(getattr(obj, field.name)) for field in model_admin.model._meta.fields if field.name not in excluded_fields]
        total_orders = obj.orderproduct_set.count()
        data_row.append(str(total_orders))
        data.append(data_row)

        # Update column widths based on cell content
        for i, value in enumerate(data_row):
            column_widths[i] = max(column_widths[i], len(value))

    for col_num, width in enumerate(column_widths):
        worksheet.set_column(col_num, col_num, width + 2)  # Adding some padding

    for row_num, row_data in enumerate(data):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_data)

    workbook.close()
    return response

download_excel.short_description = "Download Selected Items as Excel"


def download_pdf(self,request,queryset):
    model_name =self.model.__name__
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={model_name}.pdf'
    pdf =canvas.Canvas(response, pagesize=letter)
    pdf.setTitle('PDF Report')
    ordered_queryset = queryset.order_by('id')

    excluded_fields = ['slug','images','modified_date','created_date']
    
    headers = [field.verbose_name for field in self.model._meta.fields if field.name not in excluded_fields]
    headers.append('Orders')
    data =[headers]

    

    for obj in ordered_queryset:
        data_row = [str(getattr(obj,field.name)) for field in self.model._meta.fields if field.name not in excluded_fields]
        total_orders = obj.orderproduct_set.count()
        data_row.append(str(total_orders))
        data.append(data_row)

    table= Table(data)
    table.setStyle(TableStyle(
        [
         ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
         
         ('GRID', (0, 0), (-1, -1), 1, colors.black)   
        ]
    ))

    # # Calculate table width and height
    # table_width, table_height = table.wrap(0, 0)

    # canvas_width = table_width + 80  # Add some padding
    # canvas_height = table_height + 80  # Add some padding

    # # Set initial Y position
    # y_position = canvas_height

    # # Ensure table is drawn entirely on the page
    # while y_position >= 40:
    #     table.wrapOn(pdf, canvas_width, canvas_height)
    #     table.drawOn(pdf, 40, y_position - table_height)
    #     pdf.showPage()  # Start a new page
    #     y_position -= canvas_height  # Update Y position for the next page

    # pdf.save()
    # return response
    
    # Calculate table width
    column_widths = [pdf.stringWidth(header, "Helvetica", 10) for header in headers]
    table_width = sum(column_widths) + len(headers) * 2  # Add padding

    # Calculate available space on the page
    available_space = 750  # Assuming page height is 750
    
    # Ensure table is drawn entirely on the page
    table.wrapOn(pdf, table_width, available_space)

    # Calculate required height for the table
    table_height = table._height

    # Draw table starting from the top of the page
    table.drawOn(pdf, 40, available_space - table_height)

    pdf.save()
    return response


download_pdf.short_description = "Download Selected Items as PDF"


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'description', 'price','stock', 'category', 'images', 'created_date', 'modified_date', 'is_available','get_total_orders')
    prepopulated_fields={'slug':('product_name',)}
    inlines = [ProductGalleryInline]
    actions =[download_pdf , download_excel]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(total_orders=Count('orderproduct'))
        return queryset

    def get_total_orders(self, obj):
        return obj.total_orders

    get_total_orders.short_description = 'Total Orders'


# Register your models here.
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value','is_active')
    list_editable =('is_active',)
    list_filter= ('product', 'variation_category', 'variation_value')
    actions =[download_pdf, download_excel]
admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery) 


