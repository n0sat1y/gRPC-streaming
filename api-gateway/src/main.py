import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.kafka import router as kafka_router
from src.api import router
from src.handlers.grpc import grpc_service



@asynccontextmanager
async def lifespan(app: FastAPI):
    await grpc_service.start()
    yield
    await grpc_service.stop()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(kafka_router)

if __name__ == '__main__':
    uvicorn.run(
        'src.main:app',
        reload=True
    )
