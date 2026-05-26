import os
import shutil
import uvicorn
import nest_asyncio
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pyngrok import ngrok
from src.inference import my_finetuned_ocr_tool_full

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    temp_pdf_path = f"./data/{file.filename}" 
    try:
        with open(temp_pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        markdown_result = my_finetuned_ocr_tool_full(temp_pdf_path)
        
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
            
        return PlainTextResponse(content=markdown_result, media_type="text/markdown")
        
    except Exception as e:
        return PlainTextResponse(content=f"Lỗi xử lý OCR: {str(e)}", status_code=500)

def start_server():
    NGROK_AUTH_TOKEN = "3BVlsDwoTkPQgC0RgVKc5d6js8C_5MZCmPKqofZaEotxqtUJ3"
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    auth_proxy_tunnel = ngrok.connect(8000)
    print(f"API: {auth_proxy_tunnel.public_url}")
    
    nest_asyncio.apply()
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    import asyncio
    asyncio.run(server.serve())

if __name__ == "__main__":
    start_server()