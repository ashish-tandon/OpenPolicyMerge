# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Kubernetes-first deployment architecture
- Comprehensive smoke tests for dev, staging, and production
- Helm chart skeleton for advanced deployments
- Enhanced guardrails with RUN_PLAYBOOK procedures
- Service discovery via Kubernetes DNS
- ADR framework for architectural decisions

### Changed
- Updated .cursorrules for Kubernetes-first approach
- Enhanced RUN_PLAYBOOK with K8s validation steps
- Consolidated database strategy to single instance with schemas

### Fixed
- Smoke test coverage for all deployment environments
- Service health check endpoints standardization

## [0.1.0] - 2025-01-27

### Added
- Initial OpenPolicy platform architecture
- Scraper service infrastructure
- Database setup and configuration
- Basic service monitoring and health checks
