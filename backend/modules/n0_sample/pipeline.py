import time
from typing import Any, Union

from config import setup_logging
from .config import EXAMPLE_CONFIG
setup_logging("N0")

from .schemas import N0SampleData, N0SampleInput, N0SampleMetadata, N0SampleOutput


def run_sample(data: Union[N0SampleInput, dict[str, Any]]) -> dict[str, Any]:
    """Normalize input and return the standard data/metadata envelope."""
    start_time = time.perf_counter()
    
    # 1. Enforce Input validation boundary
    input_data = N0SampleInput.model_validate(data) if isinstance(data, dict) else data
    
    # 2. Extract & simple cleaning
    text = input_data.text.strip()
    tags = [t.strip() for t in input_data.tags if t.strip()]
    
    # 3. Build & Enforce Output validation boundary using Pydantic objects directly
    output = N0SampleOutput(
        data=N0SampleData(text=text, tags=tags),
        metadata=N0SampleMetadata(
            module="n0_sample",
            latency_ms=round((time.perf_counter() - start_time) * 1000, 2)
        )
    )
    
    return output.model_dump()
