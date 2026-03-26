---
paths:
  - "tests/**/*.py"
  - "**/*_test.py"
  - "**/*.test.py"
---

# Testing Rules

## Framework
- Use `pytest` — run with `uv run pytest`
- Put tests under `tests/` mirroring the source structure
- Test file: `tests/test_<module>.py`, test function: `test_<what>_<condition>()`

## Writing tests
- Each test must have exactly one logical assertion (multiple `assert` is ok if they test one concept)
- Use descriptive names: `test_cosine_similarity_returns_one_for_identical_vectors` not `test_sim`
- Fixtures go in `conftest.py` at the appropriate scope level
- Parametrize repeated test logic: `@pytest.mark.parametrize`

## API mocking
- Always mock OpenAI and other external API calls — use `pytest-mock` or `unittest.mock`
- Never make live API calls in tests (costs money, flaky, slow)
- Fixture for mocked client:
  ```python
  @pytest.fixture
  def mock_openai(mocker):
      return mocker.patch("openai.OpenAI")
  ```

## Coverage
- New features need tests before the PR merges
- Bug fixes must include a regression test that would have caught the bug

## Running
```bash
uv run pytest                          # all tests
uv run pytest tests/test_foo.py -v    # specific file, verbose
uv run pytest -k "similarity" -v      # tests matching keyword
uv run pytest --tb=short              # shorter tracebacks
```
