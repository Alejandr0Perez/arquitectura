from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException


app = FastAPI()

# Conectar con MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.arquitectura

# Modelos Pydantic
class MaterialDetalle(BaseModel):
    nombre: str
    descripcion: str
    categoria: str
    cantidad: int
    unidad_medida: str
    precio_unitario: float

class Herramienta(BaseModel):
    nombre: str
    descripcion: str
    cantidad: int
    estado: str

class Plano(BaseModel):
    nombre: str
    descripcion: str
    url: str

class Proyecto(BaseModel):
    nombre: str
    descripcion: str
    fecha_inicio: str
    fecha_fin: str
    estado: str
    responsable: str
    materiales: List[MaterialDetalle]
    herramientas: List[Herramienta]
    planos: List[Plano]

class Pedido(BaseModel):
    proyecto_id: str
    proveedor_id: str
    material_id: str
    cantidad: int
    fecha_pedido: str
    estatus: str

class ClienteProyecto(BaseModel):
    nombre: str
    descripcion: str
    fecha_inicio: str
    fecha_fin: str
    estado: str
    responsable: str

class Cliente(BaseModel):
    nombre: str
    apellido: str
    email: str
    telefono: str
    direccion: str
    proyectos: List[ClienteProyecto]

class ProyectoAsignado(BaseModel):
    nombre: str
    descripcion: str
    fecha_inicio: str
    fecha_fin: Optional[str]
    estado: str
    responsable: str

class Trabajador(BaseModel):
    nombre: str
    apellido: str
    puesto: str
    salario: float
    fecha_contratacion: str
    fecha_terminacion: Optional[str]
    proyectos_asignados: List[ProyectoAsignado]

class Proveedor(BaseModel):
    nombre: str
    direccion: str
    telefono: str
    email: str

class Material(BaseModel):
    nombre: str
    descripcion: str
    cantidad_disponible: int
    unidad_medida: str
    precio_unitario: float

# Rutas raíz
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Arquitectura API"}
# Rutas para Proyectos
@app.post("/proyectos")
async def agregar_proyecto(proyecto: Proyecto):
    result = await db.proyectos.insert_one(proyecto.dict())
    return {"estatus": "success", "mensaje": "Proyecto agregado", "id": str(result.inserted_id)}

@app.put("/proyectos/{idProyecto}")
async def actualizar_proyecto(idProyecto: str, proyecto: Proyecto):
    result = await db.proyectos.update_one({"_id": ObjectId(idProyecto)}, {"$set": proyecto.dict()})
    return {"estatus": "success", "mensaje": "Proyecto actualizado" if result.modified_count else "No se encontró el proyecto"}

@app.delete("/proyectos/{idProyecto}")
async def eliminar_proyecto(idProyecto: str):
    result = await db.proyectos.delete_one({"_id": ObjectId(idProyecto)})
    return {"estatus": "success", "mensaje": "Proyecto eliminado" if result.deleted_count else "No se encontró el proyecto"}

@app.get("/proyectos/{idProyecto}")
async def consultar_proyecto(idProyecto: str):
    try:
        proyecto = await db.proyectos.find_one({"_id": ObjectId(idProyecto)})
        if proyecto:
            proyecto_id = str(proyecto.pop("_id"))
            proyecto["idProyecto"] = proyecto_id
            return {"estatus": "success", "mensaje": "Proyecto encontrado", "proyecto": proyecto}
        else:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/proyectos/estado/{estado}")
