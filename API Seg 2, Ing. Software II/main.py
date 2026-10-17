import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# ==============================================================================
# CONFIGURACIÓN DE BASE DE DATOS SQLITE Y SQLALCHEMY
# ==============================================================================
DATABASE_URL = "sqlite:///./futbol_historico.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==============================================================================
# MODELOS DE BASE DE DATOS (ORM)
# ==============================================================================
class EquipoDB(Base):
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    pais = Column(String(60), nullable=False)
    fundacion = Column(Integer, nullable=True)
    titulos_internacionales = Column(Integer, default=0)

    jugadores = relationship("JugadorDB", back_populates="equipo")


class JugadorDB(Base):
    __tablename__ = "jugadores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apodo = Column(String(50), nullable=True)
    posicion = Column(String(50), nullable=False)
    nacionalidad = Column(String(60), nullable=False)
    epoca_dorada = Column(String(50), nullable=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=True)

    equipo = relationship("EquipoDB", back_populates="jugadores")
    goleador_rel = relationship("GoleadorDB", back_populates="jugador", uselist=False)


class PartidoDB(Base):
    __tablename__ = "partidos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    torneo = Column(String(100), nullable=False)
    fecha = Column(String(30), nullable=False)  # Formato YYYY-MM-DD
    equipo_local = Column(String(100), nullable=False)
    equipo_visitante = Column(String(100), nullable=False)
    goles_local = Column(Integer, default=0)
    goles_visitante = Column(Integer, default=0)
    estadio = Column(String(120), nullable=True)


class GoleadorDB(Base):
    __tablename__ = "goleadores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    jugador_id = Column(Integer, ForeignKey("jugadores.id"), nullable=False)
    goles_totales = Column(Integer, nullable=False)
    torneo_destacado = Column(String(120), nullable=True)

    jugador = relationship("JugadorDB", back_populates="goleador_rel")


# ==============================================================================
# ESQUEMAS PYDANTIC (VALIDACIÓN Y SERIALIZACIÓN)
# ==============================================================================
class EquipoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    pais: str
    fundacion: Optional[int] = None
    titulos_internacionales: int = 0


class JugadorCreate(BaseModel):
    nombre: str
    apodo: Optional[str] = None
    posicion: str
    nacionalidad: str
    epoca_dorada: Optional[str] = None
    equipo_id: Optional[int] = None


class JugadorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apodo: Optional[str] = None
    posicion: str
    nacionalidad: str
    epoca_dorada: Optional[str] = None
    equipo_id: Optional[int] = None


class PartidoUpdate(BaseModel):
    torneo: Optional[str] = None
    fecha: Optional[str] = None
    equipo_local: Optional[str] = None
    equipo_visitante: Optional[str] = None
    goles_local: Optional[int] = None
    goles_visitante: Optional[int] = None
    estadio: Optional[str] = None


class PartidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    torneo: str
    fecha: str
    equipo_local: str
    equipo_visitante: str
    goles_local: int
    goles_visitante: int
    estadio: Optional[str] = None


class GoleadorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    jugador_id: int
    goles_totales: int
    torneo_destacado: Optional[str] = None
    jugador_nombre: Optional[str] = None


