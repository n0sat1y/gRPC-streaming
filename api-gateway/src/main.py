from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import src.infrastructure.kafka_consumers.message
import src.infrastructure.kafka_consumers.presence
from src.api import router
from src.core.kafka import router as kafka_router
from src.infrastructure.grpc_clients import grpc_service
from src.utils.enums.status_code import CodeEnum
from src.utils.exceptions import GrpcError


@asynccontextmanager
async def lifespan(app: FastAPI):
    await grpc_service.start()

    yield
    await grpc_service.stop()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(GrpcError)
async def grpc_exception_handler(request: Request, exc: GrpcError):
    http_code = CodeEnum.from_grpc_code(exc.code)
    return JSONResponse(
        status_code=http_code,
        content={"detail": exc.detail},
    )


app.include_router(router)
app.include_router(kafka_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True, host="0.0.0.0", port=8000)
