# Local Dependency Audit

**2026-09-21 revision:** Sibling-project observations below remain historical evidence. Current selections in plan.md/research.md supersede older recommendations: Typer >=0.27.2, pylatexenc==2.11, no Unidecode, Latin-only policy, cross-volume copy first, no hard-linked backups, and separate config/catalog locations.

**Date**: 2026-09-20. **Purpose**: Ground refs package choices in the user's current development practice, including the explicit preference for Typer.

## Scope and evidence

Read Python and JavaScript manifests under `/Volumes/Casa/dev`, excluding virtual environments, dependency caches, vendored/build output, and worktrees. Discovery found 40 manifests. The primary comparison is 14 Python projects with a latest Git commit on or after 2026-07-22 (a 60-day window). Seven additional Python projects qualify only by manifest modification time; they are listed separately because several share an August 24 timestamp and a touched manifest alone does not demonstrate recent development. Also inspected the JavaScript manifests for codelab, llm-lab/frontend, dema-core/dema-core, and twc-bridge. Agent tooling and credential experiments are excluded from the product comparison.

Evidence is checked-out `pyproject.toml`, direct-package resolutions in `uv.lock`, `package.json`, Git commit timestamps, and targeted CLI source inspection. A lock resolution is not proof of installation, runtime compatibility, or a successful test. Counts below concern direct declarations in the 14 primary Python manifests; standard-library and transitive dependencies are excluded. This is a package-selection audit, not a vulnerability scan. Sibling projects were read only.

## Findings

| Area | Observed practice | Consequence for refs |
| --- | --- | --- |
| CLI | Typer in 9/14 projects and 9/11 projects declaring console scripts; no direct Click dependency in the sample. The other two packaged CLIs, md-to-pptx and near-earth-object-monitor, use argparse. | Adopt Typer, matching the user's explicit preference. |
| CLI version | danner and git-muster declare `typer>=0.27,<0.28`; both lock 0.27.1. dema-data and course-courier also lock 0.27.1. Other Typer locks range from 0.17.4 to 0.26.8. | Use `typer>=0.27,<0.28`; resolve the exact compatible version during implementation under the cooldown. |
| Paths | Every one of the 11 packaged Python CLI projects has application source importing pathlib. | Use `Path` throughout application interfaces and ordinary filesystem operations. |
| Validation | Pydantic is direct in 4/14; danner uses `>=2.13,<3` and locks 2.13.4. | Keep Pydantic; align the proposed floor to `>=2.13,<3`. |
| Human output | Rich is direct in 4/14; Textual in worldrunner. Typer 0.27.1's audited locks already include Rich. | Typer handles help. Declare Rich directly only if refs itself imports it for human output; JSON output must stay independent of presentation. No TUI requirement. |
| HTTP | HTTPX in 4/14; requests in 3/14. | No initial HTTP dependency: agents supply metadata and daily catalog work is local. Revisit HTTPX when a network adapter has a requirement. |
| Configuration | platformdirs in 2/14; conditional tomli in 2/14; tomli-w in canvas-ledger; YAML packages serve other workflows. | Keep explicit refs home/config precedence and stdlib tomllib. No TOML backport on Python 3.14. Evaluate a TOML writer if implementation needs general serialization rather than fixed setup output. |
| Storage | canvas-ledger uses SQLModel and Alembic; most sampled tools do not require an ORM. | Keep stdlib sqlite3 and explicit schema migrations for refs' journal and transactions. |
| Tests/static checks | pytest in 12/14 dev groups, Ruff in 9/14, pytest-cov in 8/14; ty in 6/14 versus mypy in 3/14. | Use pytest, pytest-cov, Ruff, and ty. |
| Packaging | uv_build in 9/14; Hatchling in 2/14; three application environments have no build backend. | Use uv_build for the single src-layout package; `>=0.12.1,<0.13` matches danner/git-muster. |
| Resolution policy | 12/14 declare `tool.uv.exclude-newer = "3 days"`; dema-data and gradebot do not declare it in these manifests. | Preserve the user's explicit portable three-day policy and locked checks. No sibling configuration changes are implied. |
| Domain libraries | No primary project directly declares bibtexparser, pylatexenc, or Unidecode. | Retain the dedicated bibliography/transliteration research and fixture gates; local popularity cannot establish their fidelity. |

