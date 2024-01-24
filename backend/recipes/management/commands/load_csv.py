import csv
import os

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Загрузка ингредиентов из CSV."""

    def handle(self, *args, **kwargs):
        csv_file_path = os.path.join(
            settings.BASE_DIR, 'data', 'ingredients.csv'
        )
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                ingredients_to_create = [
                    Ingredient(name=row[0], measurement_unit=row[1])
                    for row in reader
                ]
                Ingredient.objects.bulk_create(ingredients_to_create)
            self.stdout.write(self.style.SUCCESS(
                'Загрузка всех ингредиентов выполнена.'
            ))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'Файл {csv_file_path} не найден. Проверьте путь к файлу.'
            ))
        except Exception:
            self.stdout.write(self.style.ERROR(
                f'Произошла ошибка: {str(Exception)}'
            ))
