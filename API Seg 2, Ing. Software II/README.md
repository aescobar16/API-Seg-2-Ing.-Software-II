# ⚽ API REST de Fútbol Histórico

> **Asignatura:** Ingeniería de Software II  
> **Evaluación:** Segundo Seguimiento  
> **Tema:** Arquitectura de Software, Desarrollo de Servicios Web RESTful con FastAPI, Modelado Relacional y Persistencia con SQLite / SQLAlchemy.

---

## 📌 Contexto y Propósito del Proyecto

Este proyecto fue desarrollado como parte de las actividades prácticas de la materia **Ingeniería de Software II**. Su objetivo primordial es diseñar, implementar y documentar una **API RESTful completa** con operaciones CRUD bajo estándares de la industria, integrando:

1. **Patrón de Arquitectura por Capas:** Separación limpia entre la capa de presentación (rutas y endpoints HTTP), capa de validación/negocio (esquemas Pydantic) y capa de persistencia (modelos relacionales SQLAlchemy).
2. **Cumplimiento de Estándares HTTP:** Implementación rigurosa de 4 métodos HTTP distintos (`GET`, `POST`, `PUT`, `DELETE`) con códigos de estado semánticos (`200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`).
3. **Persistencia y Sembrado Automatizado (Seed Data):** Inicialización automática de la base de datos con registros históricos reales para pruebas inmediatas.
4. **Capa Cliente (Frontend Web):** Un panel interactivo desacoplado que consume de forma asíncrona los endpoints mediante JavaScript (`fetch` API).

---

## 🛠️ Stack Tecnológico y Justificación Técnica

| Componente | Tecnología | Versión | Rol y Justificación Técnica |
| :--- | :--- | :--- | :--- |
| **Lenguaje Base** | Python | `3.10+` | Lenguaje de alto nivel, fuertemente tipado mediante anotaciones de tipo (`typing`), ideal para APIs robustas. |
| **Framework Web** | FastAPI | `>= 0.110.0` | Framework moderno y de altísimo rendimiento sobre estándares ASGI. Provee serialización veloz, validación nativa y documentación Swagger automática. |
| **Servidor ASGI** | Uvicorn | `>= 0.28.0` | Servidor asíncrono ultrarrápido basado en `uvloop` y `httptools` para ejecutar aplicaciones FastAPI. |
| **ORM / Persistencia** | SQLAlchemy | `>= 2.0.0` | Object Relational Mapper líder en Python. Permite mapear clases de negocio a tablas relacionales con soporte de claves foráneas y relaciones complejas. |
| **Motor de Base de Datos** | SQLite 3 | Integrado | Motor relacional embebido, serverless y de archivo único (`futbol_historico.db`), que facilita la portabilidad y evaluación del proyecto sin dependencias externas de servidores. |
| **Validación de Datos** | Pydantic V2 | `>= 2.0.0` | Motor de parsing y validación estricta de esquemas y tipos de datos para los cuerpos JSON de las solicitudes y respuestas. |
| **Frontend UI** | HTML5 / CSS3 / JS Vanilla | Estándar W3C | Cliente web ligero y responsivo con tema oscuro, consumo asíncrono con `fetch()`, sin necesidad de frameworks pesados de frontend. |

---

## 🗄️ Modelo Relacional y Entidades

El dominio del sistema administra datos históricos del fútbol mundial a través de cuatro entidades principales:

1. **Equipos (`equipos`):** Clubes con país de origen, año de fundación y conteo de títulos internacionales.
2. **Jugadores (`jugadores`):** Leyendas del fútbol con nombre, apodo, posición, nacionalidad, época dorada y relación de pertenencia (`ForeignKey`) hacia un equipo.
3. **Partidos (`partidos`):** Encuentros memorables con torneo, fecha, equipos rivales, marcador final y estadio.
4. **Goleadores (`goleadores`):** Registro de máximos anotadores históricos con total de goles y torneo destacado, vinculado (`ForeignKey`) a la entidad de jugadores.

---

## 📁 Estructura del Repositorio

```text
├── main.py                  # API principal: configuración, modelos ORM, esquemas Pydantic, endpoints y seed data
├── requirements.txt         # Lista de dependencias del entorno de Python
├── README.md                # Documentación detallada del proyecto y guía de entrega
├── .gitignore               # Exclusión de entornos virtuales, temporales y bases de datos generadas
└── static/
    └── index.html           # Interfaz web interactiva para probar los endpoints en vivo
```

---

