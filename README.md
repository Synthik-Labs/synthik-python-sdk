# Synthik Python Client

A thin, well-typed Python client for the Synthik Labs backend.

## Install (editable from repo)

```bash
pip install synthik-client
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
```

## Quick Start

```python
from synthik import SynthikClient
from synthik.types import ColumnBuilder, DatasetGenerationRequest, TextDatasetGenerationRequest

client = SynthikClient(api_version="v2", api_key="YOUR_API_KEY")

tabular_req = DatasetGenerationRequest(
    num_rows=100,
    topic="User profiles",
    columns=[
        ColumnBuilder.string("full_name", description="User's full name").build(),
        ColumnBuilder.int("age", description="Age in years", constraints={"min": 18, "max": 90}).build(),
        ColumnBuilder.categorical("country", ["US", "CA", "GB"]).build(),
        ColumnBuilder.email().build(),
    ],
    seed=42,
)

tabular_json = client.tabular.generate(tabular_req, strategy="adaptive_flow", format="json", batch_size=256)
print(tabular_json["metadata"])  # when format=json

text_req = TextDatasetGenerationRequest(
    num_samples=10,
    task_definition="sentiment analysis",
    data_domain="e-commerce",
    data_description="product reviews",
    output_format="instruction",
    sample_examples=[{"instruction": "Classify sentiment", "input": "Love it", "output": "positive"}],
)
text_dataset = client.text.generate(text_req)
print(text_dataset.metadata)
```
**NOTE**: Replace `"YOUR_API_KEY"` with your actual API key is your access token, which is generated upon login.

---

## API Versioning

Set `api_version="v2"` to use the latest endpoints. Explicit `v1_*/v2_*` methods (e.g. `v2_generate`) are available; using `v1_*` will emit deprecation warnings.

## Tabular Module

| Method                                             | Description                                                   |
| -------------------------------------------------- | ------------------------------------------------------------- |
| `generate(req, strategy?, format?, batch_size?)` | Unified generate (formats: json, csv, parquet, arrow, excel). |
| `v1_generate / v2_generate`                      | Explicit versioned helpers (v1 deprecated).                   |
| `strategies()`                                   | List available generation strategies.                         |
| `analyze(req)`                                   | Pre-flight schema/topic analysis.                             |
| `validate(data, columns)`                        | Validate rows against a schema.                               |
| `status()`                                       | Service / model readiness info.                               |

### CSV Export

```python
csv_bytes = client.tabular.generate(tabular_req, format="csv")
with open("synthetic.csv", "wb") as f:
    f.write(csv_bytes)
```

### Analyze & Strategies

```python
analysis = client.tabular.analyze(tabular_req)
available = client.tabular.strategies()
print(available["strategies"])  # list of strategies
```

### Validation

```python
rows = tabular_json["data"]  # when format=json
schema_cols = [vars(c) for c in tabular_req.columns]
validation = client.tabular.validate(rows, schema_cols)
print(validation)
```

## Text Module

| Method                        | Description                                    |
| ----------------------------- | ---------------------------------------------- |
| `generate(req)`             | Unified text dataset generation.               |
| `v1_generate / v2_generate` | Explicit versioned helpers.                    |
| `info()`                    | Model/capability info (works across versions). |
| `validate(req)`             | Validate request without generating.           |
| `examples()`                | Example tasks/prompts.                         |

## Auth Module

Access via `client.auth`.

| Method                                                        | Description                                     |
| ------------------------------------------------------------- | ----------------------------------------------- |
| `register(email, password)`                                 | Create an account (version dispatched).         |
| `login(email, password)`                                    | Obtain an auth token.                           |
| `validate_token(token)`                                     | Validate a token (override header if provided). |
| `list_tokens(include_revoked=False, include_expired=False)` | List tokens.                                    |
| `revoke(token)`                                             | Revoke by raw token.                            |
| `revoke_by_id(token_id)`                                    | Revoke by numeric id.                           |
| `me()`                                                      | Current user profile.                           |

### Auth Example

```python
auth_res = client.auth.login("user@example.com", "password123")
print(auth_res)
valid = client.auth.validate_token(auth_res.get("token"))
print(valid)
```

## Column Builder

```python
title_col = (ColumnBuilder.string("title", description="Article title", max_length=120)
             .constrain("regex", r"^[A-Z].+")
             .samples(["Hello World", "A Great Day"])  # optional examples
             .build())
```

Static constructors: `string`, `int`, `float`, `categorical`, `email`, `uuid`.

## Text Request Notes

`output_format` one of: `instruction`, `conversation`, `json`.
Provide `sample_examples` to steer structure/style.

## Error Handling

HTTP errors raise exceptions; wrap calls as needed:

```python
try:
    data = client.tabular.generate(tabular_req)
except Exception as e:  # Replace with granular error type when exposed
    print("Generation failed:", e)
```

## Migration (v1 → v2)

1. Instantiate client with `api_version="v2"`.
2. Replace any explicit `v1_*` calls with unified or `v2_*` counterparts.
3. Regenerate datasets if you rely on strategy semantics improved in v2.

## License

See repository root for license information.
