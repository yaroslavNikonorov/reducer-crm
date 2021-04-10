from datetime import datetime

from django.core.files.storage import default_storage
from django.db import models


class Line(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    length = models.IntegerField(help_text="line length in Meters")
    diameter = models.FloatField(help_text="line diameter in Millimeters")

    def __str__(self):
        return "{}-{}".format(str(self.diameter), str(self.length))


class Manufacturer(models.Model):
    name = models.CharField(max_length=200, null=False, primary_key=True, unique=True)

    def get_related_ent(self):
        return Model

    def __str__(self):
        return self.name


class Model(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=False, primary_key=True, unique=True)

    def get_related_ent(self):
        return SpoolModel

    def __str__(self):
        return "{} {}".format(self.manufacturer, self.name)


class SpoolModel(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True, unique=False, default="")
    size = models.IntegerField(default=10000, null=True, blank=True)
    D1 = models.FloatField(default=1.0, help_text="Spool D1")
    D2 = models.FloatField()
    H1 = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True, blank=True)

    def get_related_ent(self):
        return ReducerModel

    def __str__(self):
        return "{} {}".format(self.model, str(self.size))


class SpoolModelImage(models.Model):
    spool_model = models.ForeignKey(SpoolModel, on_delete=models.CASCADE)
    img_height = models.PositiveIntegerField(default=100)
    img_width = models.PositiveIntegerField(default=100)
    image = models.ImageField(storage=default_storage, upload_to="spool_images", null=True, blank=True,
                              height_field='img_height', width_field='img_width')

    def __str__(self):
        return ""


class ReducerModel(models.Model):
    spool_model = models.ForeignKey(SpoolModel, on_delete=models.CASCADE, null=False)
    line = models.ForeignKey(Line, default=1, on_delete=models.CASCADE, null=False)
    D3 = models.FloatField()
    D4 = models.FloatField()
    H2 = models.FloatField()
    description = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['spool_model', 'line'], name='spool_line_const')
        ]

    def __str__(self):
        return "{} {}".format(self.spool_model, self.line)


class ReducerModelImage(models.Model):
    reducer_model = models.ForeignKey(ReducerModel, on_delete=models.CASCADE)
    img_height = models.PositiveIntegerField(default=100)
    img_width = models.PositiveIntegerField(default=100)
    image = models.ImageField(storage=default_storage, upload_to="reducer_images", null=True, blank=True,
                              height_field='img_height', width_field='img_width')

    def __str__(self):
        return ""


class Price(models.Model):
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
    id = models.AutoField(primary_key=True)
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


class Order(models.Model):
    id = models.AutoField(primary_key=True)
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
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=1)
    reducer_model = models.ForeignKey(ReducerModel, on_delete=models.CASCADE, null=False)
    price = models.ForeignKey(Price, on_delete=models.CASCADE, null=False)
    amount = models.IntegerField(default=2)
    printed = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True, )

    def __str__(self):
        return "{} - {}x{}".format(self.reducer_model, self.amount, self.price)

    def get_item_sum(self):
        return self.price.price * self.amount
