from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

ROLES = ('Administrador', 'Mesero', 'Cajero')


class Command(BaseCommand):
    help = 'Crea los grupos del sistema: Administrador, Mesero y Cajero.'

    def handle(self, *args, **options):
        for nombre in ROLES:
            grupo, creado = Group.objects.get_or_create(name=nombre)
            if creado:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{nombre}" creado.'))
            else:
                self.stdout.write(f'Grupo "{nombre}" ya existía.')

        self.stdout.write(self.style.SUCCESS('Listo. Grupos del sistema verificados.'))
