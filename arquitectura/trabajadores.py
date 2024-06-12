from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import date

app = FastAPI()

# Conexión a MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.arquitectura

# Modelos de datos
class Trabajador(BaseModel):
    nombre: str
    apellido: str
    puesto: str
    salario: float
    fecha_contratacion: date
    fecha_terminacion: Optional[date] = None

class TrabajadorOut(Trabajador):
    idTrabajador: str

# Operaciones expuestas
@app.post("/trabajadores/", response_model=TrabajadorOut)
async def agregar_trabajador(trabajador: Trabajador):
    nuevo_trabajador = await db.trabajadores.insert_one(trabajador.dict())
    trabajador_guardado = await db.trabajadores.find_one({"_id": nuevo_trabajador.inserted_id})
    return {**trabajador_guardado, "idTrabajador": str(trabajador_guardado["_id"])}

@app.put("/trabajadores/{idTrabajador}", response_model=TrabajadorOut)
async def actualizar_trabajador(idTrabajador: str, trabajador: Trabajador):
    trabajador_obj_id = ObjectId(idTrabajador)
    result = await db.trabajadores.update_one({"_id": trabajador_obj_id}, {"$set": trabajador.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")
    trabajador_actualizado = await db.trabajadores.find_one({"_id": trabajador_obj_id})
    return {**trabajador_actualizado, "idTrabajador": str(trabajador_actualizado["_id"])}

@app.delete("/trabajadores/{idTrabajador}", response_model=dict)
async def eliminar_trabajador(idTrabajador: str):
    trabajador_obj_id = ObjectId(idTrabajador)
    result = await db.trabajadores.delete_one({"_id": trabajador_obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")
    return {"estatus": "Éxito", "mensaje": "Trabajador eliminado correctamente"}

@app.get("/trabajadores/{idTrabajador}", response_model=TrabajadorOut)
async def consultar_trabajador_por_id(idTrabajador: str):
    trabajador_obj_id = ObjectId(idTrabajador)
    trabajador = await db.trabajadores.find_one({"_id": trabajador_obj_id})
    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")
    return {**trabajador, "idTrabajador": str(trabajador["_id"])}

@app.get("/trabajadores/proyecto/{idProyecto}", response_model=List[TrabajadorOut])
async def consultar_trabajadores_por_proyecto(idProyecto: str):
    trabajadores = await db.trabajadores.find({"proyectos": idProyecto}).to_list(100)
    return [{**trabajador, "idTrabajador": str(trabajador["_id"])} for trabajador in trabajadores]
