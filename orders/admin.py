from django.contrib import admin
from .models import Payment,Order,OrderProduct

#to view another model in the current model page
class OrderProduct1(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment','user','product','quantity','product_price','ordered')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','full_name','phone','email','status','city','order_total']
    list_filter = ['status','is_ordered']
    search_fields = ['order_number','first_name','last_name','phone','email']
    list_per_page = 10
    inlines = [OrderProduct1]
 

admin.site.register(Order,OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)



# Register your models here.