Typer now vendors Click instead of declaring it as a separate dependency. Its public APIs should own command types, exceptions, and testing. Older source in canvas-ledger and dema-llm imports Click directly, so those integrations should not be copied into refs. This observation is not a claim that those locked applications are broken. [Typer release notes](https://typer.tiangolo.com/release-notes/).

The selected build backend supports ordinary Python package layouts, and ty supplies the type-checking command. The exact dev-tool versions remain implementation lockfile decisions. [uv build backend](https://docs.astral.sh/uv/concepts/build-backend/), [ty documentation](https://docs.astral.sh/ty/).

## pathlib and durable publication

Use `destination.hardlink_to(staged)` for publishing a verified regular staging file at a new destination. CPython implements that call as `os.link(staged, destination)`: it preserves the same hard-link operation and reverses the argument presentation. The existing-destination error is the collision check; do not implement no-overwrite as a separate existence check followed by replacement. Stage beside the destination so publication is on one filesystem, even when acquisition crosses volumes. [Path.hardlink_to](https://docs.python.org/3.14/library/pathlib.html#pathlib.Path.hardlink_to), [CPython implementation](https://github.com/python/cpython/blob/3.14/Lib/pathlib/__init__.py).

For an explicitly authorized replacement of an adopted bibliography, use `staged.replace(destination)`. Ordinary `Path.rename()` or `Path.move()` does not provide the required no-overwrite publication contract. Keep `os.fsync`, descriptor-level `os.open` where needed for directory flushes or flags, and `fcntl` locks inside the filesystem helper. Use direct `os.link` only if a concrete need for its descriptor-relative or symlink controls arises. Path objects can be passed to os functions without converting them to strings. These API choices preserve the journal, digest checks, and durability protocol; pathlib does not make a filesystem change and SQLite commit atomic. [Path replacement](https://docs.python.org/3.14/library/pathlib.html#pathlib.Path.replace), [OS filesystem primitives](https://docs.python.org/3.14/library/os.html).

## Primary Python project inventory

Each project links to its manifest. Requirements retain their declared ranges; the Typer column reports the lockfile resolution only.

| Project | Latest commit | Python | Typer lock | Direct runtime dependencies |
| --- | --- | --- | --- | --- |
| [codelab](../../../codelab/pyproject.toml) | 2026-09-14 | `>=3.11` | — | `boto3==1.35.0`, `cryptography>=46.0.2`, `flask==2.0.1`, `flask-cors==3.0.10`, `gevent>=23.9.1`, `gunicorn==21.2.0`, `pytz==2024.1`, `requests>=2.32.5`, `werkzeug==2.0.1` |
| [llm-lab](../../../llm-lab/pyproject.toml) | 2026-09-06 | `>=3.13` | — | `openai>=1.100,<3`, `streamlit>=1.49,<2`, `tiktoken>=0.11,<1`, `fastapi>=0.116,<1`, `uvicorn>=0.35,<1`, `pyjwt[crypto]>=2.10,<3`, `httpx>=0.28,<1` |
| [worldrunner](../../../worldrunner/pyproject.toml) | 2026-09-05 | `>=3.13` | 0.26.8 | `pydantic-ai-slim[anthropic]>=2.7.0`, `textual>=8.2.8,<9`, `typer>=0.19,<1` |
| [danvas](../../../danvas/pyproject.toml) | 2026-09-05 | `>=3.12,<3.15` | 0.25.1 | `beautifulsoup4>=4.12`, `canvasapi>=3.3`, `markdown>=3.6`, `platformdirs>=4.0`, `pyyaml>=6.0`, `requests>=2.31`, `tinycss2>=1.4`, `typer>=0.19` |
| [canvas-ledger](../../../canvas-ledger/pyproject.toml) | 2026-09-05 | `>=3.13` | 0.21.1 | `typer>=0.9.0`, `sqlmodel>=0.0.22`, `alembic>=1.14.0`, `httpx>=0.28.0`, `canvasapi>=3.3.0`, `tomli>=2.0.0;python_version<'3.11'`, `tomli-w>=1.0.0` |
| [secretpath](../../../secretpath/pyproject.toml) | 2026-09-05 | `>=3.10` | 0.26.7 | `tomli>=2.0.0; python_version < '3.11'`, `typer>=0.19` |
| [git-muster](../../../git-muster/pyproject.toml) | 2026-08-30 | `>=3.13,<3.15` | 0.27.1 | `rich>=14,<16`, `typer>=0.27,<0.28` |
| [danner](../../../danner/pyproject.toml) | 2026-08-29 | `>=3.13,<3.15` | 0.27.1 | `beautifulsoup4>=4.15,<5`, `httpx>=0.28,<1`, `platformdirs>=4,<5`, `pydantic>=2.13,<3`, `rich>=14,<15`, `typer>=0.27,<0.28` |
| [dema-data](../../../dema-data/pyproject.toml) | 2026-08-29 | `>=3.13` | 0.27.1 | `openpyxl>=3.1.5`, `pydantic>=2.11.0`, `ruamel-yaml>=0.18.10`, `typer>=0.16.0` |
| [dema-llm](../../../dema-llm/pyproject.toml) | 2026-07-27 | `>=3.13` | 0.17.4 | `typer>=0.12.3`, `rich>=13.7.0`, `python-dotenv>=1.0.0`, `python-json-logger>=2.0.7`, `pyyaml>=6.0.0`, `pydantic>=2.11.7`, `rapidfuzz>=3.14.1`, `openpyxl>=3.1.5`, `litellm>=1.43.11`, `httpx>=0.27.2` |
| [md-to-pptx](../../../md-to-pptx/pyproject.toml) | 2026-07-30 | `>=3.11` | — | `lxml>=5.0`, `python-pptx>=1.0` |
| [gradebot](../../../gradebot/pyproject.toml) | 2026-08-23 | `>=3.13` | — | `litellm>=1.80.7,!=1.82.7,!=1.82.8`, `pandas>=2.3.3`, `python-dateutil>=2.9.0.post0`, `python-dotenv>=1.2.1`, `pytz>=2025.2`, `seaborn>=0.13.2`, `sqlglot>=26.0.0`, `sqlparse>=0.5.0` |
| [course-courier](../../../course-courier/pyproject.toml) | 2026-08-20 | `>=3.11` | 0.27.1 | `jupytext>=1.17,<2.0`, `nbformat>=5.10,<6.0`, `pyyaml>=6.0,<7.0`, `typer>=0.12,<1.0` |
| [near-earth-object-monitor](../../../near-earth-object-monitor/pyproject.toml) | 2026-07-30 | `>=3.11` | — | `pydantic>=2.13.4`, `python-dotenv>=1.0`, `requests>=2.32`, `rich>=15.0.0`, `streamlit>=1.59.1` |

### Development, optional, and build dependencies

**codelab**: dev: `coverage>=7.10.7`, `freezegun>=1.5.5`, `locust>=2.41.6`, `matplotlib>=3.10.7`, `moto>=5.1.14`, `mypy`, `pandas>=2.3.3`, `playwright>=1.55.0`, `pytest-cov>=7.0.0`, `pytest-mock>=3.15.1`, `pytest-playwright>=0.7.1`; build: None declared.

**llm-lab**: build: None declared.

**worldrunner**: dev: `pytest>=9.1.1`, `pytest-asyncio>=1.4`, `ruff>=0.15.20`, `ty>=0.0.57`; build: `hatchling`.

**danvas**: dev: `pip-audit>=2.9`, `pytest>=8.0`, `pytest-cov>=6.0`, `ruff>=0.8`, `ty>=0.0.1a22`; build: `uv_build>=0.12.0,<0.13.0`.

**canvas-ledger**: dev: `pytest>=8.0.0`, `pytest-cov>=4.0.0`, `ruff>=0.8.0`, `mypy>=1.14.0`, `radon>=6.0.0`, `bandit>=1.9.2`, `vulture>=2.14`, `interrogate>=1.7.0`; docs: `mkdocs>=1.6`, `mkdocs-material>=9.5`, `mkdocs-typer2>=0.1.6`; build: `hatchling`.

**secretpath**: dev: `pytest>=8`, `ruff>=0.15.12`; build: `uv_build>=0.11.20,<0.12.0`.

**git-muster**: dev: `pytest>=8.4,<10`, `pytest-cov>=6,<8`, `ruff>=0.12,<1`, `ty>=0.0.1a20`; build: `uv_build>=0.12.1,<0.13`.

**danner**: dev: `jsonschema>=4.25,<5`, `pip-audit>=2.9,<3`, `pytest>=8.4,<10`, `pytest-cov>=6,<8`, `ruff>=0.12,<1`, `ty>=0.0.1a20`; desktop-build: `pyinstaller>=6.22.2,<6.23`; optional desktop: `PySide6-Essentials>=6.11.2,<6.12`; build: `uv_build>=0.12.1,<0.13`.

**dema-data**: dev: `hypothesis>=6.130.0`, `jsonschema>=4.23.0`, `pytest>=8.3.0`, `ruff>=0.11.0`, `ty>=0.0.1a20`; build: `uv_build>=0.8.0,<0.9.0`.

**dema-llm**: dev: `coverage>=7.10.6`, `pytest>=8.0.0`, `pytest-cov>=7.0.0`, `radon>=6.0.1`; build: `uv_build>=0.8.13,<0.9.0`.

**md-to-pptx**: dev: `pytest>=8.0`; build: `uv_build>=0.11.0,<0.12.0`.

**gradebot**: dev: `canvasapi>=3.4.0`, `pytest>=8.4.2`, `pytest-cov>=7.0.0`, `ty>=0.0.73`; build: None declared.

**course-courier**: dev: `pytest>=8.0`, `ruff>=0.6`; build: `uv_build>=0.12.0,<0.13.0`.

**near-earth-object-monitor**: dev: `jupyter>=1.1.1`, `mypy>=1.16`, `numpy<2.5`, `pandas>=3.0.3`, `pdoc>=16.0.0`, `plotnine>=0.15.7`, `pytest>=8.4`, `pytest-cov>=7.1.0`, `ruff>=0.12`, `tabulate>=0.9.0`; build: `uv_build>=0.11.25,<0.12`.

## Manifest-time-only Python sample

These projects were inspected but excluded from the primary frequency counts. Their Git activity is older than the cutoff or unavailable.

**[solstice-slide-show](../../../solstice-slide-show/pyproject.toml)** (latest commit: unavailabl): runtime `fastapi>=0.115.0,<1.0.0`, `jinja2>=3.1.0,<4.0.0`, `pydantic>=2.9.0,<3.0.0`, `pyyaml>=6.0.0,<7.0.0`, `uvicorn>=0.32.0,<1.0.0`; dev `httpx>=0.27.0,<1.0.0`, `pytest>=8.3.0,<9.0.0`, `ruff>=0.8.0,<1.0.0`.

**[pipyer](../../../pipyer/pyproject.toml)** (latest commit: 2026-06-18): runtime `pydantic>=2.7`, `pydantic-ai>=1.106.0`, `pyyaml>=6.0`, `secretpath>=0.2.0`, `typer>=0.12`; dev `pytest>=8.0`, `ruff>=0.8`, `ty`.

**[twc-bridge](../../../twc-bridge/pyproject.toml)** (latest commit: 2026-06-18): runtime `beautifulsoup4>=4.12.3`, `httpx>=0.28.1`, `openpyxl>=3.1.5`, `pandas>=2.2.3`, `pydantic-ai>=1.89.1`, `rapidfuzz>=3.10.1`, `rich>=13.9.4`, `secretpath>=0.2.0`, `sqlmodel>=0.0.22`, `streamlit>=1.40.0`, `trafilatura>=2.0.0`, `typer>=0.15.1`, `watchdog>=6.0.0`; dev `pytest>=8.3.4`, `ruff>=0.8.4`.

**[cdex](../../../cdex/pyproject.toml)** (latest commit: 2026-05-11): runtime `Pillow>=10.0`, `python-pptx>=1.0`, `typer>=0.12`; dev `pytest>=8.0`.

**[default-python](../../../default-python/pyproject.toml)** (latest commit: 2026-02-02): runtime `beautifulsoup4>=4.14.3`, `chardet>=5.2.0`, `httpx>=0.28.1`, `ipykernel>=7.2.0`, `jsonschema>=4.26.0`, `lxml>=6.0.2`, `markdown>=3.10.2`, `matplotlib>=3.10.8`, `numpy>=2.4.2`, `openpyxl>=3.1.5`, `pandas>=3.0.0`, `pdf2image>=1.17.0`, `pdfplumber>=0.11.9`, `pillow>=12.1.0`, `pypdf>=6.6.2`, `python-docx>=1.2.0`, `python-pptx>=1.0.2`, `pyyaml>=6.0.3`, `requests>=2.32.5`, `rich>=14.3.2`, `scikit-learn>=1.8.0`, `seaborn>=0.13.2`, `statsmodels>=0.14.6`, `xlrd>=2.0.2`, `youtube-transcript-api>=1.2.4`; dev `mypy>=1.19.1`, `pytest>=9.0.2`, `ruff>=0.14.14`.

**[sylla-builder](../../../sylla-builder/pyproject.toml)** (latest commit: 2026-02-07): runtime `typer>=0.15.0`, `pydantic>=2.0.0`, `pydantic[email]>=2.0.0`, `jinja2>=3.1.0`, `pyyaml>=6.0.0`, `platformdirs>=4.0.0`; dev `pytest>=8.0.0`, `pytest-cov>=4.0.0`, `ruff>=0.8.0`, `mypy>=1.0.0`, `radon>=6.0.1`.

**[stanton](../../../stanton/pyproject.toml)** (latest commit: 2026-05-23): runtime `gurobipy>=13.0.1`, `matplotlib>=3.10.8`, `pandas>=3.0.2`; dev `pytest>=9.0.3`.

## JavaScript comparison

The recently committed dema-core project (2026-08-22) adds a separate JavaScript application to the 14 Python projects; it is not included in Python frequency counts. Its nested manifest uses React, Electron, Vite, TypeScript, better-sqlite3, graph/rendering libraries, and Vitest. llm-lab/frontend uses React 19 with Vite and TypeScript. codelab's manifest declares a large Jest/Babel-related dependency surface, so it is not a useful minimal CLI packaging template. twc-bridge declares defuddle and linkedom for content extraction and qualifies here by manifest timestamp only. These packages serve UI and extraction requirements absent from the first refs release.

### [codelab/package.json](../../../codelab/package.json)

Runtime: `agent-base ^7.1.3`, `ansi-escapes ^4.3.2`, `ansi-regex ^5.0.1`, `ansi-styles ^4.3.0`, `anymatch ^3.1.3`, `argparse ^1.0.10`, `asynckit ^0.4.0`, `babel-jest ^29.7.0`, `babel-plugin-istanbul ^6.1.1`, `babel-plugin-jest-hoist ^29.6.3`, `babel-preset-current-node-syntax ^1.1.0`, `babel-preset-jest ^29.6.3`, `balanced-match ^1.0.2`, `brace-expansion ^1.1.11`, `braces ^3.0.3`, `browserslist ^4.24.4`, `bser ^2.1.1`, `buffer-from ^1.1.2`, `call-bind-apply-helpers ^1.0.2`, `callsites ^3.1.0`, `camelcase ^5.3.1`, `caniuse-lite ^1.0.30001712`, `chalk ^4.1.2`, `char-regex ^1.0.2`, `ci-info ^3.9.0`, `cjs-module-lexer ^1.4.3`, `cliui ^8.0.1`, `co ^4.6.0`, `collect-v8-coverage ^1.0.2`, `color-convert ^2.0.1`, `color-name ^1.1.4`, `combined-stream ^1.0.8`, `concat-map ^0.0.1`, `convert-source-map ^2.0.0`, `create-jest ^29.7.0`, `cross-spawn ^7.0.6`, `cssstyle ^4.3.0`, `data-urls ^5.0.0`, `debug ^4.4.0`, `decimal.js ^10.5.0`, `dedent ^1.5.3`, `deepmerge ^4.3.1`, `delayed-stream ^1.0.0`, `detect-newline ^3.1.0`, `diff-sequences ^29.6.3`, `dunder-proto ^1.0.1`, `electron-to-chromium ^1.5.134`, `emittery ^0.13.1`, `emoji-regex ^8.0.0`, `entities ^4.5.0`, `error-ex ^1.3.2`, `es-define-property ^1.0.1`, `es-errors ^1.3.0`, `es-object-atoms ^1.1.1`, `es-set-tostringtag ^2.1.0`, `escalade ^3.2.0`, `escape-string-regexp ^2.0.0`, `esprima ^4.0.1`, `execa ^5.1.1`, `exit ^0.1.2`, `expect ^29.7.0`, `fast-json-stable-stringify ^2.1.0`, `fb-watchman ^2.0.2`, `fill-range ^7.1.1`, `find-up ^4.1.0`, `form-data ^4.0.2`, `fs.realpath ^1.0.0`, `function-bind ^1.1.2`, `gensync ^1.0.0-beta.2`, `get-caller-file ^2.0.5`, `get-intrinsic ^1.3.0`, `get-package-type ^0.1.0`, `get-proto ^1.0.1`, `get-stream ^6.0.1`, `glob ^7.2.3`, `globals ^11.12.0`, `gopd ^1.2.0`, `graceful-fs ^4.2.11`, `has-flag ^4.0.0`, `has-symbols ^1.1.0`, `has-tostringtag ^1.0.2`, `hasown ^2.0.2`, `html-encoding-sniffer ^4.0.0`, `html-escaper ^2.0.2`, `http-proxy-agent ^7.0.2`, `https-proxy-agent ^7.0.6`, `human-signals ^2.1.0`, `iconv-lite ^0.6.3`, `import-local ^3.2.0`, `imurmurhash ^0.1.4`, `inflight ^1.0.6`, `inherits ^2.0.4`, `is-arrayish ^0.2.1`, `is-core-module ^2.16.1`, `is-fullwidth-code-point ^3.0.0`, `is-generator-fn ^2.1.0`, `is-number ^7.0.0`, `is-potential-custom-element-name ^1.0.1`, `is-stream ^2.0.1`, `isexe ^2.0.0`, `istanbul-lib-coverage ^3.2.2`, `istanbul-lib-instrument ^6.0.3`, `istanbul-lib-report ^3.0.1`, `istanbul-lib-source-maps ^4.0.1`, `istanbul-reports ^3.1.7`, `jest-changed-files ^29.7.0`, `jest-circus ^29.7.0`, `jest-cli ^29.7.0`, `jest-config ^29.7.0`, `jest-diff ^29.7.0`, `jest-docblock ^29.7.0`, `jest-each ^29.7.0`, `jest-environment-node ^29.7.0`, `jest-get-type ^29.6.3`, `jest-haste-map ^29.7.0`, `jest-leak-detector ^29.7.0`, `jest-matcher-utils ^29.7.0`, `jest-message-util ^29.7.0`, `jest-mock ^29.7.0`, `jest-pnp-resolver ^1.2.3`, `jest-regex-util ^29.6.3`, `jest-resolve ^29.7.0`, `jest-resolve-dependencies ^29.7.0`, `jest-runner ^29.7.0`, `jest-runtime ^29.7.0`, `jest-snapshot ^29.7.0`, `jest-util ^29.7.0`, `jest-validate ^29.7.0`, `jest-watcher ^29.7.0`, `jest-worker ^29.7.0`, `js-tokens ^4.0.0`, `js-yaml ^3.14.1`, `jsesc ^3.1.0`, `json-parse-even-better-errors ^2.3.1`, `json5 ^2.2.3`, `kleur ^3.0.3`, `leven ^3.1.0`, `lines-and-columns ^1.2.4`, `locate-path ^5.0.0`, `lru-cache ^5.1.1`, `make-dir ^4.0.0`, `makeerror ^1.0.12`, `math-intrinsics ^1.1.0`, `merge-stream ^2.0.0`, `micromatch ^4.0.8`, `mime-db ^1.52.0`, `mime-types ^2.1.35`, `mimic-fn ^2.1.0`, `minimatch ^3.1.2`, `ms ^2.1.3`, `natural-compare ^1.4.0`, `node-int64 ^0.4.0`, `node-releases ^2.0.19`, `normalize-path ^3.0.0`, `npm-run-path ^4.0.1`, `nwsapi ^2.2.20`, `once ^1.4.0`, `onetime ^5.1.2`, `p-limit ^3.1.0`, `p-locate ^4.1.0`, `p-try ^2.2.0`, `parse-json ^5.2.0`, `parse5 ^7.2.1`, `path-exists ^4.0.0`, `path-is-absolute ^1.0.1`, `path-key ^3.1.1`, `path-parse ^1.0.7`, `picocolors ^1.1.1`, `picomatch ^2.3.1`, `pirates ^4.0.7`, `pkg-dir ^4.2.0`, `pretty-format ^29.7.0`, `prompts ^2.4.2`, `punycode ^2.3.1`, `pure-rand ^6.1.0`, `react-is ^18.3.1`, `require-directory ^2.1.1`, `resolve ^1.22.10`, `resolve-cwd ^3.0.0`, `resolve-from ^5.0.0`, `resolve.exports ^2.0.3`, `rrweb-cssom ^0.8.0`, `safer-buffer ^2.1.2`, `saxes ^6.0.0`, `semver ^6.3.1`, `shebang-command ^2.0.0`, `shebang-regex ^3.0.0`, `signal-exit ^3.0.7`, `sisteransi ^1.0.5`, `slash ^3.0.0`, `source-map ^0.6.1`, `source-map-support ^0.5.13`, `sprintf-js ^1.0.3`, `stack-utils ^2.0.6`, `string-length ^4.0.2`, `string-width ^4.2.3`, `strip-ansi ^6.0.1`, `strip-bom ^4.0.0`, `strip-final-newline ^2.0.0`, `strip-json-comments ^3.1.1`, `supports-color ^7.2.0`, `supports-preserve-symlinks-flag ^1.0.0`, `symbol-tree ^3.2.4`, `test-exclude ^6.0.0`, `tldts ^6.1.85`, `tldts-core ^6.1.85`, `tmpl ^1.0.5`, `to-regex-range ^5.0.1`, `tough-cookie ^5.1.2`, `tr46 ^5.1.0`, `type-detect ^4.0.8`, `type-fest ^0.21.3`, `undici-types ^6.21.0`, `update-browserslist-db ^1.1.3`, `v8-to-istanbul ^9.3.0`, `w3c-xmlserializer ^5.0.0`, `walker ^1.0.8`, `webidl-conversions ^7.0.0`, `whatwg-encoding ^3.1.1`, `whatwg-mimetype ^4.0.0`, `whatwg-url ^14.2.0`, `which ^2.0.2`, `wrap-ansi ^7.0.0`, `wrappy ^1.0.2`, `write-file-atomic ^4.0.2`, `ws ^8.18.1`, `xml-name-validator ^5.0.0`, `xmlchars ^2.2.0`, `y18n ^5.0.8`, `yallist ^3.1.1`, `yargs ^17.7.2`, `yargs-parser ^21.1.1`, `yocto-queue ^0.1.0`.

Development: `@babel/core ^7.26.10`, `@babel/preset-env ^7.26.9`, `jest ^29.7.0`, `jest-environment-jsdom ^29.7.0`, `jsdom ^26.0.0`.

### [llm-lab/frontend/package.json](../../../llm-lab/frontend/package.json)

Runtime: `react 19.1.1`, `react-dom 19.1.1`.

Development: `@types/react 19.1.13`, `@types/react-dom 19.1.9`, `@vitejs/plugin-react 5.0.4`, `typescript 5.9.2`, `vite 7.3.6`.

### [dema-core/dema-core/package.json](../../../dema-core/dema-core/package.json)

Runtime: `better-sqlite3 ^12.4.1`, `cytoscape ^3.34.0`, `cytoscape-dagre ^4.0.0`, `exceljs ^4.4.0`, `html-to-image ^1.11.13`, `lucide-react ^0.487.0`, `react ^18.3.1`, `react-dom ^18.3.1`, `reactflow ^11.11.4`, `yaml ^2.8.3`.

Development: `@electron/rebuild ^4.0.3`, `@testing-library/react ^16.3.2`, `@types/better-sqlite3 ^7.6.13`, `@types/cytoscape ^3.21.9`, `@types/cytoscape-dagre ^2.3.4`, `@types/node ^22.18.0`, `@types/react ^18.3.1`, `@types/react-dom ^18.3.0`, `@typescript-eslint/eslint-plugin ^7.1.1`, `@typescript-eslint/parser ^7.1.1`, `@vitejs/plugin-react ^4.2.1`, `autoprefixer ^10.4.27`, `electron ^41.5.0`, `electron-builder ^26.8.1`, `eslint ^8.57.0`, `eslint-plugin-react-hooks ^4.6.0`, `jsdom ^29.1.1`, `postcss ^8.5.8`, `tailwindcss ^3.4.19`, `tsx ^4.23.1`, `typescript ^5.6.0`, `vite ^7.2.2`, `vite-plugin-electron ^0.28.6`, `vitest ^4.1.10`.

### [twc-bridge/package.json](../../../twc-bridge/package.json)

Runtime: `defuddle ^0.18.1`, `linkedom ^0.18.12`.

Development: None declared.

