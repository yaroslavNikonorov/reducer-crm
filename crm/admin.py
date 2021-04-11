import re

from django.contrib import admin
from django.forms import ModelForm
from django.urls import reverse
from django.utils.html import format_html_join, format_html
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from crm.models import Order, SpoolModel, Line, Price, Manufacturer, Model, ReducerModel, OrderGroup, SpoolModelImage, \
    ReducerModelImage, OrderItem, SpoolDimension, ReducerDimension


def get_admin_url(instance):
    return reverse('admin:{0}_{1}_change'.format(instance._meta.app_label, instance._meta.model_name),
                   args=(instance.pk,))
    # return instance.get_absolute_url()


def format_list(inst_list):
    return format_html_join(
        mark_safe('<br>'),
        '<a href={}>{}</a>',
        ((get_admin_url(inst), str(inst)) for inst in inst_list),
    ) or mark_safe("<span class='errors'>Empty</span>")


def camel_to_snake(string):
    groups = re.findall('([A-z0-9][a-z]*)', string)
    return '_'.join([i.lower() for i in groups])


@admin.register(OrderItem, Line, Price)
class CrmAdmin(admin.ModelAdmin):
    pass


@admin.register(Manufacturer, Model)
class RelationList(admin.ModelAdmin):
    readonly_fields = ['relation_list']

    # fieldsets = [
    #     (None, {'fields': ['']}),
    #     ('Relations', {'fields': ['relation_list']}),
    # ]

    def relation_list(self, instance):
        class_name = camel_to_snake(instance.__class__.__name__)
        filter_key = class_name + "_id"
        filter_dict = {filter_key: instance.pk}
        models = instance.get_related_ent().objects.filter(**filter_dict)
        return format_list(models)

    relation_list.short_description = "Related Entities"


class SpoolModelImageInline(admin.TabularInline):
    model = SpoolModelImage
    # fieldsets = [
    #     (None, {'fields': ['']}),
    #     ('Relations', {'fields': ['relation_list']}),
    # ]
    fields = ['image_preview', 'image']
    readonly_fields = ('image_preview',)
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    @staticmethod
    def _scale_width(width, height, scale_height=100):
        return (scale_height * width) / height

    def image_preview(self, instance):
        if instance.image:
            return mark_safe(
                '<a href={url}><img src="{url}" width="{width}" height="100" /></a>'.format(url=instance.image.url,
                                                                                            width=self._scale_width(
                                                                                                instance.img_width,
                                                                                                instance.img_height)))
        else:
            return '(No image)'

    image_preview.short_description = "Image"


class SpoolModelDimInline(admin.TabularInline):
    extra = 0
    model = SpoolDimension
    # verbose_name = ''
    # verbose_name_plural = ''
    # max_num = 1
    # list_display = ['__str__']
    # fields = ['name', 'line', 'D3', 'D4', 'H2']
    # readonly_fields = ['name', 'line', 'D3', 'D4', 'H2']

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
    #
    # def name(self, inst):
    #     return mark_safe('<a href="{url}">{name}</a>'.format(url=get_admin_url(inst), name=str(inst)))


class SpoolModelReducerInline(admin.TabularInline):
    extra = 0
    model = ReducerModel
    verbose_name = ''
    # verbose_name_plural = ''
    # max_num = 1
    # list_display = ['__str__']
    fields = ['name']
    # fields = ['name', 'line', 'D3', 'D4', 'H2']
    # readonly_fields = ['name', 'line', 'D3', 'D4', 'H2']
    readonly_fields = ['name']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def name(self, inst):
        return mark_safe('<a href="{url}">{name}</a>'.format(url=get_admin_url(inst), name=str(inst)))


@admin.register(SpoolModel)
class SpoolModelAdmin(VersionAdmin):
    inlines = [SpoolModelDimInline, SpoolModelReducerInline, SpoolModelImageInline]
    fieldsets = [
        ("SpoolModel", {'fields': ['model', 'name', 'size']}),
        # ("Dimensions", {'fields': ['D1', 'D2', 'H1']}),
        # ('Relations', {'fields': ['relation_list']}),
    ]


class ReducerModelImageInline(admin.TabularInline):
    model = ReducerModelImage
    # fieldsets = [
    #     (None, {'fields': ['']}),
    #     ('Relations', {'fields': ['relation_list']}),
    # ]
    fields = ['image_preview', 'image']
    readonly_fields = ('image_preview',)
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    @staticmethod
    def _scale_width(width, height, scale_height=100):
        return (scale_height * width) / height

    def image_preview(self, instance):
        if instance.image:
            return mark_safe(
                '<a href={url}><img src="{url}" width="{width}" height="100" /></a>'.format(url=instance.image.url,
                                                                                            width=self._scale_width(
                                                                                                instance.img_width,
                                                                                                instance.img_height)))
        else:
            return '(No image)'

    image_preview.short_description = "Image"


class ReducerModelDimInline(admin.TabularInline):
    extra = 0
    model = ReducerDimension


