from django.db import models


class MetroStation(models.Model):
    station_id = models.IntegerField()
    station_name = models.CharField(max_length=20)
    timestamp = models.DateTimeField()
    outflow = models.IntegerField()
    outflow_pred = models.IntegerField()
    inflow = models.IntegerField()

    def __str__(self):
        return f'[{self.timestamp}] {self.station_id}: {self.station_name}, inflow {self.inflow},  outflow {self.outflow}, outflow_pred {self.outflow_pred}'


class Road(models.Model):
    task = models.CharField(max_length=10)
    algo = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    color = models.CharField(max_length=20)
    shape = models.TextField()

    def __str__(self):
        return f'task: {self.task}; algo: {self.algo}; timestamp: {self.timestamp}'


class RoadYX(models.Model):
    task = models.CharField(max_length=10)
    algo = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    color = models.CharField(max_length=20)
    shape = models.TextField()

    def __str__(self):
        return f'task: {self.task}; algo: {self.algo}; timestamp: {self.timestamp}'