## ⚙️ Pasos para Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/aescobar16/API-Seg-2-Ing.-Software-II.git
cd "API-Seg-2-Ing.-Software-II"
```

### 2. Crear y activar el entorno virtual
* **En Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar librerías requeridas
```bash
pip install -r requirements.txt
```

### 4. Iniciar el servidor de desarrollo
```bash
uvicorn main:app --reload --port 8000
```
> **Nota:** Al ejecutar este comando por primera vez, la aplicación creará automáticamente el archivo `futbol_historico.db` y ejecutará la rutina de semilla (`seed data`) precargando equipos, jugadores, partidos y goleadores.

---

## 🖥️ Acceso a la Aplicación

Con el servidor corriendo, los servicios se encuentran en:
* **Frontend Web (Consumo en Vivo):** `http://127.0.0.1:8000`
* **Documentación Interactiva (Swagger UI):** `http://127.0.0.1:8000/docs`
* **Documentación Técnica (ReDoc):** `http://127.0.0.1:8000/redoc`

---

## 📬 Especificación de Endpoints para Pruebas (Postman / Thunder Client)

A continuación se detalla la configuración exacta de las 4 operaciones requeridas:

### 1. `GET /equipos` — Consultar Equipos Registrados
* **Método HTTP:** `GET`
* **URL:** `http://127.0.0.1:8000/equipos`
* **Descripción:** Obtiene la lista completa de clubes históricos con sus títulos internacionales y país.
* **Headers:** No requeridos.
* **Código de Respuesta:** `200 OK`
* **Ejemplo de Respuesta:**
  ```json
  [
    {
      "id": 1,
      "nombre": "Santos FC",
      "pais": "Brasil",
      "fundacion": 1912,
      "titulos_internacionales": 8
    },
    {
      "id": 2,
      "nombre": "Real Madrid",
      "pais": "España",
      "fundacion": 1902,
      "titulos_internacionales": 32
    }
  ]
  ```

---

### 2. `POST /jugadores` — Registrar Nuevo Jugador Histórico
* **Método HTTP:** `POST`
* **URL:** `http://127.0.0.1:8000/jugadores`
* **Descripción:** Da de alta un nuevo jugador legendario enviando su información en formato JSON.
* **Headers:**
  * `Content-Type: application/json`
* **Cuerpo de la Solicitud (Body raw / JSON):**
  ```json
  {
    "nombre": "Zinedine Zidane",
    "apodo": "Zizou",
    "posicion": "Centrocampista",
    "nacionalidad": "Francia",
    "epoca_dorada": "1998-2006",
    "equipo_id": 2
  }
  ```
* **Código de Respuesta:** `201 Created`
* **Ejemplo de Respuesta:**
  ```json
  {
    "id": 5,
    "nombre": "Zinedine Zidane",
    "apodo": "Zizou",
    "posicion": "Centrocampista",
    "nacionalidad": "Francia",
    "epoca_dorada": "1998-2006",
    "equipo_id": 2
  }
  ```

---

### 3. `PUT /partidos/{id}` — Actualizar Datos de un Partido Histórico
* **Método HTTP:** `PUT`
* **URL:** `http://127.0.0.1:8000/partidos/1`
* **Descripción:** Modifica el marcador final o la sede de un partido histórico ya registrado.
* **Headers:**
  * `Content-Type: application/json`
* **Cuerpo de la Solicitud (Body raw / JSON):**
  ```json
  {
    "goles_local": 3,
    "goles_visitante": 2,
    "estadio": "Estadio Azteca (Remodelado)"
  }
  ```
* **Código de Respuesta:** `200 OK`
* **Ejemplo de Respuesta:**
  ```json
  {
    "id": 1,
    "torneo": "Copa del Mundo México 1986 - Cuartos de Final",
    "fecha": "1986-06-22",
    "equipo_local": "Argentina",
    "equipo_visitante": "Inglaterra",
    "goles_local": 3,
    "goles_visitante": 2,
    "estadio": "Estadio Azteca (Remodelado)"
  }
  ```

---

### 4. `DELETE /goleadores/{id}` — Eliminar un Registro de Goleador
* **Método HTTP:** `DELETE`
* **URL:** `http://127.0.0.1:8000/goleadores/1`
* **Descripción:** Da de baja un registro de la tabla de máximos anotadores mediante su identificador.
* **Headers:** No requeridos.
* **Código de Respuesta:** `200 OK` (o `404 Not Found` en caso de no existir).
* **Ejemplo de Respuesta:**
  ```json
  {
    "status": "success",
    "message": "Registro de goleador con ID 1 eliminado exitosamente."
  }
  ```

---

## 🚀 Guía Rápida para Subir este Proyecto a GitHub

Ejecuta los siguientes comandos en tu terminal de PowerShell en la carpeta del proyecto:

```powershell
# 1. Inicializar el repositorio Git local
git init

# 2. Definir la rama principal
git branch -M main

# 3. Agregar los archivos rastreados (respetando el .gitignore)
git add .

# 4. Crear el primer commit
git commit -m "feat: API REST con FastAPI, SQLite y Frontend para Ing. Software II (Seguimiento 2)"

# 5. Vincular con el repositorio de GitHub
git remote add origin https://github.com/aescobar16/API-Seg-2-Ing.-Software-II.git

# 6. Subir el código a GitHub
git push -u origin main
```
