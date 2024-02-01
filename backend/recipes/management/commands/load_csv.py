import csv
import os

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag

CSV_ITEMS = {
    'ingredients': {
        'file': 'ingredients.csv',
        'model': Ingredient,
        'fields': ('name', 'measurement_unit')
    },
    'tags': {
        'file': 'tags.csv',
        'model': Tag,
        'fields': ('name', 'color', 'slug')
    },
}


class Command(BaseCommand):
    """Загрузка ингредиентов из CSV."""

    help = 'Загрузка ингредиентов и тегов из CSV файла.'

    def handle(self, *args, **kwargs):
        """Загружает ингредиенты и теги из CSV файла."""
        for model_name, model_info in CSV_ITEMS.items():
            csv_file_path = os.path.join(
                settings.BASE_DIR,
                'data', model_info['file'],
            )
            try:
                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    items_to_create = [
                        model_info['model'](
                            **dict(zip(model_info['fields'], row))
                        )
                        for row in reader
                    ]
                    model_info['model'].objects.bulk_create(items_to_create)
                    self.stdout.write(self.style.SUCCESS(
                        f'Загрузка всех {model_name} выполнена.'
                    ))
            except FileNotFoundError as e:
                self.stdout.write(self.style.ERROR(
                    f'Файл {csv_file_path} не найден. Проверьте путь к файлу. '
                    f'Ошибка: {str(e)}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Произошла ошибка: {str(e)}'
                ))
