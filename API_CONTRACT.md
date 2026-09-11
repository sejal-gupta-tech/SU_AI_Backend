# SevenUnique AI - API Contract

## Base URL
`/api/v1`

---

## 🤖 AI Endpoints

### 1. Get Business AI Context
Retrieves the comprehensive business context (Business info, Brand Kit, Products) to be used by the AI.
- **Endpoint**: `GET /ai/context`
- **Authentication**: Required (JWT)
- **Response** (200 OK):
```json
{
    "business": {
        "name": "Sharma Fashion",
        "category": "Clothing",
        ...
    },
    "brand": {
        "tone": "Premium",
        "tagline": "Quality apparel",
        ...
    },
    "products": [
        {
            "id": "123",
            "name": "Premium Shirt",
            "price": 999,
            ...
        }
    ]
}
```

### 2. Generate Social Media Caption
Generates a structured caption, hashtags, and CTA based on product and context.
- **Endpoint**: `POST /ai/caption`
- **Authentication**: Required (JWT)
- **Request Body**:
```json
{
    "product_id": "product_obj_id_here",
    "objective": "sale",
    "tone": "premium",
    "language": "english",
    "offer": "20% OFF",
    "cta": "Shop Now"
}
```
- **Response** (200 OK):
```json
{
    "success": true,
    "message": "Caption generated successfully",
    "data": {
        "caption": "Experience premium quality... 🌟",
        "hashtags": ["#Fashion", "#PremiumQuality"],
        "cta": "Shop Now"
    }
}
```
- **Error Response** (400/500):
```json
{
    "success": false,
    "message": "AI generation failed. Please try again.",
    "error": {
        "code": "AI_GENERATION_FAILED"
    }
}
```

### 3. Get Generation History
Retrieve paginated list of AI generations for the authenticated user.
- **Endpoint**: `GET /ai/generations`
- **Authentication**: Required (JWT)
- **Query Params**:
  - `skip` (int, default=0)
  - `limit` (int, default=20)
- **Response** (200 OK):
```json
[
  {
    "id": "gen_id",
    "user_id": "user_id",
    "business_id": "business_id",
    "generation_type": "caption",
    "provider": "mock",
    "status": "success",
    "output_data": { ... },
    "execution_time_ms": 1005,
    "created_at": "2023-10-10T..."
  }
]
```

### 4. Get Specific Generation
- **Endpoint**: `GET /ai/generations/{generation_id}`
- **Authentication**: Required (JWT)
