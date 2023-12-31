# Generated by Django 4.2.4 on 2023-11-04 18:30

import config.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DNSService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nombre de la prueba')),
                ('status', models.CharField(max_length=255, verbose_name='Ultimo Estado')),
                ('number_probe', models.IntegerField(default=1, verbose_name='Numero de pruebas')),
                ('probe_timeout', models.FloatField(default=1.0, verbose_name='Tiempo de espera por pruebas')),
                ('in_process', models.BooleanField(default=False)),
                ('processed_by', models.CharField(max_length=100, null=True)),
                ('current_iteration', models.IntegerField(blank=True, null=True)),
                ('is_monitoring', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type_service', models.CharField(blank=True, max_length=50, null=True)),
                ('ip_address', models.GenericIPAddressField(null=True)),
                ('port', models.IntegerField(blank=True, null=True)),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'DNSService',
                'verbose_name_plural': 'DNSServices',
                'db_table': 'DNSService',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='HTTPService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nombre de la prueba')),
                ('status', models.CharField(max_length=255, verbose_name='Ultimo Estado')),
                ('number_probe', models.IntegerField(default=1, verbose_name='Numero de pruebas')),
                ('probe_timeout', models.FloatField(default=1.0, verbose_name='Tiempo de espera por pruebas')),
                ('in_process', models.BooleanField(default=False)),
                ('processed_by', models.CharField(max_length=100, null=True)),
                ('current_iteration', models.IntegerField(blank=True, null=True)),
                ('is_monitoring', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type_service', models.CharField(blank=True, max_length=50, null=True)),
                ('port', models.IntegerField(default=1)),
                ('url', models.URLField()),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'HTTPService',
                'verbose_name_plural': 'HTTPServices',
                'db_table': 'httpSercice',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ICMPService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nombre de la prueba')),
                ('status', models.CharField(max_length=255, verbose_name='Ultimo Estado')),
                ('number_probe', models.IntegerField(default=1, verbose_name='Numero de pruebas')),
                ('probe_timeout', models.FloatField(default=1.0, verbose_name='Tiempo de espera por pruebas')),
                ('in_process', models.BooleanField(default=False)),
                ('processed_by', models.CharField(max_length=100, null=True)),
                ('current_iteration', models.IntegerField(blank=True, null=True)),
                ('is_monitoring', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type_service', models.CharField(blank=True, max_length=50, null=True)),
                ('dns_ip', models.CharField(max_length=50)),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'ICMPService',
                'verbose_name_plural': 'ICMPServices',
                'db_table': 'icmpService',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TFProtocolService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nombre de la prueba')),
                ('status', models.CharField(max_length=255, verbose_name='Ultimo Estado')),
                ('number_probe', models.IntegerField(default=1, verbose_name='Numero de pruebas')),
                ('probe_timeout', models.FloatField(default=1.0, verbose_name='Tiempo de espera por pruebas')),
                ('in_process', models.BooleanField(default=False)),
                ('processed_by', models.CharField(max_length=100, null=True)),
                ('current_iteration', models.IntegerField(blank=True, null=True)),
                ('is_monitoring', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type_service', models.CharField(blank=True, max_length=50, null=True)),
                ('address', models.CharField(max_length=100)),
                ('port', models.IntegerField(blank=True, null=True)),
                ('hash', models.CharField(max_length=250)),
                ('version', models.CharField(max_length=100)),
                ('public_key', models.TextField(max_length=6000)),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'TFProtocolService',
                'verbose_name_plural': 'TFProtocolServices',
                'db_table': 'TFProtocolService',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TCPService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nombre de la prueba')),
                ('status', models.CharField(max_length=255, verbose_name='Ultimo Estado')),
                ('number_probe', models.IntegerField(default=1, verbose_name='Numero de pruebas')),
                ('probe_timeout', models.FloatField(default=1.0, verbose_name='Tiempo de espera por pruebas')),
                ('in_process', models.BooleanField(default=False)),
                ('processed_by', models.CharField(max_length=100, null=True)),
                ('current_iteration', models.IntegerField(blank=True, null=True)),
                ('is_monitoring', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type_service', models.CharField(blank=True, max_length=50, null=True)),
                ('ip_address', models.CharField(max_length=50, verbose_name='IP/DNS')),
                ('port', models.IntegerField(blank=True, null=True)),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'TCPService',
                'verbose_name_plural': 'TCPServices',
                'db_table': 'TCPService',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ServiceStatusTFProtocol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('cpu_processing_time', models.FloatField(blank=True, null=True)),
                ('is_up', models.CharField(max_length=50)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.tfprotocolservice')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ServiceStatusTCP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('cpu_processing_time', models.FloatField(blank=True, null=True)),
                ('is_up', models.CharField(max_length=50)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.tcpservice')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ServiceStatusICMP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('cpu_processing_time', models.FloatField(blank=True, null=True)),
                ('is_up', models.CharField(max_length=50)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.icmpservice')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ServiceStatusHttp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('cpu_processing_time', models.FloatField(blank=True, null=True)),
                ('is_up', models.CharField(max_length=50)),
                ('response_status', models.CharField(blank=True, max_length=50, null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.httpservice')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ServiceStatusDNS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('cpu_processing_time', models.FloatField(blank=True, null=True)),
                ('is_up', models.CharField(max_length=50)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.dnsservice')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ServiceModificationTFP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.tfprotocolservice')),
            ],
            options={
                'verbose_name': 'Service Modification TFProtocol',
                'verbose_name_plural': 'Service Modifications TFProtocol',
                'db_table': 'ServiceModificationTFP',
            },
        ),
        migrations.CreateModel(
            name='ServiceModificationTCP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.tcpservice')),
            ],
            options={
                'verbose_name': 'Service Modification TCP',
                'verbose_name_plural': 'Service Modifications TCP',
                'db_table': 'ServiceModificationTCP',
            },
        ),
        migrations.CreateModel(
            name='ServiceModificationICMP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.icmpservice')),
            ],
            options={
                'verbose_name': 'Service Modification ICMP',
                'verbose_name_plural': 'Service Modifications ICMP',
                'db_table': 'ServiceModificationICMP',
            },
        ),
        migrations.CreateModel(
            name='ServiceModificationHTTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.httpservice')),
            ],
            options={
                'verbose_name': 'Service Modification HTTP',
                'verbose_name_plural': 'Service Modifications HTTP',
                'db_table': 'ServiceModificationHTTP',
            },
        ),
        migrations.CreateModel(
            name='ServiceModificationDNS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.dnsservice')),
            ],
            options={
                'verbose_name': 'Service Modification DNS',
                'verbose_name_plural': 'Service Modifications DNS',
                'db_table': 'ServiceModificationDNS',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(upload_to=config.models.user_directory_path_profile)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
