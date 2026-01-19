# GetFast
get the new Fast


# FastAPI 空响应检查服务

## 功能描述
这是一个简单的 FastAPI 服务，用于检查 API 响应是否为空。

run with command : uvicorn main:app --reload
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

## 主要特性
- 检查各种类型的空数据（None, 空字符串, 空列表等）
- 支持模拟超时测试
- 完整的错误处理
- 自动生成 API 文档
- 健康检查端点

## API 端点

### 1. 服务信息
GET /

### 2. 健康检查
GET /api/health

### 3. 检查空响应（主端点）
POST /api/check-empty
**请求体示例：**
```json
{
  "data": null,
  "check_empty": true,
  "timeout": 1000
}
‘’‘

GET /api/empty