from django.contrib import admin
from Footprint.models import *

#class UsuarioAdmin(admin.ModelAdmin):
#	list_display = ('id', 'username', 'email')

#class CategoriaAdmin(admin.ModelAdmin):
#	list_display = ('id','unidad', 'descripcion')

#class EdificioAdmin(admin.ModelAdmin):
#	list_display = ('id','descripcion')

#class Punto_MonitoreoAdmin(admin.ModelAdmin):
#	list_display = ('id', 'denominacion','ubicacion','edificio')

#class MedicionAdmin(admin.ModelAdmin):
#	list_display = ('id','valor','fecha','punto',
#                    'edificio','tipo_medicion')

admin.site.register(Usuario)
admin.site.register(Edificio)
admin.site.register(Punto_Monitoreo)
admin.site.register(Medicion)
admin.site.register(Categoria)
admin.site.register(Variable)
admin.site.register(ValorVariable_Medicion)

#admin.site.register(Usuario, UsuarioAdmin)
#admin.site.register(Tipo_Medicion, Tipo_MedicionAdmin)
#admin.site.register(Edificio,EdificioAdmin)
#admin.site.register(Punto_Monitoreo, Punto_MonitoreoAdmin)
#admin.site.register(Medicion,MedicionAdmin)
