from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import reports

app = FastAPI()

origins = [
    "http://localhost:8000",
    "https://reportgri.nliwod.org",    
]

# Allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports.router)


@app.get("/")
def root():
    return {"Hello": "World"}
