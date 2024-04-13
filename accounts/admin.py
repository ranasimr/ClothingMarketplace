from django.contrib import admin
from django.http import HttpResponse
from .models import Account ,UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors



def download_pdf(self,request,queryset):
    model_name =self.model.__name__
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={model_name}.pdf'
    pdf =canvas.Canvas(response, pagesize=letter)
    pdf.setTitle('PDF Report')
    ordered_queryset = queryset.filter(is_superadmin=False).order_by('id')
    excluded_fields = ['password', 'date_joined', 'last_login', 'is_superadmin', 'is_active', 'is_staff', 'is_admin']
    
    headers = [field.verbose_name for field in self.model._meta.fields if field.name not in excluded_fields]
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

    pdf.save()
    return response
download_pdf.short_description = "Download Selected Items as PDF"

class AcoountAdmin(UserAdmin):
    list_display = ('email','first_name','last_name','username','last_login','date_joined','is_active')
    list_display_links =('email','first_name','last_name')
    readonly_fields=('last_login','date_joined')
    ordering= ('-date_joined',)
    filter_horizontal = ()
    list_filter =()
    fieldsets=()
    actions =[download_pdf]
from django.templatetags.static import static

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.profile_picture:  # Check if profile_picture exists
            return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(obj.profile_picture.url))
        else:
            default_image_url = static('images/dp.jpg')
            return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(default_image_url))

    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')
    actions =[download_pdf]

admin.site.register(Account, AcoountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)



