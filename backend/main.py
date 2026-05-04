from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import data_service
import os

app = FastAPI(title="BTS Contract Automation API")

# Cấu hình đường dẫn
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data_source")

service = data_service.DataService(data_dir=DATA_DIR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "BTS Contract Automation API is online"}

@app.get("/site/{site_id}")
async def get_site(site_id: str):
    try:
        data = service.get_site_data(site_id.upper())
        if "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
