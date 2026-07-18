# Changelog

## [2.4.4](https://github.com/CloudRader/reservium-api/compare/v2.4.3...v2.4.4) (2026-07-18)


### ♻️ Updates & Improvements

* **access_system:** removed service ([8600f5c](https://github.com/CloudRader/reservium-api/commit/8600f5ca3fbddbc1d76b17fd391a920ddc4cff54))
* add Makefile for automatisation ([eb0374b](https://github.com/CloudRader/reservium-api/commit/eb0374bafb4676623be27ad3b073e6ce0fb96154))
* **compose:** add name of application and update services names ([c722ef8](https://github.com/CloudRader/reservium-api/commit/c722ef865e79142827b19a649c17b2e3e66c66d4))
* **dependencies:** add di in api for all services and providers ([4913419](https://github.com/CloudRader/reservium-api/commit/4913419685861b71c7aecab7f6b530d141e10d72))
* **dependency-injection:** add container for DI, refactor services ([a7b163f](https://github.com/CloudRader/reservium-api/commit/a7b163f307efee4023841cd7182d2605ed53653f))
* **deps:** update astral-sh/setup-uv action to v8.3.0 ([#353](https://github.com/CloudRader/reservium-api/issues/353)) ([bfb7f93](https://github.com/CloudRader/reservium-api/commit/bfb7f9364c84101efe6ef79b0c5df0db9fabd91e))
* **deps:** update astral-sh/setup-uv action to v8.3.1 ([#359](https://github.com/CloudRader/reservium-api/issues/359)) ([d23ff4b](https://github.com/CloudRader/reservium-api/commit/d23ff4b98b71a871455f7430fcebfe7392ca1faa))
* **deps:** update astral-sh/setup-uv action to v8.3.2 ([#363](https://github.com/CloudRader/reservium-api/issues/363)) ([4ce85a7](https://github.com/CloudRader/reservium-api/commit/4ce85a719b9889eafedd40dd588d71f75acacf7d))
* **deps:** update dependency astral-sh/uv to v0.11.26 ([#345](https://github.com/CloudRader/reservium-api/issues/345)) ([6914881](https://github.com/CloudRader/reservium-api/commit/6914881a12b6f65b6b70601c608b5f06edd35637))
* **deps:** update dependency astral-sh/uv to v0.11.27 ([#358](https://github.com/CloudRader/reservium-api/issues/358)) ([1dc5e83](https://github.com/CloudRader/reservium-api/commit/1dc5e83dd43729de3e59d84ba445d1b170021ddd))
* **deps:** update dependency astral-sh/uv to v0.11.28 ([#361](https://github.com/CloudRader/reservium-api/issues/361)) ([559ddc6](https://github.com/CloudRader/reservium-api/commit/559ddc6f151cf1522a41ff78b1688c90fc816fcb))
* **deps:** update dependency mypy to v2.2.0 ([#362](https://github.com/CloudRader/reservium-api/issues/362)) ([92aa468](https://github.com/CloudRader/reservium-api/commit/92aa4680cbcc8f08ac79bdeecc256737556ad778))
* **deps:** update dependency ruff to v0.15.21 ([#367](https://github.com/CloudRader/reservium-api/issues/367)) ([ad3f49c](https://github.com/CloudRader/reservium-api/commit/ad3f49cb9178549a15bcb83d2947792c3dab3f15))
* **deps:** update python docker tag to v3.14.6 ([#343](https://github.com/CloudRader/reservium-api/issues/343)) ([bac9ac0](https://github.com/CloudRader/reservium-api/commit/bac9ac00355af86ed60138fc8a37e9544a2274fb))
* **di:** add Services and External Providers to dishka, remove custom ([ffc0b8f](https://github.com/CloudRader/reservium-api/commit/ffc0b8f2a6bc1204f3877d946b077090135f0be3))
* **docs:** remove access card system tag from openapi docs ([da143b4](https://github.com/CloudRader/reservium-api/commit/da143b4c2adf626357f1a13919661dd03cf1a00d))
* **domain:** add business domain models undependent from orm ([e2494e0](https://github.com/CloudRader/reservium-api/commit/e2494e052b5b98d4c1896c41415aafa86b8f55f2))
* **domain:** do more pure releationships and add base entity class ([b0dfcf4](https://github.com/CloudRader/reservium-api/commit/b0dfcf46b61aa7cb8e95ee9a122dd00672f956eb))
* **domain:** rename models to entities under domain, add value objects ([27bc571](https://github.com/CloudRader/reservium-api/commit/27bc57196145b6f0ee56e70ddb5de121ccf1f490))
* **env:** add env template, add script for creating .env + add to make ([97770f4](https://github.com/CloudRader/reservium-api/commit/97770f4852154f16be8c78e9906190b79a2f25fd))
* **make:** add migrations commands to Makefile for alembic ([79c82d3](https://github.com/CloudRader/reservium-api/commit/79c82d3a0439ac0a1949d19630dc739fbb2dd436))


### 🐛 Fixes

* **api:** update v2 routers to import from application schemas ([71ad36a](https://github.com/CloudRader/reservium-api/commit/71ad36aa7ad5d47954e537fee7dfad256a45af41))
* **calendar_provider:** rename from calendar to provider ([f3653d0](https://github.com/CloudRader/reservium-api/commit/f3653d09fff3273860807107e8496b31fbc29932))
* **container:** double init services in containers ([0d7315b](https://github.com/CloudRader/reservium-api/commit/0d7315b20403edd958158a1896be9d8b1c917106))
* **deps:** update dependency fastapi to v0.138.2 ([#344](https://github.com/CloudRader/reservium-api/issues/344)) ([9b7df6f](https://github.com/CloudRader/reservium-api/commit/9b7df6f0b5967146354b44488fa984b544e12cff))
* **deps:** update dependency fastapi to v0.139.0 ([#347](https://github.com/CloudRader/reservium-api/issues/347)) ([47d665e](https://github.com/CloudRader/reservium-api/commit/47d665e5b82da674faa8e79019cf7bbc5afe8f42))
* **deps:** update dependency uvicorn to v0.50.0 ([#351](https://github.com/CloudRader/reservium-api/issues/351)) ([ef6e7d5](https://github.com/CloudRader/reservium-api/commit/ef6e7d52bac0c4407cf26364249d6ee8922ddf38))
* **deps:** update dependency uvicorn to v0.50.1 ([#355](https://github.com/CloudRader/reservium-api/issues/355)) ([b04ecb2](https://github.com/CloudRader/reservium-api/commit/b04ecb203b3cb85e6eb33e7c8c77e2d9c117e9c3))
* **deps:** update dependency uvicorn to v0.50.2 ([#356](https://github.com/CloudRader/reservium-api/issues/356)) ([5b6395d](https://github.com/CloudRader/reservium-api/commit/5b6395d91a8a1134b7e9bf87b6deb1cbacffd092))
* **deps:** update dependency uvicorn to v0.51.0 ([#365](https://github.com/CloudRader/reservium-api/issues/365)) ([e952f19](https://github.com/CloudRader/reservium-api/commit/e952f196543f0d398fb376b5c7cfa98cc27d67fd))
* **dishka:** fixes after migration to dishka in api layer ([9c8d5b4](https://github.com/CloudRader/reservium-api/commit/9c8d5b45c07226b0ff64bc5b16f722d82f5d283d))


### 🧹 Refactors

* **calendar_provider:** add interface for CalendarProvider move ([c421f6a](https://github.com/CloudRader/reservium-api/commit/c421f6a6048637cd3e82c7cd59c22937cedd5339))
* **config:** decouple mail config from fastapi-mail library ([e2f7432](https://github.com/CloudRader/reservium-api/commit/e2f74321ff4598ee5ad2edc99dc18027712103e1))
* **config:** do configs more supportable and clean ([89433e3](https://github.com/CloudRader/reservium-api/commit/89433e38992586b65b4c352fa49997e6a8fee4b3))
* **config:** split configs for every component ([8a7bda1](https://github.com/CloudRader/reservium-api/commit/8a7bda125fb7c8dcbf30a173a69641baf25c76c0))
* **container:** separate containers and update dependencies ([6ccc0c6](https://github.com/CloudRader/reservium-api/commit/6ccc0c63d26c893441d62faa3f937e504aa346c7))
* **core:** rename application to bootstrap ([608441b](https://github.com/CloudRader/reservium-api/commit/608441be7b63d8d88a8467de76f3bdc6b986bac4))
* **database:** create provider and di with dishka, remove custom ([16a9073](https://github.com/CloudRader/reservium-api/commit/16a90730368a5932ee2b58808e3b535c13361400))
* **email:** move under infra, do proper di wire with dishka ([755e78b](https://github.com/CloudRader/reservium-api/commit/755e78b45156db9f8b3242267791e08175d5e46e))
* **google:** cleanup google provider for proper di wire ([555bf1a](https://github.com/CloudRader/reservium-api/commit/555bf1a3562192643c029cd65fe799295ea1a54d))
* **google:** move google calendar dtos under infrastructure ([5acde4f](https://github.com/CloudRader/reservium-api/commit/5acde4f3819aa3dc3a7097c7c9be8ee94e1b9b5b))
* **identity_provider:** add interface for IdentityProvider move ([9a03c55](https://github.com/CloudRader/reservium-api/commit/9a03c558da9e11cfdb767ad5612491cfb1c1ca46))
* **migrations:** move under infra ([61dd092](https://github.com/CloudRader/reservium-api/commit/61dd09288fe98a6e5350ff88fc3066d4918ac305))
* **models:** move sqlalchemy under infrastracture ([7707fef](https://github.com/CloudRader/reservium-api/commit/7707fef055d2885f9c75b62ed9dcfd83a0b485a0))
* **openid:** cleanup openid provider for proper di wire ([838df9b](https://github.com/CloudRader/reservium-api/commit/838df9b1f5fc6689cfca6ef9b3d91ce681412db2))
* **openid:** move openid dtos under infrastructure ([5af38b9](https://github.com/CloudRader/reservium-api/commit/5af38b9f177faf40a60ea66c71865d3daf4f9c69))
* **ports:** rename interfaces to ports ([880aafa](https://github.com/CloudRader/reservium-api/commit/880aafaaff2587b82d6d92d4e0b9b33d90e057ff))
* **repositories:** add adapters for repositories under ([9866ce4](https://github.com/CloudRader/reservium-api/commit/9866ce4e99628989717f2daa7e8b16c3b0e6a199))
* **repositories:** add interfaces (ports) for repositories ([37fc6b8](https://github.com/CloudRader/reservium-api/commit/37fc6b89528f3df22546b5155ecebd82f087fb4b))
* **repositories:** remove depricated crud repositories and change ([e1d1bd3](https://github.com/CloudRader/reservium-api/commit/e1d1bd35d090f0e2a1067957c921b77e0121060f))
* **repositories:** rename interfaces class names ([90bb16b](https://github.com/CloudRader/reservium-api/commit/90bb16bb0fd6bca2e954472652e7e7a07a3e5ecf))
* **routers:** migrate to di with dishka in api layer ([ed6e692](https://github.com/CloudRader/reservium-api/commit/ed6e692bcd08005452391ebd0427ff13129d8d69))
* **schemas:** move api dtos under api ([3cd303e](https://github.com/CloudRader/reservium-api/commit/3cd303e134208f33a052ab8a951c3701da2b9fee))
* **schemas:** move domain schemas under application layer ([311a0dc](https://github.com/CloudRader/reservium-api/commit/311a0dcbb091cdd002c09d730860113063f35c73))
* **scripts:** remove depricated and move virt envs scripts under ([cff34c6](https://github.com/CloudRader/reservium-api/commit/cff34c62507408b395743288234af9d2a6185d16))
* **services:** move under application and remove "services" prefix ([f14eefd](https://github.com/CloudRader/reservium-api/commit/f14eefd5fdf4c79a23fd16daf48d51f1c000a6ab))


### 🧪 Tests & Quality

* **pytest:** remove test_services package ([e0031d3](https://github.com/CloudRader/reservium-api/commit/e0031d3595925394c9d59b00e9608efb4cbb6c29))

## [2.4.3](https://github.com/CloudRader/reservium-api/compare/v2.4.2...v2.4.3) (2026-07-02)


### 🧱 Updates & Improvements

* **deps:** update dependency astral-sh/uv to v0.11.25 ([#333](https://github.com/CloudRader/reservium-api/issues/333)) ([f8215c5](https://github.com/CloudRader/reservium-api/commit/f8215c5d017209fa2d790f3a0941bb9adf46e040))
* **deps:** update dependency ruff to v0.15.20 ([#329](https://github.com/CloudRader/reservium-api/issues/329)) ([03c36ba](https://github.com/CloudRader/reservium-api/commit/03c36ba9a3ac5c9ed189338e4ed777de561a74bc))
* **deps:** update packages (security issue) ([243471f](https://github.com/CloudRader/reservium-api/commit/243471f59f96f2c30bfda281c4d33f6f00792eb5))
* **deps:** update python ([#335](https://github.com/CloudRader/reservium-api/issues/335)) ([7da98a0](https://github.com/CloudRader/reservium-api/commit/7da98a0506062f244401b7f7149a3be0bc0006ac))
* **renovate:** update config ([d17a22f](https://github.com/CloudRader/reservium-api/commit/d17a22ffc1fb8ccdceced0c3557b98702f00524b))
* **repository:** add methods in base repository ([b6b7a83](https://github.com/CloudRader/reservium-api/commit/b6b7a83ebbad575ba170ddc07bf1bffb85193a31))


### 🛠️ Fixes

* **deps:** update dependency alembic to v1.18.5 ([#325](https://github.com/CloudRader/reservium-api/issues/325)) ([59c4e72](https://github.com/CloudRader/reservium-api/commit/59c4e72147c237bf947fe5fac661d74463998744))
* **deps:** update dependency fastapi to v0.138.1 ([#326](https://github.com/CloudRader/reservium-api/issues/326)) ([d80353f](https://github.com/CloudRader/reservium-api/commit/d80353f1bab32663b27b5710089be8a5a71a6b5d))
* **deps:** update dependency google-api-python-client to v2.198.0 ([#330](https://github.com/CloudRader/reservium-api/issues/330)) ([46c28ed](https://github.com/CloudRader/reservium-api/commit/46c28edc93b046e03ba49b6d3585e8bc9837df4a))
* **deps:** update dependency jwcrypto to v1.5.8 ([#324](https://github.com/CloudRader/reservium-api/issues/324)) ([02ebac8](https://github.com/CloudRader/reservium-api/commit/02ebac80dcbfe2f3255c9389fc7cc39d47ab3f5f))


### 🧹 Refactors

* **db:** session and move under infra, add dispose ([93f31f4](https://github.com/CloudRader/reservium-api/commit/93f31f4fccae299ac10aeb68859d626f9f009d64))
* rename integration to infra., remove commented tests ([2267efe](https://github.com/CloudRader/reservium-api/commit/2267efe47ff3e0ac0663e998f2ad436b1bffb730))


### 📝 Documentation

* **readme:** update description ([f9c040e](https://github.com/CloudRader/reservium-api/commit/f9c040e58653c34ec4f7128d4cf63db0d426bc6f))


### ⚙️ DevOps & CI/CD

* **fix:** paths after last refactoring ([49d00e6](https://github.com/CloudRader/reservium-api/commit/49d00e6556313fa272ed27f53eff7ea47e847884))
* **tests:** fix "unable to reserve cache with", add cache-suffix ([f41074b](https://github.com/CloudRader/reservium-api/commit/f41074b5d7e45c560bb277d96b2947aa73b2e4c2))

## [2.4.2](https://github.com/CloudRader/reservium-api/compare/v2.4.1...v2.4.2) (2026-06-24)


### 🧱 Updates & Improvements

* add well known endpoints ([2c76c6c](https://github.com/CloudRader/reservium-api/commit/2c76c6cdc6445d4c48f8f100a4c8833ae5e1ad35))
* **deps:** update dependency astral-sh/uv to v0.11.22 ([#314](https://github.com/CloudRader/reservium-api/issues/314)) ([21c374f](https://github.com/CloudRader/reservium-api/commit/21c374f6eefd021d74f3b6149f9328f999555952))
* **deps:** update dependency astral-sh/uv to v0.11.23 ([#317](https://github.com/CloudRader/reservium-api/issues/317)) ([7e257ec](https://github.com/CloudRader/reservium-api/commit/7e257ec8d99c60eae821ade6187390053d8dd818))
* **deps:** update dependency astral-sh/uv to v0.11.24 ([#320](https://github.com/CloudRader/reservium-api/issues/320)) ([04bc702](https://github.com/CloudRader/reservium-api/commit/04bc702539c2308b99a2f85c49c8a76040fb7f4b))
* **deps:** update dependency pytest to v9.1.1 ([#315](https://github.com/CloudRader/reservium-api/issues/315)) ([a7e14d3](https://github.com/CloudRader/reservium-api/commit/a7e14d3b88738eb79dd8f450eae65e9794e69369))
* **deps:** update dependency ruff to v0.15.18 ([#313](https://github.com/CloudRader/reservium-api/issues/313)) ([5d5bed7](https://github.com/CloudRader/reservium-api/commit/5d5bed79165aa31901748c10c0195ff008625451))
* **deps:** update dependency ruff to v0.15.19 ([#321](https://github.com/CloudRader/reservium-api/issues/321)) ([f8dfe12](https://github.com/CloudRader/reservium-api/commit/f8dfe12384546492e662c8f0cd7e52c69adfbf86))
* **openid:** migrate keycloak to generic openid provider ([c2aaa1e](https://github.com/CloudRader/reservium-api/commit/c2aaa1eea7d83fe4463475dc1606010ffe8c92ea))


### 🛠️ Fixes

* **deps:** update dependency fastapi to v0.138.0 ([#318](https://github.com/CloudRader/reservium-api/issues/318)) ([12d9483](https://github.com/CloudRader/reservium-api/commit/12d94831917299808822a29bc730b7a0f5e6e36e))
* **deps:** update dependency pydantic-settings to v2.14.2 ([#316](https://github.com/CloudRader/reservium-api/issues/316)) ([d2a778e](https://github.com/CloudRader/reservium-api/commit/d2a778e548ed285a3e108bab10de6916048abe25))
* **deps:** update dependency pypdf to v6.14.2 ([#319](https://github.com/CloudRader/reservium-api/issues/319)) ([3a83cee](https://github.com/CloudRader/reservium-api/commit/3a83ceede73e8227391aa478073b277b8310ab7a))


### 🧹 Refactors

* **domain:** move schemas, enums, models under domain folder in src ([e51ed1e](https://github.com/CloudRader/reservium-api/commit/e51ed1e2bdea57f1e2071fb3e5f77f2b0e09f65e))

## [2.4.1](https://github.com/CloudRader/reservium-api/compare/v2.4.0...v2.4.1) (2026-06-18)


### 🧱 Updates & Improvements

* **build:** clean and optimize dockerfile ([eac011f](https://github.com/CloudRader/reservium-api/commit/eac011f4924053bed7929be1191dd33dbd7d5e53))
* **compose:** add reservium-ui to compose ([6608491](https://github.com/CloudRader/reservium-api/commit/660849163b578bf4659e344ab2d557650c479423))
* **deps:** update actions/checkout action to v7 ([#311](https://github.com/CloudRader/reservium-api/issues/311)) ([057f7db](https://github.com/CloudRader/reservium-api/commit/057f7dbd4a6c081e358856b2f9524aefadd64542))
* **deps:** update dependency astral-sh/uv to v0.11.20 ([#294](https://github.com/CloudRader/reservium-api/issues/294)) ([8cae430](https://github.com/CloudRader/reservium-api/commit/8cae430ae6aa0955b131bddf25143661af502fc9))
* **deps:** update dependency astral-sh/uv to v0.11.21 ([#295](https://github.com/CloudRader/reservium-api/issues/295)) ([07c76d2](https://github.com/CloudRader/reservium-api/commit/07c76d21663abff630f4faed3ea95b1cc2dd0dc3))
* **deps:** update dependency pytest to v9.1.0 ([#297](https://github.com/CloudRader/reservium-api/issues/297)) ([bb5917f](https://github.com/CloudRader/reservium-api/commit/bb5917f5e019a315cd6698a20efc475d1887a281))
* **deps:** update dependency ruff to v0.15.17 ([#296](https://github.com/CloudRader/reservium-api/issues/296)) ([d21e57e](https://github.com/CloudRader/reservium-api/commit/d21e57ea73b8a22aebf7f64100d4a585c92d2f6a))
* **deps:** update dpage/pgadmin4 docker tag to v9.16 ([#309](https://github.com/CloudRader/reservium-api/issues/309)) ([15e6118](https://github.com/CloudRader/reservium-api/commit/15e61187c3a54e90c8a79021363e06fe08c57e25))
* strict id to UUID only type ([b8ab6cf](https://github.com/CloudRader/reservium-api/commit/b8ab6cf324ce25526134949cfc457f8acd9fa632))
* **user:** get current user from decoded token ([7577cf4](https://github.com/CloudRader/reservium-api/commit/7577cf42dc04391a0323e928392b74de95faea84))
* **user:** migrate user id to uuid and create provider id col for oidc ([92d64fb](https://github.com/CloudRader/reservium-api/commit/92d64fb83109e12488a4906b07393696010757dc))


### 🛠️ Fixes

* **deps:** update dependency aiohttp to v3.14.1 ([#291](https://github.com/CloudRader/reservium-api/issues/291)) ([424333c](https://github.com/CloudRader/reservium-api/commit/424333ca91e79eab38b5877a8580fce919e667d5))
* **deps:** update dependency fastapi to v0.137.1 ([#298](https://github.com/CloudRader/reservium-api/issues/298)) ([7936cab](https://github.com/CloudRader/reservium-api/commit/7936cab6bbfb4407f7209a9bd7c54df7250131dc))
* **deps:** update dependency fastapi to v0.137.2 ([#307](https://github.com/CloudRader/reservium-api/issues/307)) ([6fe4261](https://github.com/CloudRader/reservium-api/commit/6fe4261e25f01382a71b1cb79dacdce83b9d047d))
* **deps:** update dependency fastapi-mail to v1.6.5 ([#308](https://github.com/CloudRader/reservium-api/issues/308)) ([ea95c80](https://github.com/CloudRader/reservium-api/commit/ea95c8020265bd3dc78c778f5e4cc6e87f49ee77))
* **deps:** update dependency pypdf to v6.13.1 ([#292](https://github.com/CloudRader/reservium-api/issues/292)) ([dd4b9e0](https://github.com/CloudRader/reservium-api/commit/dd4b9e07fceaf424eb14af3052b472046d42cbe0))
* **deps:** update dependency pypdf to v6.13.2 ([#293](https://github.com/CloudRader/reservium-api/issues/293)) ([ba706b4](https://github.com/CloudRader/reservium-api/commit/ba706b42105afd9ec446ea004d82fca47f0d73a6))
* **deps:** update dependency pypdf to v6.13.3 ([#306](https://github.com/CloudRader/reservium-api/issues/306)) ([7ac820b](https://github.com/CloudRader/reservium-api/commit/7ac820b7414b318dcf71433704f7cd20da24f5f7))
* **deps:** update dependency sqlalchemy to v2.0.51 ([#301](https://github.com/CloudRader/reservium-api/issues/301)) ([8eb1e00](https://github.com/CloudRader/reservium-api/commit/8eb1e003284821d07f53b5033a55163390e5515c))
* **deps:** update dependency sqlalchemy-easy-softdelete to v0.9.1 ([#304](https://github.com/CloudRader/reservium-api/issues/304)) ([b18b141](https://github.com/CloudRader/reservium-api/commit/b18b141169ae1350df3b96cbff375a7591989b7e))

## [2.4.0](https://github.com/CloudRader/reservium-api/compare/v2.3.16...v2.4.0) (2026-06-07)


### ✨ New Features

* **migration:** from google id to internal models UUID ([#277](https://github.com/CloudRader/reservium-api/issues/277)) ([c9c5be0](https://github.com/CloudRader/reservium-api/commit/c9c5be0f5e734dcff2e8a526afda4199904b1a20))


### 🧱 Updates & Improvements

* **deps:** update astral-sh/setup-uv action to v8.2.0 ([#284](https://github.com/CloudRader/reservium-api/issues/284)) ([7a32686](https://github.com/CloudRader/reservium-api/commit/7a3268659255e03abf942834e827b2e7a8cf66f4))
* **deps:** update codecov/codecov-action action to v7 ([#287](https://github.com/CloudRader/reservium-api/issues/287)) ([206670f](https://github.com/CloudRader/reservium-api/commit/206670f32280f6560b9c186e3d6e5c8810939b14))
* **deps:** update dependency astral-sh/uv to v0.11.12 ([#268](https://github.com/CloudRader/reservium-api/issues/268)) ([8dafd62](https://github.com/CloudRader/reservium-api/commit/8dafd62fe9c64f071bdc64b868ece98cc7131b38))
* **deps:** update dependency astral-sh/uv to v0.11.13 ([#270](https://github.com/CloudRader/reservium-api/issues/270)) ([15dcaca](https://github.com/CloudRader/reservium-api/commit/15dcaca902290c399991fed551b433ffa242d4ea))
* **deps:** update dependency astral-sh/uv to v0.11.14 ([#272](https://github.com/CloudRader/reservium-api/issues/272)) ([bec2b2f](https://github.com/CloudRader/reservium-api/commit/bec2b2f99b1bb8eb14dcbbbbcc1ccf0704cd710a))
* **deps:** update dependency astral-sh/uv to v0.11.19 ([#278](https://github.com/CloudRader/reservium-api/issues/278)) ([482d8b9](https://github.com/CloudRader/reservium-api/commit/482d8b9587556d8a242d84f6944443d8693a74fa))
* **deps:** update dependency mypy to v2.1.0 ([#261](https://github.com/CloudRader/reservium-api/issues/261)) ([0f222b1](https://github.com/CloudRader/reservium-api/commit/0f222b1aa077ed576f81789d2d0d8b68d4a24805))
* **deps:** update dependency pytest-asyncio to v1.4.0 ([#285](https://github.com/CloudRader/reservium-api/issues/285)) ([a6bc4fd](https://github.com/CloudRader/reservium-api/commit/a6bc4fd1227131edc501b31e989beb2d0ac66776))
* **deps:** update dependency ruff to v0.15.13 ([#273](https://github.com/CloudRader/reservium-api/issues/273)) ([5965607](https://github.com/CloudRader/reservium-api/commit/5965607b8fa11dd5a248bfad0590e0d3df97b084))
* **deps:** update dependency ruff to v0.15.16 ([#279](https://github.com/CloudRader/reservium-api/issues/279)) ([3f09b60](https://github.com/CloudRader/reservium-api/commit/3f09b60686160095bdd01601675d9db9ba73dcd3))
* **deps:** update dependency types-python-dateutil to v2.9.0.20260508 ([#266](https://github.com/CloudRader/reservium-api/issues/266)) ([0ab55f7](https://github.com/CloudRader/reservium-api/commit/0ab55f778cf4e01905e918bb35b6199420547e90))
* **deps:** update dependency types-python-dateutil to v2.9.0.20260518 ([#280](https://github.com/CloudRader/reservium-api/issues/280)) ([cb4cbc8](https://github.com/CloudRader/reservium-api/commit/cb4cbc8726ac05390cfbd921d3fbad09b2edff61))
* **deps:** update dependency types-pytz to v2026.2.0.20260518 ([#281](https://github.com/CloudRader/reservium-api/issues/281)) ([dfdf1a1](https://github.com/CloudRader/reservium-api/commit/dfdf1a16bb61c3815d466dabd8943c0a9981d4a3))
* **deps:** update postgres docker tag to v18.4 ([#274](https://github.com/CloudRader/reservium-api/issues/274)) ([e35abea](https://github.com/CloudRader/reservium-api/commit/e35abea5ceb1d4c21198a17c9c845dd52b00315a))


### 🛠️ Fixes

* **deps:** update dependency aiohttp to v3.14.0 [security] ([#276](https://github.com/CloudRader/reservium-api/issues/276)) ([03c48ed](https://github.com/CloudRader/reservium-api/commit/03c48ed175ca94bc4cf88a168210ea7c2a1d7558))
* **deps:** update dependency fastapi to v0.136.3 ([#282](https://github.com/CloudRader/reservium-api/issues/282)) ([2fd4e91](https://github.com/CloudRader/reservium-api/commit/2fd4e919c508c640aa3f3249140ebf6d7a210cb9))
* **deps:** update dependency google-api-python-client to v2.197.0 ([#286](https://github.com/CloudRader/reservium-api/issues/286)) ([1c03b0b](https://github.com/CloudRader/reservium-api/commit/1c03b0b046d8b2bed1af8c3212122486b95142bc))
* **deps:** update dependency pydantic-settings to v2.14.1 ([#267](https://github.com/CloudRader/reservium-api/issues/267)) ([a7a5301](https://github.com/CloudRader/reservium-api/commit/a7a53014778a9f859e4f6e1768cfc6217825e64b))
* **deps:** update dependency pypdf to v6.13.0 ([#269](https://github.com/CloudRader/reservium-api/issues/269)) ([84d92a4](https://github.com/CloudRader/reservium-api/commit/84d92a457a87ef5e3e2efa83c7234217d55f5f38))
* **deps:** update dependency sqlalchemy to v2.0.50 ([#283](https://github.com/CloudRader/reservium-api/issues/283)) ([bcf623b](https://github.com/CloudRader/reservium-api/commit/bcf623ba2bfc6d83ff87ff1b79289b3588ce5a23))
* **deps:** update dependency uvicorn to v0.49.0 ([#275](https://github.com/CloudRader/reservium-api/issues/275)) ([45993e8](https://github.com/CloudRader/reservium-api/commit/45993e80a54544ab77f1460704c637c63e0c61ec))

## [2.3.16](https://github.com/CloudRader/reservium-api/compare/v2.3.15...v2.3.16) (2026-05-07)


### 🧱 Updates & Improvements

* **deps:** update dependency astral-sh/uv to v0.11.11 ([#258](https://github.com/CloudRader/reservium-api/issues/258)) ([715686d](https://github.com/CloudRader/reservium-api/commit/715686df28e610c63309d36b693a97ee7725d5ec))
* **deps:** update dependency astral-sh/uv to v0.11.9 ([#257](https://github.com/CloudRader/reservium-api/issues/257)) ([7a4a8b1](https://github.com/CloudRader/reservium-api/commit/7a4a8b175fe2b550dea70094cdee9c240e2993fc))
* **deps:** update dependency types-pytz to v2026.2.0.20260506 ([#259](https://github.com/CloudRader/reservium-api/issues/259)) ([8e490ef](https://github.com/CloudRader/reservium-api/commit/8e490ef10c9d5f6d623a91e79d7d105f2c0e66e9))
* **pre-commit:** add configuration ([a05e97e](https://github.com/CloudRader/reservium-api/commit/a05e97e839bc5e8865cc6fc01fb089af05d75c97))


### 🛠️ Fixes

* **deps:** update dependency fastapi-mail to v1.6.3 ([#255](https://github.com/CloudRader/reservium-api/issues/255)) ([4c88cb5](https://github.com/CloudRader/reservium-api/commit/4c88cb5a3349bafb62b3783c56b1db3a43154600))
* **deps:** update dependency fastapi-mail to v1.6.4 ([#262](https://github.com/CloudRader/reservium-api/issues/262)) ([1eac0cf](https://github.com/CloudRader/reservium-api/commit/1eac0cf42e8ec46efb08c193fd31d42e500f7048))
* **deps:** update dependency google-api-python-client to v2.196.0 ([#254](https://github.com/CloudRader/reservium-api/issues/254)) ([fc01bc3](https://github.com/CloudRader/reservium-api/commit/fc01bc33f197f72a4d65874e44db88b38ab39bb0))
* **deps:** update dependency google-auth-oauthlib to v1.4.0 ([#263](https://github.com/CloudRader/reservium-api/issues/263)) ([80f4294](https://github.com/CloudRader/reservium-api/commit/80f4294416e1721a58d03291eeb8b80aa3947f08))
* **deps:** update dependency pydantic to v2.13.4 ([#260](https://github.com/CloudRader/reservium-api/issues/260)) ([1177dfb](https://github.com/CloudRader/reservium-api/commit/1177dfbda526b40584bf247bb9a30bbb3889f253))
* **deps:** update dependency pytz to v2026.2 ([#256](https://github.com/CloudRader/reservium-api/issues/256)) ([52571b8](https://github.com/CloudRader/reservium-api/commit/52571b80ac6f997caea0f964ac8b6cc9abf19089))


### 🧪 Tests & Quality

* **mypy:** upgrade to v2 version. Update script and config ([fe58c6e](https://github.com/CloudRader/reservium-api/commit/fe58c6e50e56673c576d11c78790197e95dc88e8))
* **pre-commit:** add pytest and refactor with use local scripts ([c31c3e6](https://github.com/CloudRader/reservium-api/commit/c31c3e60afc7ef0d0a5dc498942b5121a502c90a))
* **pre-commit:** add ruff and mypy to config ([3af8ac6](https://github.com/CloudRader/reservium-api/commit/3af8ac6e91fc954551c27bb67d1d2f54dd635052))
* **pre-commit:** run pre-commit in repository ([f69a0c3](https://github.com/CloudRader/reservium-api/commit/f69a0c31f8a0b30b973b52ac9301f212f6d3f50d))

## [2.3.15](https://github.com/CloudRader/reservium-api/compare/v2.3.14...v2.3.15) (2026-04-30)


### 🧱 Updates & Improvements

* **base-model:** add created, updated, deleted at in base model ([5d71ef7](https://github.com/CloudRader/reservium-api/commit/5d71ef74a4e9e4af5d0b9257b1e23a7aa6623a94))
* **deps:** update dependency astral-sh/uv to v0.11.8 ([#250](https://github.com/CloudRader/reservium-api/issues/250)) ([a918fca](https://github.com/CloudRader/reservium-api/commit/a918fca3b91515a91907656a264ddaa9ffec0580))
* **deps:** update googleapis/release-please-action action to v5 ([#244](https://github.com/CloudRader/reservium-api/issues/244)) ([8b11a69](https://github.com/CloudRader/reservium-api/commit/8b11a69367389813b2677a16d53dc81ae6c989c0))


### 🛠️ Fixes

* **basedpyright:** warnings ([8ae5bd1](https://github.com/CloudRader/reservium-api/commit/8ae5bd1bcd6df4a9c2023c6074110802c797a5ca))
* **config:** SecretStr configuration for secrets ([ecdf442](https://github.com/CloudRader/reservium-api/commit/ecdf442529c152b3f300cb91920de7cf9ca9fb96))
* **hard-delete-event:** correct check condition ([a505100](https://github.com/CloudRader/reservium-api/commit/a505100185f71b7320441df7297b76a80291dd3b))


### 🧹 Refactors

* **models:** unify tablename in Base, rename base model ([096e40c](https://github.com/CloudRader/reservium-api/commit/096e40cfcbea31e06fe6d7578802112a978d5dc9))


### 🧪 Tests & Quality

* **basedpyright:** fix warnings (setup in code editor) ([5aa5619](https://github.com/CloudRader/reservium-api/commit/5aa5619c1c1e94715ecf5ea5db6d44516c8bfb86))
* **pytest:** fix schemas tests ([17778ec](https://github.com/CloudRader/reservium-api/commit/17778ecffd312264f25b3c2a33a3d2060bac828e))

## [2.3.14](https://github.com/CloudRader/reservium-api/compare/v2.3.13...v2.3.14) (2026-04-25)


### 🧱 Updates & Improvements

* **deps:** update astral-sh/setup-uv action to v8.1.0 ([#234](https://github.com/CloudRader/reservium-api/issues/234)) ([f34add4](https://github.com/CloudRader/reservium-api/commit/f34add480246ce64f05903cecff0d6ea5d8c4f48))
* **deps:** update dependency ruff to v0.15.12 ([#247](https://github.com/CloudRader/reservium-api/issues/247)) ([389078a](https://github.com/CloudRader/reservium-api/commit/389078a12312aa2f4408cd73da47cbdddd6ac4e8))
* **models:** rename db tables ([fa9bca9](https://github.com/CloudRader/reservium-api/commit/fa9bca9a7e8eb3fe92504dd8af7479aad859aae2))
* **user:** apply migration for remove section_head attr ([eb58fba](https://github.com/CloudRader/reservium-api/commit/eb58fbaac023d3b4eb78c862a3fc65d3786eecef))
* **user:** remove deprecated section_head attribute ([efa315f](https://github.com/CloudRader/reservium-api/commit/efa315ff1e232746cf44a041ef38562d989da675))
* **user:** start remove depr. active_member attr ([9da2d5e](https://github.com/CloudRader/reservium-api/commit/9da2d5ed247f53238253a94ef502094c026ba2ea))


### 🛠️ Fixes

* **deps:** update dependency fastapi to v0.136.1 ([#246](https://github.com/CloudRader/reservium-api/issues/246)) ([64c955c](https://github.com/CloudRader/reservium-api/commit/64c955cb0eff9364aff59bd4dafb9c15e12e1a49))
* **deps:** update dependency uvicorn to v0.46.0 ([#245](https://github.com/CloudRader/reservium-api/issues/245)) ([f86ec23](https://github.com/CloudRader/reservium-api/commit/f86ec23a778f9124ee5a5f308529f0f2feffeeec))


### 📝 Documentation

* **readme:** update readme info ([65caa0f](https://github.com/CloudRader/reservium-api/commit/65caa0f3b127f8a5e3c05023679f8728c106aae3))

## [2.3.13](https://github.com/CloudRader/reservium-api/compare/v2.3.12...v2.3.13) (2026-04-22)


### 🛠️ Fixes

* **event:** cancelation permission checks ([#242](https://github.com/CloudRader/reservium-api/issues/242)) ([4e5d415](https://github.com/CloudRader/reservium-api/commit/4e5d415d77d6cfd8b124287e965328e9073e68ee))

## [2.3.12](https://github.com/CloudRader/reservium-api/compare/v2.3.11...v2.3.12) (2026-04-19)


### 🧱 Updates & Improvements

* **delete:** separete soft and hard deletion to separete routes and ([b343558](https://github.com/CloudRader/reservium-api/commit/b34355859cb1682bb5949557fe261a041c9c6db8))
* **deps:** update dependency ruff to v0.15.11 ([#233](https://github.com/CloudRader/reservium-api/issues/233)) ([5414a58](https://github.com/CloudRader/reservium-api/commit/5414a58b2383d61dafd4214712df9b960af52493))


### 🛠️ Fixes

* **api-base:** dependencies in update ([1649600](https://github.com/CloudRader/reservium-api/commit/164960079e8413601dd9168fc770c72f363e7a12))
* **api-base:** permissions for hard delete ([756eb7f](https://github.com/CloudRader/reservium-api/commit/756eb7f87a0ae0777faeb001857d2f47ef63be03))
* **api-base:** response model in hard delete ([c7e6880](https://github.com/CloudRader/reservium-api/commit/c7e68802e1836418c7c782c410b38d5fd58b70c9))
* **delete:** path for hard deletion ([db50368](https://github.com/CloudRader/reservium-api/commit/db5036886b9637d63fea06533430622ea5969887))
* **deps:** update dependency pydantic to v2.13.2 ([#235](https://github.com/CloudRader/reservium-api/issues/235)) ([b711169](https://github.com/CloudRader/reservium-api/commit/b7111693599ab7f19cd1e45b421eafcbae490251))
* **pytest:** tests after refactoring ([dbb88dd](https://github.com/CloudRader/reservium-api/commit/dbb88dd984c719311b872f49c15cdd34291e5a7d))
* **ruff:** warning in api-base ([6110d0b](https://github.com/CloudRader/reservium-api/commit/6110d0ba0a33050d76caebf7c9f4d191e4456686))


### 🧹 Refactors

* **event-permissions:** move permissions check in ([96cb2c5](https://github.com/CloudRader/reservium-api/commit/96cb2c51644df4a8c29de5b34aa4f62d64f111e3))
* **event-permissions:** update event routes and service with new ([efb30f2](https://github.com/CloudRader/reservium-api/commit/efb30f224056e95d7e429c4f407c5b8e2bae41f7))
* **event-permission:** update permissions in cancel event, fix ([5f9d87f](https://github.com/CloudRader/reservium-api/commit/5f9d87f73584ef762621887b40d065a960acf53e))
* **permissions:** improvements check permissions from token and in ([762d6ab](https://github.com/CloudRader/reservium-api/commit/762d6abe38f63bd94ed1f17aeb63b9b5c36a6663))
* **permissions:** rename permissions for delete operations ([57202dd](https://github.com/CloudRader/reservium-api/commit/57202dd2ae7802e156366baa6736df0b2453af43))
* **permission:** update way to check abac permissions through ([ab27ce2](https://github.com/CloudRader/reservium-api/commit/ab27ce267876c0ccae7514dc50b5acb3ee5e0ef5))

## [2.3.11](https://github.com/CloudRader/reservium-api/compare/v2.3.10...v2.3.11) (2026-04-16)


### 🧱 Updates & Improvements

* **deps:** replace astral-sh/setup-uv action with astral-sh/setup-uv v8.0.0 ([#230](https://github.com/CloudRader/reservium-api/issues/230)) ([6c377f8](https://github.com/CloudRader/reservium-api/commit/6c377f8d00b296e0df748b0a35ab3013a5dc033c))
* **deps:** update dependency astral-sh/uv to v0.11.7 ([#224](https://github.com/CloudRader/reservium-api/issues/224)) ([0961aae](https://github.com/CloudRader/reservium-api/commit/0961aae870530036bed39dbfe2e4da366b02bcab))


### 🛠️ Fixes

* CHANGLOG duplications ([602fa5b](https://github.com/CloudRader/reservium-api/commit/602fa5bb9a49e9d398fc9a15d54ed3631a248938))
* **deps:** update dependency fastapi to v0.136.0 ([#227](https://github.com/CloudRader/reservium-api/issues/227)) ([e4eff59](https://github.com/CloudRader/reservium-api/commit/e4eff5961c3068f92eb1bac96299aefe2e14704f))
* **deps:** update dependency pydantic to v2.13.1 ([#225](https://github.com/CloudRader/reservium-api/issues/225)) ([8f9a414](https://github.com/CloudRader/reservium-api/commit/8f9a414bc5fc588d2031bd77f4c7323756126d87))
* **deps:** update dependency pypdf to v6.10.1 ([#199](https://github.com/CloudRader/reservium-api/issues/199)) ([3132932](https://github.com/CloudRader/reservium-api/commit/3132932fe9ebf08eff76366b82be72c855f37e13))
* **deps:** update dependency pypdf to v6.10.2 ([#226](https://github.com/CloudRader/reservium-api/issues/226)) ([3cf9575](https://github.com/CloudRader/reservium-api/commit/3cf957530a91e440dc9495d0803923e141957118))

## [2.3.10](https://github.com/CloudRader/reservium-api/compare/v2.3.9...v2.3.10) (2026-04-13)


### 🧱 Updates & Improvements

* **deps:** update dependency mypy to v1.20.1 ([#220](https://github.com/CloudRader/reservium-api/issues/220)) ([bea3778](https://github.com/CloudRader/reservium-api/commit/bea3778e9c632032b6830af3ba08d8e483c30000))


### 🛠️ Fixes

* **ci:** tags naming ([b51d874](https://github.com/CloudRader/reservium-api/commit/b51d8741a1c7aca4333e6967b1e2e5896cabf3b4))
* **ci:** with ENVs ([51fe904](https://github.com/CloudRader/reservium-api/commit/51fe904829ac2d495130ccdb6a3859198ea06f4b))
* **deps:** update dependency pydantic to v2.13.0 ([#221](https://github.com/CloudRader/reservium-api/issues/221)) ([e5e091d](https://github.com/CloudRader/reservium-api/commit/e5e091d74f8199f13a14e5e0fa979a6f8da25243))


### ⚙️ DevOps & CI/CD

* **build:** migrate fromown workflow to docker/build-push-action ([a6d2a21](https://github.com/CloudRader/reservium-api/commit/a6d2a21bd82d4624c1a1184ebba4a7f5ede94c2d))

## [2.3.9](https://github.com/CloudRader/reservium-api/compare/v2.3.8...v2.3.9) (2026-04-12)


### 🛠️ Fixes

* **ci:** condition and ref in build images ([617aa7d](https://github.com/CloudRader/reservium-api/commit/617aa7db0f543bfde71a99c3dc448044a1ce9e0b))

## [2.3.8](https://github.com/CloudRader/reservium-api/compare/v2.3.7...v2.3.8) (2026-04-12)


### 🧱 Updates & Improvements

* **ci:** merge build and push image for dev and release to one ([0a953c9](https://github.com/CloudRader/reservium-api/commit/0a953c90bc3dd49d4c4544bddbca01011357ec7d))
* **ci:** migrate from Docker Hub AR to GH ([dd1f6f4](https://github.com/CloudRader/reservium-api/commit/dd1f6f4a8c0e2f5bf26cef7883184fb5fdbe4ed7))
* **deps:** update python ([#196](https://github.com/CloudRader/reservium-api/issues/196)) ([3592884](https://github.com/CloudRader/reservium-api/commit/35928849d022cb392f14ffec00e720667deb9104))


### 🛠️ Fixes

* **ci:** add permissions for build and push image jobs ([50fb74d](https://github.com/CloudRader/reservium-api/commit/50fb74d197ba759060f58a5f9c3009c717e489ab))
* **ci:** build and push image job check conditions ([95fc26c](https://github.com/CloudRader/reservium-api/commit/95fc26c7a45158de5b8aca31014884f9188a3904))
* **ci:** GitHub repo name ([b5b6fe8](https://github.com/CloudRader/reservium-api/commit/b5b6fe8cef6308aaef6406004ce7cdd8ac78c2b6))
* **ci:** remove old build dev image and fix the new one ref ([10616f2](https://github.com/CloudRader/reservium-api/commit/10616f215a02394878b9ad653cbac776ea3a481a))
* release please manifest and changelog ([5d7e74e](https://github.com/CloudRader/reservium-api/commit/5d7e74e6a2d00e3b091ae1368bae7ade16f4e91d))

## [2.3.7](https://github.com/CloudRader/reservium-api/compare/v2.3.6...v2.3.7) (2026-04-12)


### 🛠️ Fixes

* **ci:** change build and push image job trigger ([d721580](https://github.com/CloudRader/reservium-api/commit/d721580bacc1ee4650cdba30dcd071a382372408))

## [2.3.6](https://github.com/CloudRader/reservium-api/compare/v2.3.5...v2.3.6) (2026-04-12)


### 🛠️ Fixes

* **ci:** build and push image job trigger ([acf8e70](https://github.com/CloudRader/reservium-api/commit/acf8e701e26832b896dc9bf0b4920ae82707b8d2))

## [2.3.5](https://github.com/CloudRader/reservium-api/compare/v2.3.4...v2.3.5) (2026-04-12)


### 🧱 Updates & Improvements

* remove spicedb integration from project ([4fcbcc7](https://github.com/CloudRader/reservium-api/commit/4fcbcc7ed341a7f84299fcb37ccab0f0ac74cd6c))
* **renovate:** update configuration ([ea85570](https://github.com/CloudRader/reservium-api/commit/ea8557097e461fb94fc20261d2de293530304238))
* **ruff:** solve tryceratops (try/except anti-patterns) rules ([c68696a](https://github.com/CloudRader/reservium-api/commit/c68696a3868f1bdf0df9100e2fddacebc6aa7d61))
* update to Python 14 ([cccb740](https://github.com/CloudRader/reservium-api/commit/cccb7403f10bd453e91c7119e75343a43b4ff366))


### 🛠️ Fixes

* **build:** Dockerfile and compose ([d672117](https://github.com/CloudRader/reservium-api/commit/d67211758061327f8dda14e58f91c28f53de494a))
* **ci:** build and push image job for correct tag image ([815e404](https://github.com/CloudRader/reservium-api/commit/815e4044a7441cc0bbe33c95cdfc51f219eb75aa))
* **ruff:** warning after update to Python 14 ([5db0ea2](https://github.com/CloudRader/reservium-api/commit/5db0ea2dcdc472ffe65332ed49fc4ab9132b5f1e))

## [2.3.4](https://github.com/CloudRader/reservium-api/compare/v2.3.3...v2.3.4) (2026-04-11)


### 🛠️ Fixes

* remove attendees from create google calendar body ([#205](https://github.com/CloudRader/reservium-api/issues/205)) ([e31e919](https://github.com/CloudRader/reservium-api/commit/e31e9196aa4ce0c57b420b22ded0472503e27d7f))

## [2.3.3](https://github.com/CloudRader/reservium-api/compare/v2.3.2...v2.3.3) (2026-04-11)


### 🛠️ Fixes

* **calendars:** remove user attribute from google_calendars_available_for_import ([#203](https://github.com/CloudRader/reservium-api/issues/203)) ([d1d12e9](https://github.com/CloudRader/reservium-api/commit/d1d12e96a603b774618035ef4e58a93e726cf78a))

## [2.3.2](https://github.com/CloudRader/reservium-api/compare/v2.3.1...v2.3.2) (2026-04-11)


### 🧱 Updates & Improvements

* change oauth2 user account to service account ([db0536c](https://github.com/CloudRader/reservium-api/commit/db0536c83881a128cd01329d23d299c9788b6407))
* **google:** add permission checks for google endpoints ([00b66d2](https://github.com/CloudRader/reservium-api/commit/00b66d23392b6151f3bc46e45e1ed4057d3f75d3))
* **google:** add sync operations for google calendar integration ([84cca1b](https://github.com/CloudRader/reservium-api/commit/84cca1bd561a48829af492545959ce14c48659d0))
* **google:** use service account for google integrations  ([#201](https://github.com/CloudRader/reservium-api/issues/201)) ([58b9f53](https://github.com/CloudRader/reservium-api/commit/58b9f53818f856316e89f25cd8ec84ca243f00ab))


### 🛠️ Fixes

* **deps:** update dependency pypdf to v6.10.0 [security] ([#200](https://github.com/CloudRader/reservium-api/issues/200)) ([e6fc363](https://github.com/CloudRader/reservium-api/commit/e6fc3635ca42f4ac81d446a5562e0f3c4e9ed917))
* **tetsts:** test variables ([f5c5a06](https://github.com/CloudRader/reservium-api/commit/f5c5a062d6dc1c676efa0b6c3f50ca0d0d45d181))

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
