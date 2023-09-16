# Generated by Django 4.2.4 on 2023-09-16 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
                ('stop_flags', models.IntegerField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(null=True)),
                ('port', models.IntegerField(blank=True, null=True)),
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
                ('stop_flags', models.IntegerField(blank=True, null=True)),
                ('port', models.IntegerField(default=1)),
                ('url', models.URLField()),
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
                ('stop_flags', models.IntegerField(blank=True, null=True)),
                ('dns_ip', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'ICMPService',
                'verbose_name_plural': 'ICMPServices',
                'db_table': 'icmpService',
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
                ('stop_flags', models.IntegerField(blank=True, null=True)),
                ('ip_address', models.CharField(max_length=50, verbose_name='IP/DNS')),
                ('port', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'TCPService',
                'verbose_name_plural': 'TCPServices',
                'db_table': 'TCPService',
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
                ('stop_flags', models.IntegerField(blank=True, null=True)),
                ('dns', models.CharField(max_length=50)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('port', models.IntegerField(blank=True, null=True)),
                ('hash', models.CharField(max_length=250)),
                ('version', models.CharField(max_length=100)),
                ('public_key', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'TFProtocolService',
                'verbose_name_plural': 'TFProtocolServices',
                'db_table': 'TFProtocolService',
                'managed': True,
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
    ]
