# Synthik Python Client

A thin, well-typed Python client for the Synthik Labs backend.

## Install (editable from repo)

```bash
pip install -e clients/python
```

## Usage

```python
from synthik import SynthikClient
from synthik.types import ColumnBuilder, DatasetGenerationRequest, TextDatasetGenerationRequest

client = SynthikClient()

# Tabular
req = DatasetGenerationRequest(
    num_rows=100,
    topic="User profiles",
    columns=[
        ColumnBuilder.string("full_name", description="User's full name").build(),
        ColumnBuilder.int("age", description="Age in years", constraints={"min": 18, "max": 90}).build(),
        ColumnBuilder.categorical("country", ["US", "CA", "GB"]).build(),
        ColumnBuilder.email().build(),
    ]
)
result = client.tabular.generate(req)
print(result["metadata"])  # when format=json

# Text
text_req = TextDatasetGenerationRequest(
    num_samples=10,
    task_definition="sentiment analysis",
    data_domain="e-commerce",
    data_description="product reviews",
    output_format="instruction",
)
text_data = client.text.generate(text_req)
print(text_data.metadata)
```
