from typing import Dict, Any, Optional
from pydantic import Field
from app.models.base import MongoBaseModel

class AIGenerationHistory(MongoBaseModel):
    user_id: str
    business_id: str
    generation_type: str
    provider: str
    model_name: str
    input_params: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str  # 'pending', 'processing', 'success', 'failed'
    execution_time_ms: int = 0
    error_message: Optional[str] = None
