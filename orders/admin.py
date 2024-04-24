from django.contrib import admin
from .models import Payment, Order, OrderProduct
from reportlab.lib.units import inch


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from django.http import HttpResponse



def download_pdf(self,request,queryset):
    model_name =self.model.__name__
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={model_name}.pdf'
    pdf =canvas.Canvas(response, pagesize=letter)
    pdf.setTitle('PDF Report')
    ordered_queryset = queryset.order_by('id')
    excluded_fields = ['payment','user']

    headers = [field.verbose_name for field in self.model._meta.fields if field.name not in excluded_fields ]
    data =[headers]

    

    for obj in ordered_queryset:
        data_row = [str(getattr(obj,field.name)) for field in self.model._meta.fields if field.name not in excluded_fields]
        data.append(data_row)

    table= Table(data)
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

    # column_widths = [pdf.stringWidth(header, "Helvetica", 10) + 2 * inch for header in headers]
    # table_width = sum(column_widths)

    # # Calculate available space on the page
    # available_space = 750  # Assuming page height is 750

    # # Ensure table is drawn entirely on the page
    # table.wrapOn(pdf, table_width, available_space)

    # # Calculate required height for the table
    # table_height = table._height

    # # Draw table starting from the top of the page
    # table.drawOn(pdf, 40, available_space - table_height)

    pdf.save()
    return response

download_pdf.short_description = "Download Selected Items as PDF"


class OrderProductInline(admin.TabularInline):
    model= OrderProduct
    readonly_fields=('payment','user','product','quantity','product_price','ordered')
    extra=0
    
    

class OrderAdmin(admin.ModelAdmin):
    list_display=['order_number','full_name','phone','email','city','order_total','tax','status','is_ordered','created_at']
    list_filter=['status','is_ordered']
    search_fields=['order_number','first_name','last_name','phone','email']
    list_per_page=20
    inlines=[OrderProductInline]
    actions =[download_pdf]


admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)

# Register your models here.
