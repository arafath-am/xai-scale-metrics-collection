# Contributing to xAI-Scale Metrics Collection

Thanks for your interest in contributing! This is a reference architecture project demonstrating production-grade monitoring for large-scale GPU datacenters.

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/arafath-am/xai-scale-metrics-collection.git
cd xai-scale-metrics-collection

# Start the demo stack
docker-compose up -d

# Access interfaces
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
# Cooling Exporter: http://localhost:8000/metrics
# Mock DCGM: http://localhost:9400/metrics

# Run tests
cd exporters/cooling_rest_exporter
pip install -r requirements.txt
pytest test_app.py -v
```

## Development Workflow

### 1. Fork and Clone
```bash
# Fork the repo on GitHub
git clone https://github.com/YOUR_USERNAME/xai-scale-metrics-collection.git
cd xai-scale-metrics-collection
git remote add upstream https://github.com/arafath-am/xai-scale-metrics-collection.git
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes
- Write clear, concise code with proper error handling
- Add unit tests for new functionality
- Update documentation (README, TESTING.md) if needed
- Follow existing code style and conventions

### 4. Test Your Changes
```bash
# Run unit tests
cd exporters/cooling_rest_exporter
pytest test_app.py -v --cov=app

# Validate Prometheus configs
promtool check config configs/prometheus/cell-prometheus.yml

# Test Docker build
docker build -t test-exporter exporters/cooling_rest_exporter/

# Test full stack
docker-compose up -d
docker-compose logs
```

### 5. Commit Your Changes
```bash
git add .
git commit -m "feat: add new feature description"
```

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 6. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub with:
- Clear description of what changed and why
- Reference any related issues
- Screenshots if UI/dashboard changes

## Code Style Guidelines

### Python
- Follow PEP 8 style guide
- Use `black` for auto-formatting: `black exporters/`
- Use `flake8` for linting: `flake8 exporters/ --max-line-length=100`
- Type hints encouraged for function signatures
- Docstrings for modules and functions

### YAML
- 2-space indentation
- Use `---` document separator
- Quote strings with special characters
- Validate with `yamllint` before committing

### Prometheus Configs
- Use consistent label naming (snake_case)
- Document non-obvious relabeling rules
- Validate with `promtool check config`

### Commit Messages
- Use present tense ("Add feature" not "Added feature")
- Be specific and concise
- Reference issues: `fix: resolve DCGM timeout (#123)`

## Testing Requirements

All code changes must include appropriate tests:

### Unit Tests
```python
# Example test structure
def test_fetch_data_success(mock_payload):
    """Test successful data fetch from API."""
    data = fetch_data()
    assert data == mock_payload

def test_update_gauges_handles_empty():
    """Test graceful handling of empty payloads."""
    update_gauges({})  # Should not raise
```

### Integration Tests
- Docker Compose stack must start without errors
- All exporters must respond to `/metrics` endpoint
- Health checks must pass

### CI/CD
All PRs must pass:
- Linting (flake8, black)
- Unit tests with coverage
- Prometheus config validation
- Docker build

## Documentation

Update documentation when:
- Adding new features or exporters
- Changing deployment procedures
- Modifying configuration patterns
- Adding new dependencies

Documentation locations:
- `README.md` - Overview and quick start
- `TESTING.md` - Local testing and development
- `docs/` - Architecture and design decisions
- `exporters/*/README.md` - Exporter-specific docs

## Adding New Exporters

When contributing a new exporter:

1. **Create directory**: `exporters/your_exporter/`
2. **Required files**:
   - `app.py` - Main exporter code
   - `Dockerfile` - Container build
   - `requirements.txt` - Python dependencies
   - `README.md` - Usage and configuration
   - `test_app.py` - Unit tests
3. **Optional but recommended**:
   - `k8s-deployment.yaml` - Kubernetes manifest
   - `*.service` - systemd service file
   - `docker-compose.yml` - Standalone testing

4. **Integration**:
   - Add to main `docker-compose.yml`
   - Add sample scrape config to `demo/prometheus.yml`
   - Update main `README.md` with description

## Questions or Issues?

- **Bugs**: Open an issue with the bug report template
- **Features**: Open an issue with the feature request template
- **Questions**: Start a discussion in the Discussions tab
- **Security**: Email security@example.com (do not open public issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be acknowledged in the README and release notes. Thank you for helping make this project better!
