print("hola mundo") #este es un comentario

#variables

fabri = "nombre"

entero = 20
decimal = 100,33


#operadores
print (10 + 20)

class lenguaje:
    def __init__(self, nombre, año):
        self.nombre = nombre 
        self.año = año
    def descripcion(self):
        print ("%s fue creado en %s" % (self.nombre, self.año))

javascript = lenguaje("JavaScript", 1995)
javascript.descripcion()  
        
        