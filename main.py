"""
FastAPI 空响应检查服务
作者: zinan-c
日期: 2026-01-19
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time

# 创建 FastAPI 应用实例
# - title: API 文档标题
# - description: API 描述
# - version: API 版本
app = FastAPI(
    title="空响应检查服务",
    description="这是一个用于检查空响应的示例 FastAPI 服务",
    version="1.0.0"
)

# ============================================
# 数据模型定义 (使用 Pydantic)
# ============================================

class CheckRequest(BaseModel):
    """
    检查请求的数据模型
    
    属性:
    - data: 任意数据，用于测试
    - check_empty: 是否检查为空，默认为 True
    - timeout: 模拟超时时间（毫秒），默认为 0
    """
    data: Optional[Any] = None
    check_empty: bool = True
    timeout: int = 0


class CheckResponse(BaseModel):
    """
    检查响应的数据模型
    
    属性:
    - success: 请求是否成功
    - message: 响应消息
    - is_empty: 输入数据是否为空
    - timestamp: 响应时间戳
    - processing_time_ms: 处理时间（毫秒）
    """
    success: bool
    message: str
    is_empty: bool
    timestamp: str
    processing_time_ms: float


# ============================================
# 工具函数
# ============================================

def is_data_empty(data: Any) -> bool:
    """
    检查数据是否为空的工具函数
    
    参数:
    - data: 要检查的数据
    
    返回:
    - bool: 如果数据为空返回 True，否则返回 False
    
    注意: 这里定义了多种空值情况：
    1. None
    2. 空字符串
    3. 空列表
    4. 空字典
    5. 空集合
    """
    if data is None:
        return True
    elif isinstance(data, str) and data.strip() == "":
        return True
    elif isinstance(data, (list, dict, set, tuple)) and len(data) == 0:
        return True
    return False


# ============================================
# API 端点定义
# ============================================

@app.get("/")
async def root():
    """
    根端点 - 返回服务信息
    
    返回:
    - dict: 包含服务信息的字典
    
    这个端点用于：
    1. 验证服务是否正常运行
    2. 提供基本的服务信息
    3. 作为健康检查端点
    """
    return {
        "service": "空响应检查服务",
        "version": "1.0.0",
        "status": "运行中",
        "endpoints": {
            "GET /": "服务信息",
            "POST /api/check-empty": "检查空响应",
            "GET /api/health": "健康检查"
        }
    }


@app.get("/api/health")
async def health_check():
    """
    健康检查端点
    
    返回:
    - dict: 包含健康状态的信息
    
    用途：
    1. 监控系统可以定期调用此端点
    2. 确保服务正常运行
    3. 返回服务状态和当前时间
    """
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "service": "empty-response-checker"
    }


@app.post("/api/check-empty", response_model=CheckResponse)
async def check_empty_response(request: CheckRequest):
    """
    检查空响应的主 API 端点
    
    参数:
    - request: CheckRequest 对象，包含请求数据
    
    返回:
    - CheckResponse: 检查结果
    
    处理流程：
    1. 记录开始时间
    2. 检查是否需要模拟超时
    3. 验证输入数据
    4. 检查数据是否为空
    5. 构建并返回响应
    
    可能出现的 HTTP 状态码：
    - 200: 请求成功处理
    - 400: 请求参数错误
    - 500: 服务器内部错误
    """
    start_time = time.time()
    
    try:
        # 1. 模拟处理时间（如果设置了 timeout）
        if request.timeout > 0:
            # 使用 await asyncio.sleep() 在真实异步环境中
            import asyncio
            await asyncio.sleep(request.timeout / 1000)
        
        # 2. 检查数据是否为空
        is_empty = False
        if request.check_empty:
            is_empty = is_data_empty(request.data)
        
        # 3. 计算处理时间
        processing_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 4. 构建响应
        response = CheckResponse(
            success=True,
            message="检查完成" if not is_empty else "数据为空",
            is_empty=is_empty,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            processing_time_ms=round(processing_time, 2)
        )
        
        return response
        
    except Exception as e:
        # 错误处理：记录错误并返回适当的 HTTP 错误
        processing_time = (time.time() - start_time) * 1000
        
        # 返回详细的错误响应
        error_response = CheckResponse(
            success=False,
            message=f"处理请求时发生错误: {str(e)}",
            is_empty=False,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            processing_time_ms=round(processing_time, 2)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@app.get("/api/empty")
async def return_empty_response():
    """
    返回空响应的端点
    
    返回:
    - Response: 空响应，状态码为 204 No Content
    
    使用场景：
    1. 测试客户端对空响应的处理
    2. 某些 API 可能不需要返回数据，只需要状态码
    3. 删除操作成功时常用
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============================================
# 异常处理器
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    HTTP 异常处理器
    
    参数:
    - request: 请求对象
    - exc: 异常对象
    
    返回:
    - JSONResponse: 包含错误信息的 JSON 响应
    
    这个处理器会捕获所有 HTTPException 异常，
    并返回结构化的错误响应
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    )


# ============================================
# 中间件示例（可选）
# ============================================

@app.middleware("http")
async def add_process_time_header(request, call_next):
    """
    添加处理时间头的中间件
    
    这个中间件会在每个请求中：
    1. 记录请求开始时间
    2. 调用下一个处理程序
    3. 在响应头中添加处理时间
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    # 添加自定义响应头
    response.headers["X-Process-Time"] = f"{process_time:.2f} ms"
    response.headers["X-Service"] = "Empty-Checker-API"
    
    return response


# ============================================
# 启动应用
# ============================================

if __name__ == "__main__":
    """
    直接运行时的启动代码
    
    使用 uvicorn 启动服务器：
    - host: 绑定地址，0.0.0.0 表示监听所有网络接口
    - port: 监听端口
    - reload: 开发时启用热重载
    
    启动命令：
    python main.py
    或
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    """
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,       # 监听端口
        reload=True      # 开发模式，代码修改后自动重启
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)