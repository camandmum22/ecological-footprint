from django.db import models

# Create your models here.
class Usuario(models.Model):
    #id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.EmailField(max_length=50, default='email@email.com')

    def __str__(self):              # __unicode__ on Python 2
        return str(self.id)+" "+self.username#+" "+self.password

class Categoria(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    descripcion = models.CharField(max_length=80)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.id)+" "+self.descripcion

class Edificio(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    descripcion = models.CharField(max_length=80)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.id)+" "+self.descripcion

class Variable(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    unidad = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=80)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.id)+" "+self.unidad+" "+self.descripcion

class Punto_Monitoreo(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    denominacion = models.CharField(max_length=80)
    #--edificio = models.ForeignKey(Edificio)
    edificio = models.OneToOneField(Edificio, primary_key=True)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.id)+" "+self.denominacion+" "+self.edificio.id

class Medicion(models.Model):
    #id = models.IntegerField(primary_key=True)
    fecha = models.DateTimeField(auto_now=True)
    punto = models.ForeignKey(Punto_Monitoreo)
    #--edificio = models.ForeignKey(Edificio)
    #edificio = models.ForeignKey(Punto_Monitoreo)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.id)+" "+self.fecha.__str__()+" "+self.punto.id+" "#+self.edificio.id

class ValorVariable_Medicion(models.Model):
    #id = models.IntegerField(primary_key=True)
    valor = models.DecimalField(max_digits=10,decimal_places=2)
    variable = models.ForeignKey(Variable)
    medicion = models.ForeignKey(Medicion)
    categoria = models.ForeignKey(Categoria)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.id)+" "+str(self.valor)+" "+self.variable.id+" "\
        +self.medicion.fecha.__str__()+" "+self.medicion.punto.id+" "+self.categoria.id+"\n"
