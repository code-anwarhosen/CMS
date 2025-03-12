from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Model, Product, Contract, Payment, Guarantor, Account


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'phone', 'gender', 'age', 'occupation', 'avatar_preview')
    list_filter = ('gender', 'occupation')
    search_fields = ('name', 'phone', 'address')
    readonly_fields = ('uid', 'avatar_preview')
    fieldsets = (
        ('Personal Information', {
            'fields': ('uid', 'name', 'age', 'gender', 'phone', 'occupation')
        }),
        ('Guardian Information', {
            'fields': ('guardianType', 'guardianName')
        }),
        ('Address Information', {
            'fields': ('address', 'location_mark')
        }),
        ('Avatar', {
            'fields': ('avatar', 'avatar_preview')
        }),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" />', obj.avatar.url)
        return "No Avatar"
    avatar_preview.short_description = 'Avatar Preview'


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('uid', 'category', 'model')
    list_filter = ('category', 'model')
    search_fields = ('category', 'model__name')
    readonly_fields = ('uid',)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'cashValue', 'hireValue', 'downPayment', 'monthlyPayment', 'length', 'cashBalance', 'hireBalance')
    readonly_fields = ('cashBalance', 'hireBalance')
    fieldsets = (
        ('Contract Details', {
            'fields': ('cashValue', 'hireValue', 'downPayment', 'monthlyPayment', 'length')
        }),
        ('Balances', {
            'fields': ('cashBalance', 'hireBalance')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract', 'date', 'receiptId', 'amount')
    list_filter = ('date', 'contract')
    search_fields = ('receiptId', 'contract__id')


@admin.register(Guarantor)
class GuarantorAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'phone', 'occupation')
    search_fields = ('name', 'phone')
    readonly_fields = ('uid',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer', 'product', 'contract', 'status', 'saleDate')
    list_filter = ('status', 'saleDate')
    search_fields = ('number', 'customer__name', 'product__category')
    filter_horizontal = ('guarantors',)
    readonly_fields = ('number', 'saleDate')
    fieldsets = (
        ('Account Information', {
            'fields': ('number', 'user', 'customer', 'product', 'contract', 'status')
        }),
        ('Guarantors', {
            'fields': ('guarantors',)
        }),
        ('Sale Information', {
            'fields': ('saleDate',)
        }),
    )