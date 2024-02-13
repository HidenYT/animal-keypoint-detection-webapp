from django.core.management.base import BaseCommand
import random

from model_training.models import NeuralNetworkType

# python manage.py seed --mode=refresh

""" Clear all data and creates addresses """
MODE_REFRESH = 'refresh'

""" Clear all data and do not create any object """
MODE_CLEAR = 'clear'

class Command(BaseCommand):
    help = "seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        run_seed(options['mode'])
        self.stdout.write('done.')


def clear_data():
    """Deletes all the table data"""
    NeuralNetworkType.objects.all().delete()


def create_neural_network_types():
    names = ["DeepLabCut", "SLEAP", "DeepPoseKit", "AlphaTracker"]
    for name in names:
        nn = NeuralNetworkType()
        nn.name = name
        nn.save()

def run_seed(mode):
    """ Seed database based on mode

    :param mode: refresh / clear 
    :return:
    """
    # Clear data from tables
    clear_data()
    if mode == MODE_CLEAR:
        return
    
    create_neural_network_types()
