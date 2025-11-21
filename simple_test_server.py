"""
简单的测试服务器
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "测试服务器运行正常", "status": "ok"}

@app.get("/test")
def test():
    return {"test": "success", "server": "simple"}

if __name__ == "__main__":
    print("启动简单测试服务器...")
    uvicorn.run(app, host="localhost", port=8001) 