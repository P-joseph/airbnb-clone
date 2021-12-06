from django.core.management.base import BaseCommand
from rooms import models as room_models


class Command(BaseCommand):

    help = "This command creates amenities"

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         "--times", help="How many times do you want me to tell you that I love you?"
    #     )

    def handle(self, *args, **options):
        amenities = [
            "Toiletries",
            "Personal_care",
            "Coffee_Kit",
            "Free_parking",
            "Premium_coffee",
            "Free_WiFi",
            "Free_breakfast",
            "Bathrobes_and_slippers",
            "Tissue_box",
        ]
        for a in amenities:
            room_model.Amenity.objects.create(name=a)
        self.stdout.write(self.style.SUCCESS("Amenities created!"))