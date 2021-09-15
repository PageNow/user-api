from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core import config, tasks

from app.api.api import api_router

app = FastAPI(title=config.PROJECT_NAME, version=config.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_event_handler("startup", tasks.create_start_app_handler(app))
app.add_event_handler("shutdown", tasks.create_start_app_handler(app))

app.include_router(api_router)
