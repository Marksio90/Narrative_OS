# Agent Collaboration System - Tests 🧪

Comprehensive test suite for the Agent Collaboration System.

## 📊 Test Statistics

**Total Tests: 148**

- **Unit Tests**: 111
  - AgentOrchestrationService: 35 tests
  - AgentMemoryService: 47 tests
  - Specialized Agents: 29 tests

- **Integration Tests**: 37
  - Agent Management API: 8 tests
  - Task Management API: 11 tests
  - Conversation API: 7 tests
  - Memory API: 6 tests
  - Project Statistics API: 1 test
  - Additional Integration: 4 tests

## 🏗️ Test Structure

```
tests/
├── conftest.py                    # Fixtures and test configuration
├── test_orchestration_service.py  # AgentOrchestrationService unit tests
├── test_memory_service.py         # AgentMemoryService unit tests
├── test_specialized_agents.py     # Specialized agent implementation tests
└── test_api_integration.py        # API endpoint integration tests
```

## 🚀 Running Tests

### Install Dependencies
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=backend --cov-report=html
```

### Run Specific Test Types

**Unit Tests Only:**
```bash
pytest -m unit
```

**Integration Tests Only:**
```bash
pytest -m integration
```

**Agent-Related Tests:**
```bash
pytest -m agent
```

**Memory Tests:**
```bash
pytest -m memory
```

**Task Tests:**
```bash
pytest -m task
```

### Run Specific Test File
```bash
pytest tests/test_orchestration_service.py
pytest tests/test_memory_service.py
pytest tests/test_specialized_agents.py
pytest tests/test_api_integration.py
```

### Run Specific Test
```bash
pytest tests/test_orchestration_service.py::test_create_task_basic
pytest tests/test_memory_service.py::test_search_memories_basic
```

### Verbose Output
```bash
pytest -v
```

### Show Print Statements
```bash
pytest -s
```

## 📝 Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.agent` - Agent-related tests
- `@pytest.mark.memory` - Memory system tests
- `@pytest.mark.task` - Task management tests
- `@pytest.mark.conversation` - Conversation tests
- `@pytest.mark.slow` - Slow-running tests

## 🔧 Test Fixtures

Key fixtures defined in `conftest.py`:

### Database Fixtures
- `db_engine` - In-memory SQLite test database
- `db_session` - Database session for tests
- `test_client` - FastAPI test client

### Model Fixtures
- `test_project` - Sample project
- `test_agents` - 3 test agents (plotting, character, dialogue)
- `test_tasks` - 4 test tasks with various statuses
- `test_conversation` - Sample conversation
- `test_messages` - Sample messages
- `test_memories` - Sample memories
- `test_character` - Sample character
- `test_chapter` - Sample chapter

### Service Fixtures
- `orchestration_service` - AgentOrchestrationService instance
- `memory_service` - AgentMemoryService instance

### Data Fixtures
- `sample_task_data` - Template task data
- `sample_agent_data` - Template agent data
- `sample_memory_data` - Template memory data

## ✅ Test Coverage

Current coverage targets:

- **AgentOrchestrationService**: ~90%
  - Task creation (single & batch)
  - Task assignment (manual & auto)
  - Agent scoring algorithm
  - Task lifecycle (start, complete, fail)
  - Dependency management
  - Queue management
  - Statistics

- **AgentMemoryService**: ~95%
  - Memory creation (all types)
  - Memory retrieval & filtering
  - Semantic search
  - Memory decay
  - Memory consolidation
  - Statistics
  - Embedding utilities

- **Specialized Agents**: ~85%
  - PlottingAgent: Plot analysis, pacing
  - CharacterAgent: Character development
  - DialogueAgent: Dialogue review
  - ContinuityAgent: Continuity checking
  - QCAgent: Quality control
  - AgentFactory: Agent instantiation

- **API Endpoints**: ~80%
  - Agent management (CRUD + statistics)
  - Task management (CRUD + lifecycle)
  - Conversation management (create, messages, voting)
  - Memory management (CRUD + search)
  - Project statistics

## 🐛 Common Issues

### Database Errors
If you see "table already exists" errors:
```bash
# Clear test database (if using persistent DB)
rm test.db
```

### Import Errors
Make sure backend is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

### Fixture Not Found
Ensure `conftest.py` is in the tests directory and properly loaded.

## 📈 Adding New Tests

### Test File Template
```python
import pytest
from backend.core.models import YourModel

@pytest.mark.unit
def test_your_function(db_session, test_project):
    # Arrange
    expected = "value"

    # Act
    result = your_function(test_project.id)

    # Assert
    assert result == expected
```

### Integration Test Template
```python
@pytest.mark.integration
def test_your_endpoint(test_client, test_project):
    response = test_client.post(
        f"/api/projects/{test_project.id}/your-endpoint",
        json={"key": "value"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "value"
```

## 🎯 Testing Best Practices

1. **One assertion per test** (when possible)
2. **Use descriptive test names** (`test_what_when_then`)
3. **Arrange-Act-Assert pattern**
4. **Use fixtures for setup**
5. **Mark tests appropriately** (`@pytest.mark.unit`)
6. **Mock external dependencies**
7. **Test edge cases and error conditions**
8. **Keep tests independent**

## 📊 Coverage Reports

After running tests with coverage:
```bash
pytest --cov=backend --cov-report=html
```

Open the report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🔄 Continuous Integration

Tests should be run in CI/CD pipeline:
```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=backend --cov-report=xml
```

## 📚 Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)

---

**Happy Testing!** 🧪✨
