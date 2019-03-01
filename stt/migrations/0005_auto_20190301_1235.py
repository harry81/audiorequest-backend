# Generated by Django 2.1.3 on 2019-03-01 12:35

from django.db import migrations, models
from stt.models import Stt
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('stt', '0004_auto_20190222_0704'),
    ]

    def gen_uuid(apps, schema_editor):
        for row in Stt.objects.all():
            row.uuid = uuid.uuid4()
            row.save()

    operations = [
        migrations.AddField(
            model_name='stt',
            name='uuid',
            field=models.SlugField(default=uuid.uuid4),
            preserve_default=True,
        ),
        migrations.RunPython(gen_uuid),

        migrations.AlterField(
            model_name='stt',
            name='uuid',
            field=models.SlugField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='stt',
            name='lang_code',
            field=models.CharField(default='ko-KR', max_length=8),
        ),
    ]