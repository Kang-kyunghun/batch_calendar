from django.db import models

class Batch(models.Model):
    name       = models.CharField(max_length=50)
    start_date = models.DateField(null=True)

    class Meta:
        db_table = 'batches'

    def __str__(self):
        return self.name

class Calendar(models.Model):
    name = models.CharField(max_length = 200)
    batch = models.ForeignKey(Batch, on_delete = models.CASCADE)

    class Meta:
        db_table = 'calendars'

    def __str__(self):
        return self.name
