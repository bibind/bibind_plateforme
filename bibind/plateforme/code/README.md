# Odoo REST

Odoo REST es un framework que permite implementar de forma sencilla API REST
para conectar con los objetos de Odoo.

Para lograrlo hace uso principalmente de las siguientes tecnologías:
* flask y flask-restfull para crear el servidor REST
* erppeek para conectar con odoo

Para utilizar Odoo REST será necesario seguir los siguientes pasos:
1. Crear fichero de configuración
2. Crear "resources"
3. Lanzar el servidor

## Crear fichero de configuración
En el directorio raíz del proyecto se encuentra odoo_rest.conf.sample, haz una
copia de este fichero y llamalo odoo_rest.conf

Los parametros disponibles para la configuración son:
* secret_key, será una frase utilizada para encriptar los passwords
* odoo_server, dirección del servidor de odoo, por ejemplo http://localhost:8069
* odoo_db, base de datos a la que nos vamos a conectar

Se ha incluido odoo_rest.conf en el .gitignore para poder crear el fichero de
configuración y que no haya problemas al modificarlo con el repositorio de git.

## Crear resources
Dentro del directorio odoo_rest/odoo_rest se ha de crear una carpeta llamada
resources, y dentro de esta carpeta se ha de crear un fichero para cada
resource.

Un resource será cada uno de los objetos que vamos a definir para conectar con
Odoo. Es decir por cada objeto de Odoo al que queramos conectar tendremos que
crear un resource.

Un ejemplo de resource es:
```
# -*- coding: utf-8 -*-
from ..common.odoo_resource import OdooResource
from ..common.odoo_rest import api


class ResUsers(OdooResource):

    odoo_model = 'res.users'
    odoo_fields = [
        'name',
        'login'
    ]


class ResUsersList(ResUsers):
    pass

api.add_resource(ResUsersList, '/res_users')
api.add_resource(ResUsers, '/res_users/<res_id>')
```
En el resource se podrán sobreescribir los metodos get y post si es necesario
cambiar la forma de mostrar campos o de recibir parametros.

Se ha incluido odoo_rest/resources en el .gitignore para poder crear el
directorio y que no haya problemas al modificarlo con el repositorio de git,
de esta forma podremos tener un repositorio de git con los resources de cada
proyecto.

## Lanzar el servidor
Una vez configurado y creados los resources se lanza directamente ejecutando
el fichero run_odoo_rest

## Test de Odoo REST
Una vez lanzado el servidor de Odoo REST y correctamente configurado contra
un servidor de Odoo se pueden hacer las siguientes pruebas:

### Probar método get
El método get se puede probar directamente en el navegador.

### Probar método post
Con el método post se crean nuevos elementos, se puede probar con:
$ curl -H "Content-Type: application/json" --user admin:admin http://localhost:5000/res_users -d '{"name":"test","login":"login"}' -X POST -v

### Probar método put
Con el método put se actualiza el elemento con el id indicado, se puede probar con:
$ curl -H "Content-Type: application/json" --user admin:admin http://localhost:5000/res_users/5 -d '{"name":"test34"}' -X PUT -v

### Probar método delete
Con el método post se elimina el elemento con el id indicado, se puede probar con:
$ curl --user admin:admin http://localhost:5000/res_users/5 -X DELETE -v
