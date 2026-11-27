from fastapi import FastAPI
from app.api.routes import animals, biometrics

app = FastAPI(
    title="Nose Print Biometric Identification API",
    version="0.1.0",
    description="Research PoC. Similarity is not proof of animal identity.",
)
app.include_router(animals.router, prefix="/api/v1")
app.include_router(biometrics.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": "noseprint-biometric-api"}
