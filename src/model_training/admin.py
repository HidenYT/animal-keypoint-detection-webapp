from django.contrib import admin
from .models import SLEAPNeuralNetwork, DLCNeuralNetwork


admin.site.register(SLEAPNeuralNetwork)
admin.site.register(DLCNeuralNetwork)