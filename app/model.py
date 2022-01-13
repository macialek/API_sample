from pydantic import BaseModel, Field

class SampleAnswer(BaseModel):
    answer: str = Field(description="Sample answer")
    param_received: str = Field(description="Param received during request")

class SampleInput(BaseModel):
    input_text: str = Field(description="Some sample input text")

class HealthCheck(BaseModel):
    status: str = Field(description="Server status")
    up_since: str = Field(description="Server initialization time in UTC")
    uptime: str = Field(description="Server running time")
