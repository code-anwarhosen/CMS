from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Product, Contract, Payment, Guarantor, Account


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'phone', 'age', 'occupation', 'avatar_preview')
    list_filter = ('occupation', )
    search_fields = ('name', 'phone', 'address')
    readonly_fields = ('uid', 'avatar_preview')
    fieldsets = (
        ('Creator', {
            'fields': ('creator',)
        }),
        ('Personal Information', {
            'fields': ('uid', 'name', 'age', 'phone', 'occupation')
        }),
        ('Guardian Information', {
            'fields': ('guardianType', 'guardianName')
        }),
        ('Address Information', {
            'fields': ('address', 'locationMark')
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



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('model', 'category')
    list_filter = ('model', 'category')
    search_fields = ('model', 'category')


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('account', 'cashValue', 'hireValue', 'downPayment', 'monthlyPayment', 'length', 'cashBalance', 'hireBalance')
    readonly_fields = ('uid', 'cashBalance', 'hireBalance', 'totalPaid')
    fieldsets = (
        ('Contract Details', {
            'fields': ('uid', 'cashValue', 'hireValue', 'downPayment', 'monthlyPayment', 'length')
        }),
        ('Balances', {
            'fields': ('totalPaid', 'cashBalance', 'hireBalance')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'date', 'receiptId', 'amount')
    list_filter = ('date', 'contract')
    search_fields = ('receiptId', 'contract__id')


@admin.register(Guarantor)
class GuarantorAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'phone', 'occupation')
    search_fields = ('name', 'phone')
    readonly_fields = ('uid',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('accountNumber', 'customer', 'product', 'contract', 'isActive', 'saleDate')
    list_filter = ('isActive', 'saleDate')

    search_fields = ('accountNumber', 'customer__name')
    filter_horizontal = ('guarantors',)
    
    fieldsets = (
        ('Account Information', {
            'fields': ('creator', 'accountNumber', 'customer', 'product', 'contract', 'isActive')
        }),
        ('Guarantors', {
            'fields': ('guarantors',)
        }),
        ('Additional Information', {
            'fields': ('saleDate', 'remarks')
        }),
    )
