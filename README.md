# Codle Translate

A python based code translator with a simple GUI

## Quick Start

> [!IMPORTANT]
> python 3.13.x must be installed for this to run

Make sure poetry is installed on system using `pip install poetry` or `pipx install poetry` depending on your system.

```bash
poetry sync
poetry run gui
```

## Testing

Run all tests with verbose logging:
`poetry run test`

Run a specific class:
`poetry run pytest tests/test.py::TestNormalize -v`

Run a specific test:
`pytest tests/test.py::TestIRParser::test_js_for_loop -vt`
