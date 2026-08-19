# Proceso de construcción

Documento este proceso tal cual pasó, incluyendo los cambios de rumbo y los
errores reales — no es un resumen prolijo hecho después, es la crónica de
la conversación con el agente (Claude).

## 1. El punto de partida: no sabía qué construir

Le conté al agente mi trabajo (coordino un equipo comercial que maneja la
relación con Agentes Productores para un grupo financiero, y también
desarrollo productos nuevos) y le pedí **10 ideas** de cosas que podría
construir con IA para uno de mis mayores consumos de tiempo: revisar el
estado de cada productor antes de una reunión, juntando información de
mails, Excel y un CRM.

El agente armó una lista de 10, de la más obvia a la más rara (desde un
buscador unificado hasta un "simulador de reacción" a productos nuevos), y
para cada una explicó qué haría falta, qué ahorraría, y por dónde empezar.
Elegí la primera y más obvia: un buscador unificado por productor.

## 2. Descubrí que ya había un proyecto arrancado

Al pedirle que avance con esa idea, el agente revisó la carpeta de trabajo
y encontró que ya había un MVP armado en una sesión anterior: un script en
Python que buscaba en Outlook, en Excel de OneDrive y en un CRM propio en
Firebase, usando Claude para redactar el resumen. Es decir, parte del
trabajo ya estaba hecho — el agente lo detectó y reconstruyó el contexto
antes de seguir, en vez de arrancar de cero.

## 3. Soy un principiante total — hubo que bajar el nivel técnico

Cuando el agente empezó a explicar los pasos técnicos (registrar una app
en "Azure AD", conseguir un "MS_CLIENT_ID"), le dije que no entendía nada
de esos términos. El agente cambió el enfoque: empezó a explicar todo en
criollo, paso a paso, esperando confirmación en cada uno antes de seguir, y
usando capturas de pantalla que yo le mandaba para guiarme por lugares
exactos de menús que no encontraba (por ejemplo, cuando no hallaba dónde
ver el nombre de la colección en Firestore).

## 4. Decisión: descartar la parte de Outlook/Azure AD

Mi área de sistemas administra las cuentas de Microsoft, así que había que
pedirles el registro de la app. El agente armó el texto exacto para
pedírselo. Pero más adelante, cuando retomamos el proyecto, decidí
**descartar esa parte** para esta v1.0 y avanzar directo con un Excel que
ya tenía guardado localmente. El agente adaptó la arquitectura: sacó el
conector de Outlook/OneDrive (que dependía de Microsoft Graph) y lo
reemplazó por uno que lee el Excel directo del disco — más simple, sin
necesitar ningún registro ni permiso de IT.

## 5. Decisión: no pagar por la API de Claude

El diseño original usaba la API de Anthropic (de pago) para redactar el
resumen en prosa. Al llegar a ese paso, no entendía por qué tenía que pagar
si ya pago una suscripción de Claude — el agente me explicó la diferencia
(suscripción de chat vs. API de pago por uso) y, como no me convencía
gastar en algo que no había probado todavía, el agente propuso una alternativa:
armar el resumen ordenando los datos directamente en Python, sin IA,
dejando la opción de Claude como algo opcional para más adelante. Elegí
esa alternativa gratuita.

## 6. Instalación y primeros errores reales

Al instalar y correr el programa por primera vez aparecieron **tres errores
reales**, que el agente diagnosticó y arregló uno por uno:

1. **Error de codificación**: la consola de Windows no podía mostrar un
   emoji (⚠️) y el programa se caía (`UnicodeEncodeError`). Se arregló
   forzando la salida a UTF-8 al arrancar.
2. **Firestore no encontraba la base de datos**: el error decía que "la
   base (default) no existe". Investigando junto con una captura de
   pantalla de Firebase, descubrimos que mi proyecto usa una base de
   Firestore con **nombre propio** (no la que se llama "default"), algo
   típico de proyectos creados con Google AI Studio. Hubo que agregar una
   variable de configuración nueva (`FIREBASE_DATABASE_ID`) y pasarla
   explícitamente al conectarse.
3. **Ruta de archivo rota según la carpeta**: al correr el programa desde
   una carpeta distinta (PowerShell abierto en `system32`), no encontraba
   la credencial de Firebase porque la ruta estaba escrita en forma
   relativa. Se arregló haciendo que el programa siempre calcule la ruta
   relativa a la carpeta del proyecto, sin importar desde dónde se ejecute.

También hubo un error de sintaxis mío en PowerShell (me faltaba el
operador `&` antes de un comando entre comillas) — no era un bug del
programa, sino de cómo yo estaba escribiendo el comando.

## 7. Iteración sobre el alcance: sumar más colecciones y noticias

Una vez andando con una sola colección del CRM, pedí que también busque en
otras tres (`aperturas`, `companies`, `reminders`) porque ahí también hay
información relevante de cada productor. Después surgió una idea nueva:
que busque si hay noticias en internet sobre el productor y avise si
encuentra algo. El agente propuso usar el RSS de Google News (gratis, sin
clave) y lo integró como un cuarto conector, con una alerta bien visible al
principio de la ficha si hay resultados.

Un efecto secundario que detectamos probándolo: buscar solo por apellido
("Carafi") trajo noticias de personas distintas con el mismo apellido. El
agente lo corrigió automáticamente: ahora usa el nombre completo que
encuentra en el CRM (en vez del texto que yo tipeo) para buscar las
noticias, lo cual da resultados mucho más precisos.

## 8. Legibilidad para el equipo comercial

El resultado funcionaba pero se veía "como código": una tabla cruda del
Excel con muchas columnas vacías y técnicas. Le pedí que lo hiciera más
amigable para que lo use un comercial en una reunión, no solo yo. Le di a
elegir entre mejorar el formato a mano (gratis) o activar la redacción con
IA (con costo). Elegí la opción gratuita. El agente reescribió el armado
del reporte para que muestre solo los campos con datos reales, en formato
de "ficha" con viñetas y encabezados claros — y en el camino encontramos y
arreglamos un bug propio (separaba en letras sueltas los campos que ya
venían en MAYÚSCULAS, ej. "C u e n t a" en vez de "Cuenta").

## Cómo iteré con el agente (patrón general)

En casi todos los pasos seguí el mismo patrón: le pedía algo en lenguaje
natural, el agente proponía un enfoque (a veces con alternativas explícitas
para que yo elija, como en la decisión de pagar o no la IA), lo implementaba,
y **lo probaba él mismo antes de pasármelo** — corriendo el programa con un
productor real y mostrándome el resultado o el error tal cual salía. Cuando
algo fallaba, no me pasaba el error crudo a resolver: lo diagnosticaba,
proponía la causa más probable, y si necesitaba un dato que no podía ver
(como el nombre exacto de una colección en Firebase), me pedía que le
mandara una captura de pantalla puntual en vez de que yo intente describir
lo que veía.
