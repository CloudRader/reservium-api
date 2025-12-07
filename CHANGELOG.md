# Changelog

## [2.1.1](https://github.com/CloudRader/reservium-api/compare/v2.1.0...v2.1.1) (2025-12-07)


### 🧱 Updates & Improvements

* **tests:** full test coverage for crud layer + add more ruff rules + add generate release notes ([#114](https://github.com/CloudRader/reservium-api/issues/114)) ([48a1e76](https://github.com/CloudRader/reservium-api/commit/48a1e76ec03e29e11fff25d8c3d1e53c4418b446))


### 🛠️ Fixes

* **ci:** rules for trigger Build and Push image after merge PR for generated release not ([#116](https://github.com/CloudRader/reservium-api/issues/116)) ([fa217f9](https://github.com/CloudRader/reservium-api/commit/fa217f9bd393ca040e3d8dd2dd79238835081584))

## [2.1.0](https://github.com/CloudRader/reservium-api/compare/v2.0.0...v2.1.0) (2025-11-07)


### 🚀 Reservium Backend v2.1.0 — Code Quality & Dependency Update

A focused minor release that improves **code quality**, **test coverage**, and **CI/CD visibility**.  
This version introduces full test coverage for schemas and models layers, expanded Ruff rules, visual Codecov integration and **dependency upgrades**.


### ✨ Highlights

- 🧩 **Full coverage added for Schemas and Models layers** 
- 🔧 **Expanded Ruff rule set** for stricter code style and best practices  
- 🧱 **Refactored imports and RET/ERA rule fixes** across multiple modules  
- 🧩 **Moved Renovate configuration** under `.github` for cleaner repository structure  
- ⚙️ **Updated most of dependencies** to the latest stable versions 


### 🧹 Refactoring & Cleanup

- 🧹 Sorted `__all__` declarations in `__init__` modules  
- 🧹 Addressed `RET`, `ERA`, and `DTZ` warnings in Ruff configuration  
- 🧹 Improved static analysis results and enforced new linting standards  


### 🧪 CI/CD & Tooling

- ✅ Added **Codecov and Pipeline badges** to `README.md`  
- ✅ Improved **Ruff** and workflows with consistent checks  
- ✅ Maintained dependency automation via **Renovate**  
- ✅ Simplified coverage artifact uploads for easier inspection  


### 🏁 Summary

Reservium Backend **v2.1.0** enhances internal quality by improving structure, coverage, and CI visibility.  
Developers now benefit from improved linting, full schema/model validation coverage, and automatic Codecov reporting.


**Released:** 7 November 2025  
**Maintainer:** [DarkRader](mailto:artyom.20century@gmail.com)

## [2.0.0](https://github.com/CloudRader/reservium-api/compare/v1.0.0...v2.0.0) (2025-10-25)


### 🚀 Reservium Backend v2.0.0 — Major Update

A complete system refactor introducing a more modular structure, updated dependencies, strict versioning, and automated CI/CD with semantic versioning.


### ✨ New Features

- ✅ Added **Keycloak integration** for authentication and authorization  
- ✅ Introduced **JWT-based role and permission handling**
- ✅ Introduced **new event endpoints** with timelines and pagination  
- ✅ Added **automatic database migrations** at container startup  
- ✅ Added **email sending logic** and improved email templates  
- ✅ Added **GitHub Actions** for build, test, and Docker publishing  
- ✅ Added **semantic versioning (SemVer)** tagging and release workflow  
- ✅ Added **support for soft delete restore** and **hard delete** for reservation services  
- ✅ Added **manager registration forms** and **PDF generation**


### 🧱 Updates & Improvements

- ✴️ Updated dependencies and switched to **UV** environment management  
- ✴️ Updated and reorganized **Google Calendar integration**  
- ✴️ Improved event and reservation filtering, pagination, and performance  
- ✴️ Updated Pydantic schemas, naming conventions, and configuration settings  
- ✴️ Improved code formatting with **Ruff** (replacing Black and Pylint)  
- ✴️ Updated Docker and CI/CD pipelines for versioned builds  
- ✴️ Enhanced app logging in API layer


### 🧹 Refactoring

- 🧹 Major **codebase restructuring**: new folder layout (`core`, `integrations`, `api`)  
- 🧹 Migrated from IS authentication to Keycloak  
- 🧹 Unified exception handling, error mapping, and docstring consistency  
- 🧹 Simplified routers using **BaseCRUDRouter** and **Routers classes**  
- 🧹 Moved shared utilities, constants, and configuration to core modules  
- 🧹 Replaced UUID types with string identifiers across all models  
- 🧹 Introduced **strict dependency versioning** and refactored old scripts  


### 🛠️ Fixes

- 🛠️ Fixed multiple CI/CD pipeline issues (Docker builds, Mypy, Ruff)  
- 🛠️ Fixed role schemas, Alembic configs, and migration scripts  
- 🛠️ Fixed CORS configuration and environment variables  
- 🛠️ Fixed async database engine and SQLAlchemy 2.0 migration  
- 🛠️ Fixed login routes, permissions, and exception handling  
- 🛠️ Fixed event/reservation relationships, API responses, and timezone handling  
- 🛠️ Fixed dependency mismatches after major refactor  


### ❌ Removed / Deprecated

- ❌ Removed IS authentication  
- ❌ Removed old Pylint and Black setup  
- ❌ Deprecated old router and schema structures  


### 🧪 Tests & Quality

- ✅ Added linting and formatting checks to CI  


### ⚙️ DevOps & CI/CD

- ✅ Introduced automated **SemVer tagging** and image versioning  
- ✅ Added **Docker Hub** publishing workflow  
- ✅ Set up **test matrix** for Mypy and Pytest jobs  


### 🏁 Summary

Reservium v2.0.0 marks a **major milestone** in the project:

- Modernized backend architecture  
- Unified CI/CD pipelines  
- Introduced scalable authentication and permissions  
- Ensured maintainability through stricter structure and linting  


**Released:** 25 October 2025  
**Maintainer:** [DarkRader](mailto:artyom.20century@gmail.com)