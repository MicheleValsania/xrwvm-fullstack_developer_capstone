from django.contrib import admin
from .models import CarMake, CarModel

# Register your models here.
# CarModelInline class

class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 3

# CarModelAdmin class

class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'make', 'dealer_id', 'car_type', 'year')
    list_filter = ('make', 'car_type', 'year')
    search_fields = ('name', 'make__name')

# CarMakeAdmin class with CarModelInline

class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    inlines = [CarModelInline]
    search_fields = ('name',)


admin.site.register(CarModel, CarModelAdmin)
admin.site.register(CarMake, CarMakeAdmin)