from fastapi import FastAPI

app = FastAPI(title="Pet Shop API")

@app.get("/health")
def health():
    return {"status": "ok", "project": "Pet_Shop_v2"}
