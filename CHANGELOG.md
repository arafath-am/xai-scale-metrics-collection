# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-29

### Added
- Complete Docker Compose stack for local testing and demos
- Mock DCGM exporter simulating realistic 8x H100 GPU metrics
- Pre-built Grafana dashboard with 10 visualization panels
- Comprehensive testing guide (TESTING.md) with scenarios and troubleshooting
- CI/CD pipeline with GitHub Actions (lint, test, build, validate)
- Kubernetes deployment manifests for all exporters
- systemd service files for bare-metal deployments
- Unit tests with pytest for cooling exporter
- Production-ready error handling and structured logging
- Health check endpoints with staleness monitoring

### Changed
- Refactored cooling exporter with graceful shutdown (SIGTERM/SIGINT)
- Enhanced target generator with argparse CLI and CSV validation
- Improved Prometheus metric naming conventions (celsius vs c)
- Updated documentation with production deployment guides

### Fixed
- Mermaid diagram syntax in README for GitHub rendering
- Docker health checks now use proper wget syntax
- Prometheus config validation in CI pipeline

## [0.2.0] - 2026-01-15

### Added
- Custom cooling plant exporter (REST/JSON → Prometheus format)
- Reference Prometheus configurations with cell-based sharding
- Cell-based architecture documentation (docs/)
- Multi-target exporter patterns for IPMI and SNMP
- Recording rules for GPU thermal rollups
- Cardinality management guidelines

### Changed
- Reorganized configs into prometheus/ subdirectory
- Split documentation into focused topic files

## [0.1.0] - 2025-12-10

### Added
- Initial project structure and architecture
- Design documentation for 200k GPU monitoring
- Sample inventory CSV schema
- Target generation tooling
- MIT License
- README with architecture overview
