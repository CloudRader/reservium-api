# Changelog

## [2.3.1](https://github.com/CloudRader/reservium-api/compare/v2.3.0...v2.3.1) (2026-04-10)


### 🧱 Updates & Improvements

* **deps:** update dependency astral-sh/uv to v0.11.6 ([#190](https://github.com/CloudRader/reservium-api/issues/190)) ([a03b28c](https://github.com/CloudRader/reservium-api/commit/a03b28c16049569c7d741649dcee3e24b419bfa2))
* **deps:** update dependency pytest to v9.0.3 ([#189](https://github.com/CloudRader/reservium-api/issues/189)) ([2a43625](https://github.com/CloudRader/reservium-api/commit/2a43625ea49cc395f09b400724a69f1d9db66a14))
* **deps:** update dependency ruff to v0.15.10 ([#192](https://github.com/CloudRader/reservium-api/issues/192)) ([b85fe88](https://github.com/CloudRader/reservium-api/commit/b85fe88fbf0870a7ae8a9ec60ca90878b03d5721))
* **deps:** update dependency types-python-dateutil to v2.9.0.20260408 ([#193](https://github.com/CloudRader/reservium-api/issues/193)) ([b9d465f](https://github.com/CloudRader/reservium-api/commit/b9d465fd3b87e2ab24c2cead3b6430acbcde571f))
* **deps:** update dependency types-pytz to v2026.1.1.20260408 ([#194](https://github.com/CloudRader/reservium-api/issues/194)) ([47eedb7](https://github.com/CloudRader/reservium-api/commit/47eedb7a91a00f15cb07314fac78db09121af0ef))
* **google-calendar:** introduce async-safe executor using thread pool ([df24abe](https://github.com/CloudRader/reservium-api/commit/df24abeef39b3c1690f9f8f57f2e9236c5cdb225))
* **patch:** refactor api and services layer, do calendar integration non-blocking call, update dependencies ([#197](https://github.com/CloudRader/reservium-api/issues/197)) ([8598c22](https://github.com/CloudRader/reservium-api/commit/8598c22aaced645aeda209e99efd62ee7e822e17))


### 🛠️ Fixes

* **deps:** update dependency google-api-python-client to v2.194.0 ([#195](https://github.com/CloudRader/reservium-api/issues/195)) ([1777583](https://github.com/CloudRader/reservium-api/commit/177758346614642fe0f0be81f618d3f962c6801e))
* **deps:** update dependency jwcrypto to v1.5.7 ([#188](https://github.com/CloudRader/reservium-api/issues/188)) ([76d7afa](https://github.com/CloudRader/reservium-api/commit/76d7afa346cebc6b82374320f0566458d947dde4))
* **deps:** update dependency uvicorn to v0.44.0 ([#187](https://github.com/CloudRader/reservium-api/issues/187)) ([0d5aa9c](https://github.com/CloudRader/reservium-api/commit/0d5aa9c19150f0afde3c97a678035b2a75e21141))
* **events:** return with await approve_update_reservation_time ([046ab6c](https://github.com/CloudRader/reservium-api/commit/046ab6c0f595fa960a8b567a1e994608b63e2622))
* **events:** tmp fix for retrieve event with proper relations load ([77049c3](https://github.com/CloudRader/reservium-api/commit/77049c3a5224941bdde0042ccc6e72047e0d6be7))


### 🧹 Refactors

* move calendar, events and emails api layer business logic to services layer ([#191](https://github.com/CloudRader/reservium-api/issues/191)) ([dda313f](https://github.com/CloudRader/reservium-api/commit/dda313fb60bfb7ace73fd9cb24b3e6e6f7768285))

## [2.3.0](https://github.com/CloudRader/reservium-api/compare/v2.2.0...v2.3.0) (2026-04-04)


### ✨ New Features

* update deps, fix bugs ([#184](https://github.com/CloudRader/reservium-api/issues/184)) ([412ed89](https://github.com/CloudRader/reservium-api/commit/412ed89d3a1203b65776ac4ad506664064247944))


### 🧱 Updates & Improvements

* add .zed folder to .gitignore ([d4e654d](https://github.com/CloudRader/reservium-api/commit/d4e654d241b4e70d286f29d4df40d89900b19562))
* **deps:** update codecov/codecov-action action to v6 ([#178](https://github.com/CloudRader/reservium-api/issues/178)) ([bf2909c](https://github.com/CloudRader/reservium-api/commit/bf2909ce7373e2c3b87f616847fda223726185af))
* **deps:** update dependency astral-sh/uv to v0.10.2 ([#147](https://github.com/CloudRader/reservium-api/issues/147)) ([788f75e](https://github.com/CloudRader/reservium-api/commit/788f75eef7e5a8dd8444b78934eb41c2a5ec28f9))
* **deps:** update dependency astral-sh/uv to v0.11.3 ([#169](https://github.com/CloudRader/reservium-api/issues/169)) ([eda2d2b](https://github.com/CloudRader/reservium-api/commit/eda2d2be7a875a14749c2b099bce38af5eda20dd))
* **deps:** update dependency astral-sh/uv to v0.9.22 ([#140](https://github.com/CloudRader/reservium-api/issues/140)) ([c66b7ba](https://github.com/CloudRader/reservium-api/commit/c66b7baa95caf96fa2b54c5463b5a91de14ff21d))
* **deps:** update dependency astral-sh/uv to v0.9.24 ([#145](https://github.com/CloudRader/reservium-api/issues/145)) ([a130235](https://github.com/CloudRader/reservium-api/commit/a130235babd2a61963e1cf11e45c2885f97df62c))
* **deps:** update dependency mypy to v1.20.0 ([#170](https://github.com/CloudRader/reservium-api/issues/170)) ([d21e4cb](https://github.com/CloudRader/reservium-api/commit/d21e4cbb9accfc65a4cefd6a27d23e8b3a8046e7))
* **deps:** update dependency pytest-cov to v7.1.0 ([#171](https://github.com/CloudRader/reservium-api/issues/171)) ([4f30ed0](https://github.com/CloudRader/reservium-api/commit/4f30ed0a6a53eff213c9e4c9607f85e66300e2eb))
* **deps:** update dependency pytest-env to v1.6.0 ([#160](https://github.com/CloudRader/reservium-api/issues/160)) ([ee39423](https://github.com/CloudRader/reservium-api/commit/ee3942306e3e2d6b8cd6420b4f51020d12773438))
* **deps:** update dependency ruff to v0.14.11 ([#142](https://github.com/CloudRader/reservium-api/issues/142)) ([2e5ed21](https://github.com/CloudRader/reservium-api/commit/2e5ed21f14c0503c739c8e6608d255bced7302b3))
* **deps:** update dependency testcontainers to v4.14.0 ([#141](https://github.com/CloudRader/reservium-api/issues/141)) ([0552a80](https://github.com/CloudRader/reservium-api/commit/0552a80836d696a8c2d38271118f243fd32e9ea5))
* **deps:** update dependency testcontainers to v4.14.1 ([#152](https://github.com/CloudRader/reservium-api/issues/152)) ([740e04c](https://github.com/CloudRader/reservium-api/commit/740e04c0abf783289d98138f8df87fd98923755e))
* **deps:** update dependency testcontainers to v4.14.2 ([#163](https://github.com/CloudRader/reservium-api/issues/163)) ([2569547](https://github.com/CloudRader/reservium-api/commit/256954779941e405dd7c6eb0715180de5f6d6dd6))
* **deps:** update dependency types-python-dateutil to v2.9.0.20260124 ([#153](https://github.com/CloudRader/reservium-api/issues/153)) ([969951d](https://github.com/CloudRader/reservium-api/commit/969951ddf5033b2f69752e418890f672af90402f))
* **deps:** update dependency types-python-dateutil to v2.9.0.20260402 ([#164](https://github.com/CloudRader/reservium-api/issues/164)) ([72b67c5](https://github.com/CloudRader/reservium-api/commit/72b67c57ded8b876d97f091842da84b61945cffc))
* **deps:** update dependency types-pytz to v2026 ([#180](https://github.com/CloudRader/reservium-api/issues/180)) ([751a3be](https://github.com/CloudRader/reservium-api/commit/751a3beaaccbb34aad24d06f5b2accffe54c482b))
* **deps:** update docker/login-action action to v4 ([#181](https://github.com/CloudRader/reservium-api/issues/181)) ([189bba7](https://github.com/CloudRader/reservium-api/commit/189bba724600aac910e37f61d1a1211c866e73d8))
* **deps:** update docker/setup-buildx-action action to v4 ([#182](https://github.com/CloudRader/reservium-api/issues/182)) ([022809c](https://github.com/CloudRader/reservium-api/commit/022809ca0f6c4398a9c3d994029cb362f827ebbb))
* remove gunicorn from everywhere ([bcb034e](https://github.com/CloudRader/reservium-api/commit/bcb034e0d60c1a8ededdba238cbeaae21442ffde))
* remove orjson (Deprecated) ([26726d3](https://github.com/CloudRader/reservium-api/commit/26726d3f5c2af09fc9fff7121cae7d902b9cbbc4))


### 🛠️ Fixes

* blocking code to async and race condition after background task ([8ead512](https://github.com/CloudRader/reservium-api/commit/8ead5124a79044cc3eca232ce2b5c4cecd8e8bd6))
* **deps:** update dependency aiohttp to v3.13.3 [security] ([#139](https://github.com/CloudRader/reservium-api/issues/139)) ([932b936](https://github.com/CloudRader/reservium-api/commit/932b9364445f39edb5e78dddbce8d5d845f3f37f))
* **deps:** update dependency aiohttp to v3.13.4 [security] ([#162](https://github.com/CloudRader/reservium-api/issues/162)) ([45c776d](https://github.com/CloudRader/reservium-api/commit/45c776da5dd9208208f9133443eb3492a89f589e))
* **deps:** update dependency aiohttp to v3.13.5 ([#165](https://github.com/CloudRader/reservium-api/issues/165)) ([fa269d7](https://github.com/CloudRader/reservium-api/commit/fa269d7e95cbc4482d5376969abfcf83c259efe7))
* **deps:** update dependency alembic to v1.18.0 ([#146](https://github.com/CloudRader/reservium-api/issues/146)) ([f7a3814](https://github.com/CloudRader/reservium-api/commit/f7a38149e654dbbc8beccf8d9ed8faae3a401c07))
* **deps:** update dependency alembic to v1.18.4 ([#149](https://github.com/CloudRader/reservium-api/issues/149)) ([80aa479](https://github.com/CloudRader/reservium-api/commit/80aa4792462bd9f77c3a5e2f16a8e6639b16a6c6))
* **deps:** update dependency authzed to v1.24.2 ([#154](https://github.com/CloudRader/reservium-api/issues/154)) ([80796cf](https://github.com/CloudRader/reservium-api/commit/80796cf1edcf76abd42878c05d486176459dbb9b))
* **deps:** update dependency authzed to v1.24.4 ([#166](https://github.com/CloudRader/reservium-api/issues/166)) ([e037c11](https://github.com/CloudRader/reservium-api/commit/e037c11827bb42457de9f0a287d0aeaab7db4ad0))
* **deps:** update dependency fastapi to v0.135.3 ([#155](https://github.com/CloudRader/reservium-api/issues/155)) ([7d00f46](https://github.com/CloudRader/reservium-api/commit/7d00f46ad2d0c8e0b34c3ba01afc759aa2f999ea))
* **deps:** update dependency fastapi-mail to v1.6.2 ([#167](https://github.com/CloudRader/reservium-api/issues/167)) ([74dd431](https://github.com/CloudRader/reservium-api/commit/74dd43181fc9691d9362ad2f7d8c56193df1e2dd))
* **deps:** update dependency google-api-python-client to v2.189.0 ([#148](https://github.com/CloudRader/reservium-api/issues/148)) ([54b6a74](https://github.com/CloudRader/reservium-api/commit/54b6a74047e3a523335771434e61cab5fe9d55db))
* **deps:** update dependency google-api-python-client to v2.193.0 ([#172](https://github.com/CloudRader/reservium-api/issues/172)) ([2856b77](https://github.com/CloudRader/reservium-api/commit/2856b77bce333383253888ae22ad332255749acc))
* **deps:** update dependency google-auth-oauthlib to v1.2.4 ([#156](https://github.com/CloudRader/reservium-api/issues/156)) ([c2438e6](https://github.com/CloudRader/reservium-api/commit/c2438e66062d8aae9183eb2d05999f998b81dda5))
* **deps:** update dependency google-auth-oauthlib to v1.3.1 ([#173](https://github.com/CloudRader/reservium-api/issues/173)) ([82378f4](https://github.com/CloudRader/reservium-api/commit/82378f4bca0ee4cc7d24008e57460d28fc196dac))
* **deps:** update dependency orjson to v3.11.7 ([#157](https://github.com/CloudRader/reservium-api/issues/157)) ([8094836](https://github.com/CloudRader/reservium-api/commit/809483648f94e166793b02d497761afb2f5d670b))
* **deps:** update dependency pydantic-settings to v2.13.1 ([#174](https://github.com/CloudRader/reservium-api/issues/174)) ([135cffe](https://github.com/CloudRader/reservium-api/commit/135cffe939cc3835fcb37955a85043fc8ff4eaae))
* **deps:** update dependency pypdf to v6.6.0 [security] ([#144](https://github.com/CloudRader/reservium-api/issues/144)) ([e8bb0b0](https://github.com/CloudRader/reservium-api/commit/e8bb0b01ce903a14cf2118e1fb14514a611326ff))
* **deps:** update dependency pypdf to v6.6.2 [security] ([#151](https://github.com/CloudRader/reservium-api/issues/151)) ([472eb3d](https://github.com/CloudRader/reservium-api/commit/472eb3dea4898b5b9b720bfce3064c75332b0da7))
* **deps:** update dependency pypdf to v6.9.2 [security] ([#161](https://github.com/CloudRader/reservium-api/issues/161)) ([d4470e9](https://github.com/CloudRader/reservium-api/commit/d4470e9fd520032ff8fd46eb6a0c189d6895a78d))
* **deps:** update dependency python-keycloak to v7 ([#138](https://github.com/CloudRader/reservium-api/issues/138)) ([eb4bced](https://github.com/CloudRader/reservium-api/commit/eb4bced8768ffc8f102baad929349af676823b88))
* **deps:** update dependency python-keycloak to v7.0.3 ([#158](https://github.com/CloudRader/reservium-api/issues/158)) ([976efd9](https://github.com/CloudRader/reservium-api/commit/976efd945bef42bef45b3453933ba950161255b3))
* **deps:** update dependency python-keycloak to v7.1.1 ([#175](https://github.com/CloudRader/reservium-api/issues/175)) ([fff502d](https://github.com/CloudRader/reservium-api/commit/fff502dce9271e664d35f922a750bada57dafcb0))
* **deps:** update dependency pytz to v2026 ([#183](https://github.com/CloudRader/reservium-api/issues/183)) ([d925ead](https://github.com/CloudRader/reservium-api/commit/d925ead7d398457338dc5b1e24044c46348b0cf0))
* **deps:** update dependency sqlalchemy to v2.0.49 ([#159](https://github.com/CloudRader/reservium-api/issues/159)) ([9073493](https://github.com/CloudRader/reservium-api/commit/90734934e23e9b8c76ccb54cfa17b6312485b26b))
* **deps:** update dependency sqlalchemy-easy-softdelete to v0.9.0 ([#176](https://github.com/CloudRader/reservium-api/issues/176)) ([6c18955](https://github.com/CloudRader/reservium-api/commit/6c18955283ae45bd0cfac1afdd617797d8abe5de))
* **deps:** update dependency uvicorn to v0.43.0 ([#177](https://github.com/CloudRader/reservium-api/issues/177)) ([56a49ca](https://github.com/CloudRader/reservium-api/commit/56a49ca34b95e499e88c5a33b0a86aac9e49e120))
* remove guvicorn from main ([84627d0](https://github.com/CloudRader/reservium-api/commit/84627d05ff49ea3b7d0fb406c31f024acb405424))
* update collision_ids in calendar ([23b09de](https://github.com/CloudRader/reservium-api/commit/23b09de970f6ae677a74344be4a10a85eacf04be))


### 🧹 Refactors

* rename docker-composes to compose ([c674e39](https://github.com/CloudRader/reservium-api/commit/c674e3901d5498678560b3b296a548f10911d84e))

## [2.2.0](https://github.com/CloudRader/reservium-api/compare/v2.1.1...v2.2.0) (2026-01-01)


### ✨ New Features

* **deps:** upgrade python from 3.12 to 3.13 ([#132](https://github.com/CloudRader/reservium-api/issues/132)) ([d53ec6e](https://github.com/CloudRader/reservium-api/commit/d53ec6ecee1cf2f702560a2054a2a79dfa30e815))


### 🛠️ Fixes

* **event:** show reservation creator in Google Calendar instead of last updater when update ([#134](https://github.com/CloudRader/reservium-api/issues/134)) ([5de6b5b](https://github.com/CloudRader/reservium-api/commit/5de6b5ba50f6397cbd15e5b5929be954e01aa829))

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