@admin.register(ReducerModel)
class ReducerModelAdmin(VersionAdmin):
    inlines = [ReducerModelDimInline, ReducerModelImageInline]
    # fields = ['spool_d1']
    readonly_fields = ("spool_name", "spool_d1", "spool_d2", "spool_h1",'reducer_d3', 'reducer_d4', 'reducer_h2')
    fieldsets = [
        ("SpoolModel", {'fields': [("spool_model", "spool_name")]}),
        ("Line", {"fields": ["line"]}),
        # ("Reducer Dimensions", {'fields': ['spool_d1', 'spool_d2', 'D3', 'D4', 'spool_h1', 'H2']}),
        ("Reducer Dimensions", {'fields': ['spool_d1', 'spool_d2', 'reducer_d3', 'reducer_d4', 'spool_h1', 'reducer_h2']}),
        # ('Relations', {'fields': ['relation_list']}),
    ]

    def spool_name(self, instance):
        return mark_safe('<a href="{url}">{name}</a>'.format(url=get_admin_url(instance.spool_model),
                                                             name=str(instance.spool_model)))

    spool_name.short_description = "Go to"

    def _get_spool_dim(self, instance):
        return SpoolDimension.objects.filter(spool_model_id=instance.spool_model.pk, actual=True).first()

    def _get_reducer_dim(self, instance):
        return ReducerDimension.objects.filter(reducer_model_id=instance.pk, actual=True).first()

    def spool_d1(self, instance):
        spool_dim = self._get_spool_dim(instance)
        return spool_dim.D1 if spool_dim else None

    spool_d1.short_description = "D1"

    def spool_d2(self, instance):
        spool_dim = self._get_spool_dim(instance)
        return spool_dim.D2 if spool_dim else None

    spool_d2.short_description = "D2"

    def spool_h1(self, instance):
        spool_dim = self._get_spool_dim(instance)
        return spool_dim.H1 if spool_dim else None
    spool_h1.short_description = "H1"

    def reducer_d3(self, instance):
        reducer_dim = self._get_reducer_dim(instance)
        return reducer_dim.D3 if reducer_dim else None

    reducer_d3.short_description = "D3"

    def reducer_d4(self, instance):
        reducer_dim = self._get_reducer_dim(instance)
        return reducer_dim.D4 if reducer_dim else None

    reducer_d4.short_description = "D4"

    def reducer_h2(self, instance):
        reducer_dim = self._get_reducer_dim(instance)
        return reducer_dim.H2 if reducer_dim else None
    reducer_h2.short_description = "H2"



class MarkNewInstancesAsChangedModelForm(ModelForm):
    def has_changed(self):
        """Returns True for new instances, calls super() for ones that exist in db.
        Prevents forms with defaults being recognized as empty/unchanged."""
        return not self.instance.pk or super().has_changed()


class OrderGroupNotSentInline(admin.TabularInline):
    extra = 0
    model = Order
    form = MarkNewInstancesAsChangedModelForm
    fields = ['name']
    # readonly_fields = ['order_url', ]
    show_change_link = True
    verbose_name = "Orders"
    verbose_name_plural = "Orders not sent"

    # def order_url(self, inst):
    #     return mark_safe('<a href="{url}">{name}</a>'.format(url=get_admin_url(inst), name=str(inst)))

    def get_queryset(self, request):
        qs = super(OrderGroupNotSentInline, self).get_queryset(request)
        return qs.filter(sent=False)


class OrderGroupSentInline(admin.TabularInline):
    extra = 0
    model = Order
    # form = MarkNewInstancesAsChangedModelForm
    fields = ['order_url']
    readonly_fields = ['order_url', ]
    # show_change_link = True
    verbose_name = "Orders"
    verbose_name_plural = "Orders sent"

    def order_url(self, inst):
        return mark_safe('<a href="{url}">{name}</a>'.format(url=get_admin_url(inst), name=str(inst)))

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(OrderGroupSentInline, self).get_queryset(request)
        return qs.filter(sent=True)


@admin.register(OrderGroup)
class OrderGroupAdmin(VersionAdmin):
    # fields = ["name", "orders_list"]
    readonly_fields = ['get_sum']
    inlines = [OrderGroupNotSentInline, OrderGroupSentInline]

    # def orders_list(self, instance):
    #     orders = Order.objects.filter(order_group_id=instance.pk) or []
    #     return format_list(orders)

    # orders_list.short_description = "Related Orders"

    def get_sum(self, instance):
        orders = Order.objects.filter(order_group_id=instance.pk)
        return format_html("{}", sum(map(lambda o: o.get_order_sum(), orders))) or mark_safe(
            "<span class='errors'>No orders.</span>")

    get_sum.short_description = "Total"


class OrderInline(admin.TabularInline):
    extra = 0
    model = OrderItem
    # verbose_name = ''
    # verbose_name_plural = ''
    # max_num = 1
    # list_display = ['__str__']
    # fields = ['name', 'line', 'D3', 'D4', 'H2']
    # readonly_fields = ['name', 'line', 'D3', 'D4', 'H2']

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
    #
    # def name(self, inst):
    #     return mark_safe('<a href="{url}">{name}</a>'.format(url=get_admin_url(inst), name=str(inst)))


@admin.register(Order)
class OrderAdmin(VersionAdmin):
    readonly_fields = ['order_group_url']
    inlines = [OrderInline]

    # def orders_list(self, instance):
    #     return format_list(instance.get_orders())
    #
    # orders_list.short_description = "Related Orders"
    #
    # def show_sum(self, instance):
    #     return format_html("{}", instance.get_sum()) or mark_safe(
    #         "<span class='errors'>No orders.</span>")
    #
    # show_sum.short_description = "SUM"

    def order_group_url(self, inst):
        return mark_safe(
            '<a href="{url}">{name}</a>'.format(url=get_admin_url(inst.order_group), name=str(inst.order_group)))

    order_group_url.short_description = "Order Group URL"
