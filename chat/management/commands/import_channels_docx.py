from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from unidecode import unidecode
from docx import Document

from chat.models import Channel, ChannelMember

User = get_user_model()

def slug_username(fullname: str) -> str:
    """
    Genera un username único a partir del nombre completo.
    - quita tildes (Unidecode)
    - slugify
    - si existe, agrega sufijos -2, -3...
    """
    base = slugify(unidecode(fullname)).replace("-", "_")  # prefiero _ para legibilidad
    if not base:
        base = "usuario"
    username = base
    n = 2
    while User.objects.filter(username=username).exists():
        username = f"{base}_{n}"
        n += 1
    return username

class Command(BaseCommand):
    help = "Importa canales y usuarios desde un .docx donde cada bloque es: nombre-de-canal y debajo sus miembros, separado por líneas en blanco."

    def add_arguments(self, parser):
        parser.add_argument("docx_path", type=str, help="Ruta al archivo .docx")
        parser.add_argument(
            "--default-password",
            dest="default_password",
            default="GoVision123!",
            help="Password por defecto para nuevos usuarios creados.",
        )
        parser.add_argument(
            "--creator-username",
            dest="creator_username",
            default=None,
            help="Opcional: username del creador de los canales (si no, usa el primer superuser).",
        )

    def handle(self, *args, **opts):
        path = opts["docx_path"]
        default_password = opts["default_password"]
        creator_username = opts["creator_username"]

        try:
            doc = Document(path)
        except Exception as e:
            raise CommandError(f"No pude abrir el DOCX: {e}")

        # quién será el created_by de los canales
        creator = None
        if creator_username:
            try:
                creator = User.objects.get(username=creator_username)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"creator_username='{creator_username}' no existe. Buscando superuser..."
                ))
        if not creator:
            creator = User.objects.filter(is_superuser=True).first()
        if not creator:
            raise CommandError("No hay superuser ni creator_username válido. Crea uno con createsuperuser.")

        # El DOCX que enviaste está con este patrón:
        # - Una línea con NOMBRE DE CANAL (ej. 'asistente-consultorio')
        # - Varias líneas con nombres de miembros
        # - Línea en blanco = separador
        # Vamos a parsearlo así:
        blocks = []
        cur = []
        for p in doc.paragraphs:
            text = (p.text or "").strip()
            if not text:
                if cur:
                    blocks.append(cur)
                    cur = []
                continue
            cur.append(text)
        if cur:
            blocks.append(cur)

        total_channels = 0
        total_users_created = 0
        total_memberships = 0

        for block in blocks:
            if not block:
                continue
            channel_name = block[0].strip()
            members = [m.strip() for m in block[1:] if m.strip()]

            # Normaliza nombre del canal: lo usamos tal cual (con guiones si viene así)
            # en DB guardamos 'name' sin '#'
            ch_name_clean = channel_name.lstrip("#").strip()

            # crea/obtiene canal
            channel, ch_created = Channel.objects.get_or_create(
                name=ch_name_clean,
                defaults={"created_by": creator, "is_private": False},
            )
            if ch_created:
                total_channels += 1
                self.stdout.write(self.style.SUCCESS(f"Canal creado: #{channel.name}"))
            else:
                self.stdout.write(f"Canal existente: #{channel.name}")

            # procesa miembros
            for full in members:
                # ignora cabeceras/roles sueltos tipo 'Chofer', 'Editor (a)' si quieres:
                # si te interesa mantenerlos igual, comenta este filtro:
                if len(full) < 3:
                    continue

                # crea user si no existe (buscamos por nombre EXACTO antes de crear slug nuevo)
                user = User.objects.filter(first_name__iexact=full).first()  # si ya guardaste 'first_name' = nombre completo
                if not user:
                    username = slug_username(full)
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            # si quieres separar nombre/apellido, haz split aquí:
                            "first_name": full,  # guardo el nombre completo aquí (simple)
                            "last_name": "",
                            "email": "",  # puedes completar luego
                        },
                    )
                    if created:
                        user.set_password(default_password)
                        user.save()
                        total_users_created += 1
                        self.stdout.write(self.style.SUCCESS(f"  Usuario creado: {user.username} ({full})"))
                    else:
                        self.stdout.write(f"  Usuario existente: {user.username} ({full})")
                else:
                    self.stdout.write(f"  Usuario coincidente por nombre: {user.username} ({full})")

                # añade al canal (sin duplicar)
                _, member_created = ChannelMember.objects.get_or_create(
                    channel=channel, user=user, defaults={"is_admin": False}
                )
                if member_created:
                    total_memberships += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nLISTO ✅  Canales nuevos: {total_channels} | Usuarios nuevos: {total_users_created} | Membresías creadas: {total_memberships}"
        ))
        self.stdout.write(self.style.NOTICE(
            "Contraseña por defecto para nuevos usuarios: " + default_password
        ))
