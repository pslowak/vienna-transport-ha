# Changelog

## [1.1.1](https://github.com/pslowak/vienna-transport-ha/compare/v1.1.0...v1.1.1) (2026-09-04)


### Bug Fixes

* align Ruff target version with project's Python version ([#72](https://github.com/pslowak/vienna-transport-ha/issues/72)) ([8824764](https://github.com/pslowak/vienna-transport-ha/commit/88247649face6a079b2c3761a25792a5c65763fc))
* **client:** handle all transport and JSON errors as ClientError ([#94](https://github.com/pslowak/vienna-transport-ha/issues/94)) ([d9a6793](https://github.com/pslowak/vienna-transport-ha/commit/d9a6793109e71aecd8b53fb8791d577c6e938381))
* **config-flow:** reject unknown stop IDs ([#95](https://github.com/pslowak/vienna-transport-ha/issues/95)) ([ce6603d](https://github.com/pslowak/vienna-transport-ha/commit/ce6603d6dd0e5097bf4665998a4c571ea57da564))
* **config-flow:** surface connection and API errors during setup ([#70](https://github.com/pslowak/vienna-transport-ha/issues/70)) ([c9e4c31](https://github.com/pslowak/vienna-transport-ha/commit/c9e4c3140bde41235f74b49964bc66f88a94bfce))
* **sensor:** serialize departure datetime as ISO string in state attributes ([#71](https://github.com/pslowak/vienna-transport-ha/issues/71)) ([1a8bc60](https://github.com/pslowak/vienna-transport-ha/commit/1a8bc60bf9d3d9f1e7958fb46156067e51b703a4))
* share single coordinator across all config entries ([#65](https://github.com/pslowak/vienna-transport-ha/issues/65)) ([e0b7456](https://github.com/pslowak/vienna-transport-ha/commit/e0b7456ac0d6e0ea60f1577c6acb553d3b28c410))

## [1.1.0](https://github.com/pslowak/vienna-transport-ha/compare/v1.0.0...v1.1.0) (2026-08-13)


### Features

* add HACS support ([#59](https://github.com/pslowak/vienna-transport-ha/issues/59)) ([3c1b3cc](https://github.com/pslowak/vienna-transport-ha/commit/3c1b3ccc38e3cf5f46db25cbbc88256a934e09c2))

## 1.0.0 (2026-08-07)


### Features

* add editor card ([#9](https://github.com/pslowak/vienna-transport-ha/issues/9)) ([c866a8a](https://github.com/pslowak/vienna-transport-ha/commit/c866a8af2c9f40b89ab0d13fcaf7440998fe8cc5))
* add format check in ci ([#13](https://github.com/pslowak/vienna-transport-ha/issues/13)) ([d8958dd](https://github.com/pslowak/vienna-transport-ha/commit/d8958ddfc878785b6bc4bc60124090bc4bf75b40))
* add line colors for departures ([#4](https://github.com/pslowak/vienna-transport-ha/issues/4)) ([a00b91d](https://github.com/pslowak/vienna-transport-ha/commit/a00b91dc19053e378781a9964231fd5002bf549d))
* add line filtering ([#1](https://github.com/pslowak/vienna-transport-ha/issues/1)) ([1edcc19](https://github.com/pslowak/vienna-transport-ha/commit/1edcc190278e44757e5c70919ab716ecdac30892))
* add option to limit shown departures ([#2](https://github.com/pslowak/vienna-transport-ha/issues/2)) ([55deb31](https://github.com/pslowak/vienna-transport-ha/commit/55deb31e01c497b2ada9bce817409b26df9013d5))
* add translation support for card and editor ([#11](https://github.com/pslowak/vienna-transport-ha/issues/11)) ([940665a](https://github.com/pslowak/vienna-transport-ha/commit/940665ae8f7ecd098105db765bf5db53a977c00d))
* **card:** add `getStubConfig` for card default values ([#46](https://github.com/pslowak/vienna-transport-ha/issues/46)) ([337069e](https://github.com/pslowak/vienna-transport-ha/commit/337069eb6969f88b314c1418c00c1f5a66f35e7a))
* **card:** display "now" for arriving vehicles ([#22](https://github.com/pslowak/vienna-transport-ha/issues/22)) ([16ae788](https://github.com/pslowak/vienna-transport-ha/commit/16ae78833f9f56216e611a088759885f4c5bb406))
* **card:** display card in card picker ([#45](https://github.com/pslowak/vienna-transport-ha/issues/45)) ([ae524db](https://github.com/pslowak/vienna-transport-ha/commit/ae524db8a6d47f2d43991679654d920e7cdf60af))
* **card:** show cooling indicator for air-conditioned vehicles ([#24](https://github.com/pslowak/vienna-transport-ha/issues/24)) ([d49162f](https://github.com/pslowak/vienna-transport-ha/commit/d49162fa1559eb4190e0c6e41f58fdcbd75b21a8))
* **coordinator:** use expiring cache as fallback on errors ([#33](https://github.com/pslowak/vienna-transport-ha/issues/33)) ([8b62185](https://github.com/pslowak/vienna-transport-ha/commit/8b621859a6a7003e4e075c2d3b777d471598d40b))
* **frontend:** auto-register Lovelace card when integration is set up ([#43](https://github.com/pslowak/vienna-transport-ha/issues/43)) ([ce9fe44](https://github.com/pslowak/vienna-transport-ha/commit/ce9fe4448a1c51ccd95629d5f752737f9d250200))
* handle API rate limit ([#6](https://github.com/pslowak/vienna-transport-ha/issues/6)) ([e0d1f79](https://github.com/pslowak/vienna-transport-ha/commit/e0d1f79337d3068c27d59426d7b1c8796f073171))
* introduce backend integration and connect frontend card ([#16](https://github.com/pslowak/vienna-transport-ha/issues/16)) ([9a40fb0](https://github.com/pslowak/vienna-transport-ha/commit/9a40fb03c8de16556d24f20d2d02a8da5914def7))
* make lines optional ([#3](https://github.com/pslowak/vienna-transport-ha/issues/3)) ([caf8d50](https://github.com/pslowak/vienna-transport-ha/commit/caf8d508147b19907142a1d3c096c0a7f363fc3f))
* **parser:** include information whether vehicle is cooled ([#23](https://github.com/pslowak/vienna-transport-ha/issues/23)) ([b682d46](https://github.com/pslowak/vienna-transport-ha/commit/b682d46ab5a9563f84863e948012776cddabaeba))


### Bug Fixes

* **card:** exclude public directory from library builds ([#42](https://github.com/pslowak/vienna-transport-ha/issues/42)) ([9a3c59d](https://github.com/pslowak/vienna-transport-ha/commit/9a3c59d08c5b4ff86ea5db6e962424bdd9a53a10))
* **config-flow:** update data description to match text selector ([#20](https://github.com/pslowak/vienna-transport-ha/issues/20)) ([2ca500c](https://github.com/pslowak/vienna-transport-ha/commit/2ca500cdd2acebbf37a72dce0cb88a0e25b427c6))
* exclude `manifest.json` from prettier ([#57](https://github.com/pslowak/vienna-transport-ha/issues/57)) ([9a900c6](https://github.com/pslowak/vienna-transport-ha/commit/9a900c638e1088da5d1d2883266e71ebe05552bb))
* **frontend:** handle duplicate static path registration ([#44](https://github.com/pslowak/vienna-transport-ha/issues/44)) ([0aa6920](https://github.com/pslowak/vienna-transport-ha/commit/0aa6920603edc09d51b5381f6086f6dbaa419b2e))
* **parser:** fall back to `time_planned` if `time_real` is not supported ([#17](https://github.com/pslowak/vienna-transport-ha/issues/17)) ([b3d4cc1](https://github.com/pslowak/vienna-transport-ha/commit/b3d4cc1ddeb191886cf8763a70daee329393abb1))
* **parser:** use `timePlanned` if `timeReal` is not available and vice versa ([#19](https://github.com/pslowak/vienna-transport-ha/issues/19)) ([c51974a](https://github.com/pslowak/vienna-transport-ha/commit/c51974acc56aefa729307fe7a54b0479702f4e38))
* rename package to match domain name ([#18](https://github.com/pslowak/vienna-transport-ha/issues/18)) ([f03bbb3](https://github.com/pslowak/vienna-transport-ha/commit/f03bbb3c17d384e87d97ba9aad112b31ac9dca7f))
* use vehicle type from line if available ([#15](https://github.com/pslowak/vienna-transport-ha/issues/15)) ([c0f97f9](https://github.com/pslowak/vienna-transport-ha/commit/c0f97f97a6ede67316ae7f348756e063daf74882))
