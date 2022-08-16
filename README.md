# PyEEPROM

Programa con interfaz gráfica para la lectura y escritura de datos en memoria EEPROM a través de Arduino.

### ¿Por qué buscar usar memorias tipo EEPROM?

Aunque su gran desventaja es que tienen una muy baja capacidad (en el orden de KB), son fácilmente reemplazables, toleran altas y bajas temperaturas, mantienen la información por alrededor de un siglo y soportan hasta un millón de reescrituras, lo cual es muy superior a las comunes memorias flash USB si se desea almacenar información en condiciones más exigentes.

### ¿Por qué usar este programa?

La memoria EEPROM no tiene la habilidad de asignar la información entrante en su interior, su escritura y lectura se realiza de manera directa, de forma cercana al uso de un array, por tanto, este programa se encarga de realizar las asignaciones, borrado y listado de los datos usando una GUI. Además, en caso de no disponer de la GUI los datos escritos son fácilmente legibles por un humano, reduciendo la probabilidad de perdida de datos debida por ejemplo a la corrupción de un sistema de archivo común, como ocurre en el caso de usar memorias USB.
