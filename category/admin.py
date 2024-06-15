from django.contrib import admin
from django.db.models import Count
from .models import Category
from orders.models import OrderProduct

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
    headers = ['ID', 'Category Name', 'Description', 'Total Orders']  # Define headers
    data = [headers]

    # Determine column widths based on content length
    column_widths = [len(header) for header in headers]

    for obj in ordered_queryset:
        category_id = obj.id
        category_name = obj.category_name
        description = obj.description
        total_orders = OrderProduct.objects.filter(product__category=obj).count()
        data_row = [str(category_id), category_name, description, str(total_orders)]  # Include data
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

def download_pdf(model_admin, request, queryset):
    model_name = model_admin.model.__name__
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={model_name}.pdf'
    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle('PDF Report')
    ordered_queryset = queryset.order_by('id')
    
    
    # headers = [field.verbose_name for field in model_admin.model._meta.fields ]
    # data =[headers]

    headers = ['ID', 'Category Name', 'Description', 'Total Orders']  # Define headers
    data = [headers]


    for obj in ordered_queryset:
        category_id = obj.id
        category_name = obj.category_name
        description = obj.description
        total_orders = OrderProduct.objects.filter(product__category=obj).count()
        data_row = [str(category_id), category_name, description, str(total_orders)]  # Include data
        data.append(data_row)
        # data_row = [str(getattr(obj,field.name)) for field in model_admin.model._meta.fields ]
        # data.append(data_row)

    table = Table(data)
    table.setStyle(TableStyle(
        [
         ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
         ('GRID', (0, 0), (-1, -1), 1, colors.black)   
        ]
    ))

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

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug', 'total_orders')
    actions = [download_pdf, download_excel]

    def total_orders(self, obj):
        # Calculate the total number of orders for this category
        return OrderProduct.objects.filter(product__category=obj).count()

    total_orders.short_description = 'Total Orders'

admin.site.register(Category, CategoryAdmin)
