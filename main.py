import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.pets.routes import pets_router
from controllers.registros.routes import registros_router
from controllers.users.routes import user_router
from controllers.uploadfile.routes import uploadfile_router
from controllers.mantenimiento.routes import mantenimiento_router
from controllers.reportes.routes import reporte_router
from controllers.proveedor.routes import proveedor_router


from config import config

app = FastAPI()

origins = [
    "http://192.168.56.1:8080",
    "http://192.168.56.1:8080",
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://192.168.0.34:8080",
    "http://192.168.0.30:8080",
    "http://192.168.0.31:8080",
    "http://192.168.0.32:8080",
    "http://192.168.0.10:8080",
    "http://95.111.235.214:9776",
    "https://tuenvioexpress.apps.com.pe/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    pets_router,
    prefix="/envios/pets",
    tags=["pets"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    registros_router,
    prefix="/envios/registros",
    tags=["registros"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    user_router,
    prefix="/envios/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    uploadfile_router,
    prefix="/envios/uploads",
    tags=["upload"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    mantenimiento_router,
    prefix="/envios/mantenimiento",
    tags=["mantenimiento"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    reporte_router,
    prefix="/envios/reporte",
    tags=["reporte"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    proveedor_router,
    prefix="/envios/proveedor",
    tags=["proveedor"],
    responses={404: {"description": "Not found"}},
)

@app.on_event("startup")
async def app_startup():
    """
    Do tasks related to app initialization.
    """
    # This if fact does nothing its just an example.
    config.load_config()


@app.on_event("shutdown")
async def app_shutdown():
    """
    Do tasks related to app termination.
    """
    # This does finish the DB driver connection.
    config.close_db_client()


# if __name__ == "__main__":
    # uvicorn.run("main:app", host="0.0.0.0", port=9776)
    # uvicorn.run("main:app", host="0.0.0.0", port=9776, log_level="info", loop="asyncio")
#
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", loop="asyncio")