async def consultar_proyectos_por_estado(estado: str):
    try:
        proyectos = await db.proyectos.find({"estado": estado}).to_list(length=100)
        proyectos_info = []
        for proyecto in proyectos:
            proyecto_id = str(proyecto.pop("_id"))
            proyecto["idProyecto"] = proyecto_id
            proyectos_info.append(proyecto)
        return {"estatus": "success", "mensaje": "Proyectos encontrados", "proyectos": proyectos_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/proyectos/responsable/{responsable}")
async def consultar_proyectos_por_responsable(responsable: str):
    try:
        proyectos = await db.proyectos.find({"responsable": responsable}).to_list(length=100)
        proyectos_info = []
        for proyecto in proyectos:
            proyecto_id = str(proyecto.pop("_id"))
            proyecto["idProyecto"] = proyecto_id
            proyectos_info.append(proyecto)
        return {"estatus": "success", "mensaje": "Proyectos encontrados", "proyectos": proyectos_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Rutas para Pedidos
@app.post("/pedidos")
async def agregar_pedido(pedido: Pedido):
    result = await db.pedidos.insert_one(pedido.dict())
    return {"estatus": "success", "mensaje": "Pedido agregado", "id": str(result.inserted_id)}

@app.put("/pedidos/{idPedido}")
async def actualizar_pedido(idPedido: str, pedido: Pedido):
    result = await db.pedidos.update_one({"_id": ObjectId(idPedido)}, {"$set": pedido.dict()})
    return {"estatus": "success", "mensaje": "Pedido actualizado" if result.modified_count else "No se encontró el pedido"}

@app.delete("/pedidos/{idPedido}")
async def eliminar_pedido(idPedido: str):
    result = await db.pedidos.delete_one({"_id": ObjectId(idPedido)})
    return {"estatus": "success", "mensaje": "Pedido eliminado" if result.deleted_count else "No se encontró el pedido"}

@app.get("/pedidos/{idPedido}")
async def consultar_pedido(idPedido: str):
    try:
        Pedido = await db.pedidos.find_one({"_id": ObjectId(idPedido)})
        if Pedido:
            pedido_id = ObjectId(Pedido.pop("_id"))
            Pedido["idPedido"] = pedido_id
            return {"estatus": "success", "mensaje": "pedido encontrado", "pedido": Pedido}
        else:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pedidos/proyecto/{idProyecto}")
async def consultar_pedidos_por_proyecto(idProyecto: str):
    try:
        pedidos = await db.pedidos.find({"proyecto_id": idProyecto}).to_list(length=100)
        pedidos_info = []
        for pedido in pedidos:
            pedido_id = str(pedido.pop("_id"))
            pedido["idPedido"] = pedido_id
            pedidos_info.append(pedido)
        return {"estatus": "success", "mensaje": "Pedidos encontrados", "pedidos": pedidos_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pedidos/proveedor/{idProveedor}")
async def consultar_pedidos_por_proveedor(idProveedor: str):
    try:
        pedidos = await db.pedidos.find({"proveedor_id": idProveedor}).to_list(length=100)
        pedidos_info = []
        for pedido in pedidos:
            pedido_id = str(pedido.pop("_id"))
            pedido["idPedido"] = pedido_id
            pedidos_info.append(pedido)
        return {"estatus": "success", "mensaje": "Pedidos encontrados", "pedidos": pedidos_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rutas para Proveedores
@app.post("/proveedores")
async def agregar_proveedor(proveedor: Proveedor):
    result = await db.proveedores.insert_one(proveedor.dict())
    return {"estatus": "success", "mensaje": "Proveedor agregado", "id": str(result.inserted_id)}

@app.put("/proveedores/{idProveedor}")
async def actualizar_proveedor(idProveedor: str, proveedor: Proveedor):
    result = await db.proveedores.update_one({"_id": ObjectId(idProveedor)}, {"$set": proveedor.dict()})
    return {"estatus": "success", "mensaje": "Proveedor actualizado" if result.modified_count else "No se encontró el proveedor"}

@app.delete("/proveedores/{idProveedor}")
async def eliminar_proveedor(idProveedor: str):
    result = await db.proveedores.delete_one({"_id": ObjectId(idProveedor)})
    return {"estatus": "success", "mensaje": "Proveedor eliminado" if result.deleted_count else "No se encontró el proveedor"}

@app.get("/proveedores/{idProveedor}")
async def consultar_proveedor(idProveedor: str):
    try:
        Proveedor = await db.proveedores.find_one({"_id": ObjectId(idProveedor)})
        if Proveedor:
            proveedor_id = str(Proveedor.pop("_id"))
            Proveedor["idProveedor"] = proveedor_id
            return {"estatus": "success", "mensaje": "Proveedor encontrado", "Proveedor": Proveedor}
        else:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from fastapi import HTTPException



# Rutas para Clientes
@app.post("/clientes")
async def agregar_cliente(cliente: Cliente):
    result = await db.clientes.insert_one(cliente.dict())
    return {"estatus": "success", "mensaje": "Cliente agregado", "id": str(result.inserted_id)}

@app.put("/clientes/{idCliente}")
async def actualizar_cliente(idCliente: str, cliente: Cliente):
    result = await db.clientes.update_one({"_id": ObjectId(idCliente)}, {"$set": cliente.dict()})
    return {"estatus": "success", "mensaje": "Cliente actualizado" if result.modified_count else "No se encontró el cliente"}

@app.delete("/clientes/{idCliente}")
async def eliminar_cliente(idCliente: str):
    result = await db.clientes.delete_one({"_id": ObjectId(idCliente)})
    return {"estatus": "success", "mensaje": "Cliente eliminado" if result.deleted_count else "No se encontró el cliente"}

@app.get("/clientes/{idCliente}")
async def consultar_cliente(idCliente: str):
    try:
        Cliente = await db.clientes.find_one({"_id": ObjectId(idCliente)})
        if Cliente:
            cliente_id = str(Cliente.pop("_id"))
            Cliente["idCliente"] = cliente_id
            return {"estatus": "success", "mensaje": "Cliente encontrado", "Cliente": Cliente}
        else:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Rutas para Trabajadores
@app.post("/trabajadores")
async def agregar_trabajador(trabajador: Trabajador):
    result = await db.trabajadores.insert_one(trabajador.dict())
    return {"estatus": "success", "mensaje": "Trabajador agregado", "id": str(result.inserted_id)}

@app.put("/trabajadores/{idTrabajador}")
async def actualizar_trabajador(idTrabajador: str, trabajador: Trabajador):
    result = await db.trabajadores.update_one({"_id": ObjectId(idTrabajador)}, {"$set": trabajador.dict()})
    return {"estatus": "success", "mensaje": "Trabajador actualizado" if result.modified_count else "No se encontró el trabajador"}

@app.delete("/trabajadores/{idTrabajador}")
async def eliminar_trabajador(idTrabajador: str):
    result = await db.trabajadores.delete_one({"_id": ObjectId(idTrabajador)})
    return {"estatus": "success", "mensaje": "Trabajador eliminado" if result.deleted_count else "No se encontró el trabajador"}

@app.get("/trabajadores/{idTrabajador}")
async def consultar_trabajador(idTrabajador: str):
    try:
        Trabajador = await db.trabajadores.find_one({"_id": ObjectId(idTrabajador)})
        if Trabajador:
            trabajador_id = str(Trabajador.pop("_id"))
            Trabajador["idTrabajador"] = trabajador_id
            return {"estatus": "success", "mensaje": "Trabajador encontrado", "Trabajador": Trabajador}
        else:
            raise HTTPException(status_code=404, detail="Trabajador no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  


# Rutas para Materiales
@app.post("/materiales")
async def agregar_material(material: Material):
    result = await db.materiales.insert_one(material.dict())
    return {"estatus": "success", "mensaje": "Material agregado", "id": str(result.inserted_id)}

@app.put("/materiales/{idMaterial}")
async def actualizar_material(idMaterial: str, material: Material):
    result = await db.materiales.update_one({"_id": ObjectId(idMaterial)}, {"$set": material.dict()})
    return {"estatus": "success", "mensaje": "Material actualizado" if result.modified_count else "No se encontró el material"}

@app.delete("/materiales/{idMaterial}")
async def eliminar_material(idMaterial: str):
    result = await db.materiales.delete_one({"_id": ObjectId(idMaterial)})
    return {"estatus": "success", "mensaje": "Material eliminado" if result.deleted_count else "No se encontró el material"}

@app.get("/materiales/{idMaterial}")
async def consultar_material(idMaterial: str):
    try:
        Material = await db.materiales.find_one({"_id": ObjectId(idMaterial)})
        if Material:
            material_id = str(Material.pop("_id"))
            Material["idMaterial"] = material_id
            return {"estatus": "success", "mensaje": "Material encontrado", "Material": Material}
        else:
            raise HTTPException(status_code=404, detail="Material no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