# ==============================================================================
# INICIALIZACIÓN DE LA API Y MIDDLEWARE
# ==============================================================================
app = FastAPI(
    title="API de Fútbol Histórico",
    description="API RESTful construida con FastAPI y SQLite para registrar y consultar hitos históricos del fútbol mundial.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# SEED DE DATOS HISTÓRICOS INICIALES
# ==============================================================================
def inicializar_base_de_datos():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(EquipoDB).count() == 0:
            # 1. Equipos Históricos
            equipos = [
                EquipoDB(nombre="Santos FC", pais="Brasil", fundacion=1912, titulos_internacionales=8),
                EquipoDB(nombre="Real Madrid", pais="España", fundacion=1902, titulos_internacionales=32),
                EquipoDB(nombre="SSC Napoli", pais="Italia", fundacion=1926, titulos_internacionales=1),
                EquipoDB(nombre="AFC Ajax", pais="Países Bajos", fundacion=1900, titulos_internacionales=11),
                EquipoDB(nombre="Boca Juniors", pais="Argentina", fundacion=1905, titulos_internacionales=22)
            ]
            db.add_all(equipos)
            db.commit()

            # 2. Jugadores Legendarios
            jugadores = [
                JugadorDB(nombre="Pelé (Edson Arantes do Nascimento)", apodo="O Rei", posicion="Delantero", nacionalidad="Brasil", epoca_dorada="1958-1970", equipo_id=1),
                JugadorDB(nombre="Diego Armando Maradona", apodo="El Pibe de Oro", posicion="Mediapunta", nacionalidad="Argentina", epoca_dorada="1982-1990", equipo_id=3),
                JugadorDB(nombre="Johan Cruyff", apodo="El Flaco", posicion="Extremo / Mediapunta", nacionalidad="Países Bajos", epoca_dorada="1971-1974", equipo_id=4),
                JugadorDB(nombre="Alfredo Di Stéfano", apodo="La Saeta Rubia", posicion="Delantero total", nacionalidad="Argentina / España", epoca_dorada="1953-1964", equipo_id=2)
            ]
            db.add_all(jugadores)
            db.commit()

            # 3. Partidos Históricos
            partidos = [
                PartidoDB(
                    torneo="Copa del Mundo México 1986 - Cuartos de Final",
                    fecha="1986-06-22",
                    equipo_local="Argentina",
                    equipo_visitante="Inglaterra",
                    goles_local=2,
                    goles_visitante=1,
                    estadio="Estadio Azteca"
                ),
                PartidoDB(
                    torneo="Copa del Mundo México 1970 - Final",
                    fecha="1970-06-21",
                    equipo_local="Brasil",
                    equipo_visitante="Italia",
                    goles_local=4,
                    goles_visitante=1,
                    estadio="Estadio Azteca"
                ),
                PartidoDB(
                    torneo="Copa de Europa 1960 - Final",
                    fecha="1960-05-18",
                    equipo_local="Real Madrid",
                    equipo_visitante="Eintracht Frankfurt",
                    goles_local=7,
                    goles_visitante=3,
                    estadio="Hampden Park"
                )
            ]
            db.add_all(partidos)
            db.commit()

            # 4. Goleadores
            goleadores = [
                GoleadorDB(jugador_id=1, goles_totales=1281, torneo_destacado="Copa del Mundo (12 goles) y Santos"),
                GoleadorDB(jugador_id=2, goles_totales=346, torneo_destacado="Serie A Napoli y México 1986"),
                GoleadorDB(jugador_id=4, goles_totales=514, torneo_destacado="Copa de Europa (5 títulos consecutivos)")
            ]
            db.add_all(goleadores)
            db.commit()
    finally:
        db.close()

# Ejecutar inicialización al cargar
inicializar_base_de_datos()


# ==============================================================================
# ENDPOINTS SOLICITADOS (4 MÉTODOS HTTP DISTINTOS)
# ==============================================================================

# 1. GET /equipos: Obtener la lista de todos los equipos registrados
@app.get("/equipos", response_model=List[EquipoResponse], tags=["Equipos"], summary="Listar todos los equipos")
def get_equipos(db: Session = Depends(get_db)):
    """Retorna la lista completa de equipos de fútbol históricos registrados."""
    equipos = db.query(EquipoDB).order_by(EquipoDB.id).all()
    return equipos


# 2. POST /jugadores: Registrar un nuevo jugador histórico
@app.post("/jugadores", response_model=JugadorResponse, status_code=status.HTTP_201_CREATED, tags=["Jugadores"], summary="Registrar un nuevo jugador")
def crear_jugador(jugador: JugadorCreate, db: Session = Depends(get_db)):
    """Registra un nuevo jugador histórico en la base de datos."""
    if jugador.equipo_id is not None:
        equipo = db.query(EquipoDB).filter(EquipoDB.id == jugador.equipo_id).first()
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El equipo con ID {jugador.equipo_id} no existe."
            )

    nuevo_jugador = JugadorDB(
        nombre=jugador.nombre,
        apodo=jugador.apodo,
        posicion=jugador.posicion,
        nacionalidad=jugador.nacionalidad,
        epoca_dorada=jugador.epoca_dorada,
        equipo_id=jugador.equipo_id
    )
    db.add(nuevo_jugador)
    db.commit()
    db.refresh(nuevo_jugador)
    return nuevo_jugador


# 3. PUT /partidos/{id}: Actualizar el resultado o datos de un partido histórico existente
@app.put("/partidos/{id}", response_model=PartidoResponse, tags=["Partidos"], summary="Actualizar partido histórico")
def actualizar_partido(id: int, partido_data: PartidoUpdate, db: Session = Depends(get_db)):
    """Actualiza los campos proporcionados de un partido histórico específico."""
    partido = db.query(PartidoDB).filter(PartidoDB.id == id).first()
    if not partido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partido con ID {id} no encontrado."
        )

    datos_actualizar = partido_data.model_dump(exclude_unset=True)
    if not datos_actualizar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un campo para actualizar."
        )

    for campo, valor in datos_actualizar.items():
        setattr(partido, campo, valor)

    db.commit()
    db.refresh(partido)
    return partido


# 4. DELETE /goleadores/{id}: Eliminar un registro de la lista de goleadores
@app.delete("/goleadores/{id}", status_code=status.HTTP_200_OK, tags=["Goleadores"], summary="Eliminar goleador")
def eliminar_goleador(id: int, db: Session = Depends(get_db)):
    """Elimina el registro de un goleador histórico por su ID."""
    goleador = db.query(GoleadorDB).filter(GoleadorDB.id == id).first()
    if not goleador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goleador con ID {id} no encontrado."
        )

    db.delete(goleador)
    db.commit()
    return {
        "status": "success",
        "message": f"Registro de goleador con ID {id} eliminado exitosamente."
    }


# ==============================================================================
# ENDPOINTS ADICIONALES DE APOYO PARA EL FRONTEND (LISTADOS AUXILIARES)
# ==============================================================================
@app.get("/jugadores", response_model=List[JugadorResponse], tags=["Jugadores"], summary="Listar jugadores")
def get_jugadores(db: Session = Depends(get_db)):
    return db.query(JugadorDB).order_by(JugadorDB.id).all()

@app.get("/partidos", response_model=List[PartidoResponse], tags=["Partidos"], summary="Listar partidos")
def get_partidos(db: Session = Depends(get_db)):
    return db.query(PartidoDB).order_by(PartidoDB.id).all()

@app.get("/goleadores", tags=["Goleadores"], summary="Listar goleadores")
def get_goleadores(db: Session = Depends(get_db)):
    resultados = []
    goleadores = db.query(GoleadorDB).all()
    for g in goleadores:
        nombre_jugador = g.jugador.nombre if g.jugador else "Desconocido"
        resultados.append({
            "id": g.id,
            "jugador_id": g.jugador_id,
            "jugador_nombre": nombre_jugador,
            "goles_totales": g.goles_totales,
            "torneo_destacado": g.torneo_destacado
        })
    return resultados

# ==============================================================================
# SERVIR FRONTEND ESTÁTICO SI EXISTE LA CARPETA STATIC
# ==============================================================================
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
