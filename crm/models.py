from datetime import datetime

from django.core.files.storage import default_storage
from django.db import models


class Line(models.Model):
    class Meta:
        ordering = ['length', 'diameter']
        constraints = [
            models.UniqueConstraint(fields=['length', 'diameter'], name='line_const')
        ]

    name = models.CharField(max_length=200, null=True, blank=True)
    length = models.IntegerField(help_text="line length in Meters")
    diameter = models.FloatField(help_text="line diameter in Millimeters")

    def __str__(self):
        return "{}-{}".format(str(self.diameter), str(self.length))


class ReelManufacturer(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=200, null=False, unique=True)

    def __str__(self):
        return self.name


class ReelModel(models.Model):
    class Meta:
        ordering = ['reel_manufacturer', 'name']
        constraints = [
            models.UniqueConstraint(fields=['reel_manufacturer', 'name'], name='reel_model_const')
        ]

    reel_manufacturer = models.ForeignKey(ReelManufacturer, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return "{} {}".format(self.reel_manufacturer, self.name)


class SpoolModel(models.Model):
    class Meta:
        ordering = ['reel_model', 'name', 'modified']
        constraints = [
            models.UniqueConstraint(fields=['reel_model', 'name'], name='spool_model_const')
        ]

    reel_model = models.ForeignKey(ReelModel, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=200, null=True, blank=True, unique=False, default="")
    size = models.IntegerField(default=None, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.reel_model, self.name or "")


class SpoolDimension(models.Model):
    actual = models.BooleanField(default=False)
    spool_model = models.ForeignKey(SpoolModel, on_delete=models.CASCADE, default=1)
    D1 = models.FloatField(default=1.0, help_text="Spool D1", null=False)
    D2 = models.FloatField(default=1.0, help_text="Spool D2", null=False)
    H1 = models.FloatField(default=1.0, help_text="Spool H1", null=False)
    description = models.CharField(max_length=200, null=True, blank=True, unique=False, default="")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.actual:
            # select all other active items
            qs = type(self).objects.filter(actual=True)
            # except self (if self already exists)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            # and deactive them
            qs.update(actual=False)
        super().save(force_insert, force_update, using, update_fields)


class SpoolModelImage(models.Model):
    spool_model = models.ForeignKey(SpoolModel, on_delete=models.CASCADE, default=1)
    img_height = models.PositiveIntegerField(default=100)
    img_width = models.PositiveIntegerField(default=100)
    image = models.ImageField(storage=default_storage, upload_to="spool_images", null=True, blank=True,
                              height_field='img_height', width_field='img_width')

    def __str__(self):
        return ""


class ReducerModel(models.Model):
    spool_model = models.ForeignKey(SpoolModel, on_delete=models.CASCADE, null=False, default=1)
    line = models.ForeignKey(Line, default=1, on_delete=models.CASCADE, null=False)
    description = models.TextField(null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['spool_model', 'modified']
        constraints = [
            models.UniqueConstraint(fields=['spool_model', 'line'], name='reducer_model_const')
        ]

    def __str__(self):
        return "{} {}".format(self.spool_model, self.line)


class ReducerDimension(models.Model):
    actual = models.BooleanField(default=False)
    reducer_model = models.ForeignKey(ReducerModel, on_delete=models.CASCADE, default=1)
    D3 = models.FloatField(default=1.0, help_text="Spool D3", null=False)
    D4 = models.FloatField(default=1.0, help_text="Spool D4", null=False)
    H2 = models.FloatField(default=1.0, help_text="Spool H2", null=False)
    description = models.CharField(max_length=200, null=True, blank=True, unique=False, default="")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.actual:
            # select all other active items
            qs = type(self).objects.filter(actual=True)
            # except self (if self already exists)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            # and deactive them
            qs.update(actual=False)
        super().save(force_insert, force_update, using, update_fields)


class ReducerModelImage(models.Model):
    reducer_model = models.ForeignKey(ReducerModel, on_delete=models.CASCADE, default=1)
    img_height = models.PositiveIntegerField(default=100)
    img_width = models.PositiveIntegerField(default=100)
    image = models.ImageField(storage=default_storage, upload_to="reducer_images", null=True, blank=True,
                              height_field='img_height', width_field='img_width')

    def __str__(self):
        return ""


class Price(models.Model):
    class Meta:
        ordering = ['currency', 'price']
        constraints = [
            models.UniqueConstraint(fields=['currency', 'price'], name='price_const')
        ]

    class Currency(models.TextChoices):
        UAH = "UAH"
        USD = "USD"
        EUR = "ERU"

    currency = models.CharField(max_length=3, default=Currency.UAH, choices=Currency.choices)
    price = models.IntegerField(default=100)

    def __str__(self):
        return "{} {}".format(str(self.price), self.currency)


def group_name():
    return "OrderGroup-{}".format(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))


class OrderGroup(models.Model):
    class Meta:
        ordering = ['created', 'name']
    name = models.CharField(max_length=200, null=False, unique=True, default=group_name)
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    payed_sum = models.IntegerField(default=0)

    # def get_orders(self):
    #     return Order.objects.filter(order_group_id=self.name) or []
    #
    # def get_sum(self):
    #     return sum([x.price.price * x.amount for x in self.get_orders()])
    #
    def __str__(self):
        return self.name


def order_name():
    return "Order-{}".format(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))


class OrderBucket(models.Model):
    class Meta:
        ordering = ['created', 'name']

    name = models.CharField(max_length=200, null=False, unique=True, default=order_name)
    order_group = models.ForeignKey(OrderGroup, on_delete=models.CASCADE, default=1)
    payed = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name

    def get_order_items(self):
        return OrderItem.objects.filter(order_id=self.pk)

    def get_order_sum(self):
        return sum([item.get_item_sum() for item in self.get_order_items()])


class OrderItem(models.Model):
    order = models.ForeignKey(OrderBucket, on_delete=models.CASCADE, default=1)
    reducer_model = models.ForeignKey(ReducerModel, on_delete=models.CASCADE, null=False, default=1)
    price = models.ForeignKey(Price, on_delete=models.CASCADE, null=False, default=1)
    amount = models.IntegerField(default=2)
    printed = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True, )

    def __str__(self):
        return "{} - {}x{}".format(self.reducer_model, self.amount, self.price)

    def get_item_sum(self):
        return self.price.price * self.amount
