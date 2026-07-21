from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, parent, child, sync, payouts
from app.scheduler.jobs import start_scheduler

app = FastAPI(
    title="Bakaláři Rewards API",
    description="Synchronizace známek z Bakalářů + Lightning Address payouty",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(parent.router)
app.include_router(child.router)
app.include_router(sync.router)
app.include_router(payouts.router)


@app.on_event("startup")
async def startup_event():
    start_scheduler()


@app.get("/health")
def health():
    return {"status": "ok"}
