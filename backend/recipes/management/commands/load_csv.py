import csv
import os

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Загрузка ингредиентов из CSV."""

    help = 'Загрузка ингредиентов и тегов из CSV файла.'

    def handle(self, *args, **kwargs):
        csv_files = {
            'ingredients': 'ingredients.csv',
            'tags': 'tags.csv',
        }

        for model_name, csv_file_name in csv_files.items():
            csv_file_path = os.path.join(
                settings.BASE_DIR,
                'data',
                csv_file_name
            )

            try:
                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)

                    if model_name == 'ingredients':
                        items_to_create = [
                            Ingredient(name=name, measurement_unit=unit)
                            for name, unit in reader
                        ]
                        model_class = Ingredient
                    elif model_name == 'tags':
                        items_to_create = [
                            Tag(name=name, color=color, slug=slug)
                            for name, color, slug in reader
                        ]
                        model_class = Tag
                    else:
                        continue

                    model_class.objects.bulk_create(items_to_create)
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
