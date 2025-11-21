from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
from code_generation import router as code_router 

app = FastAPI(title="Code Voice IDE Test Server", version="1.0.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only the code generation router for testing
app.include_router(code_router)

@app.get("/")
async def root():
    return {"message": "Test Code Voice API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)