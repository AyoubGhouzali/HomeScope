# HomeScope — implementation plan

Prepared for Ayoub • 17 September 2026

**Goal:** build a deployed French property application that demonstrates supervised learning, time-series forecasting, reproducible MLOps and cloud engineering.

**Planning estimate:** 50 focused hours across seven days, assuming existing Python, Git and Docker familiarity. This is a week for HomeScope itself. If you have 20–25 hours, use two weeks. Integration and data cleaning are the main uncertainties; these estimates are not measured build times.

## 1. The first release

Start with **apartments in Puy-de-Dôme (department 63)**. This is a proposed scope, chosen for manageable data and relevance to Clermont-Ferrand. Expand only after the first release works.

| User feature | What the user receives | Implementation |
|---|---|---|
| Sale valuation | Estimated sale price, uncertainty range, reference period, comparable recorded sales | LightGBM regression and a calibrated interval |
| Rental context | Indicative monthly rent excluding charges, where an appropriate published benchmark exists | OLL aggregate lookup; no individual rental ML model |
| Inflation comparison | Original purchase cost expressed in another month's euros; purchasing-power comparison | Deterministic calculation using INSEE CPI |
| Market outlook | Historical index and forecasts one and two quarters ahead | Baseline versus a small ARIMA model |
| Transparency | Geographic coverage, source dates, model version and measured errors | Metadata returned by the API and displayed in the UI |

The market forecast will use **Province apartments**, a broader geography than Puy-de-Dôme. Label it accordingly. It does not predict the future selling price of the user's particular apartment.

Use a commune selector, floor area and room count. Do not request an exact address in the first release. Require only features present in training data. Omit accounts, payments, saved portfolios and nationwide coverage.

**Completion means:** a working public URL, an organized public repository, reproducible training, evaluation reports, persisted model versions, automated deployment, monitoring and a demonstrated rollback. No accuracy or latency claim is earned until measured.

## 2. Stack and responsibilities

| Component | Choice | Purpose |
|---|---|---|
| Preparation | Python, Pandas, Parquet | Repeatable cleaning and compact datasets |
| Valuation | LightGBM, scikit-learn utilities | Fast CPU training and evaluation |
| Forecasting | statsmodels | Small, interpretable quarterly forecasting experiment |
| Tracking and registry | MLflow | Runs, metrics, artifacts and registered versions |
| Application | FastAPI, Jinja2, simple JavaScript charts | One deployable service containing API and UI |
| Packaging | Docker | Identical serving environment locally and in the cloud |
| Automation | GitHub Actions | Tests, source checks, training and releases |
| Cloud | Google Cloud Run, Artifact Registry, Cloud Storage | Autoscaled service, container images and private artifacts |
| Infrastructure | Terraform | Reproducible cloud configuration and traffic changes |
| Observability | Cloud Logging/Monitoring; local Prometheus/Grafana | Cloud operations and a reproducible local monitoring demo |

Use Google Cloud as the default implementation target. Keep training outside request handling. Bundle an immutable model and lookup tables in each serving image, so predictions do not depend on a live tracking server.

Kubernetes, Helm and Airflow belong in a later extension. GitHub Actions is sufficient for this project's small scheduled pipeline.

## 3. Data sources and acquisition

### A. Transactions: DVF

Use the official [geolocated DVF dataset](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees) and its [department-level downloads](https://files.data.gouv.fr/geo-dvf/latest/csv/2025/departements/). The department 63 file is available. Begin with 2021–2025 and confirm each download exists before running the pipeline.

Download pattern:

```text
https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/departements/63.csv.gz
```

Preserve original files unchanged. Record URL, retrieval time, SHA-256, row count, schema, observation dates and license in a source manifest. The `latest` path is mutable; it is not a reproducible version by itself.

DVF releases arrive in batches, with revisions. A transaction's date is different from the date its data became available. See the [original DVF publication](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres). Store both observation dates and the date you first retrieved a release.

### B. Rents: OLL

Use [OLL results by agglomeration](https://www.data.gouv.fr/datasets/resultats-des-observatoires-locaux-des-loyers-par-agglomeration). The [observatory directory](https://www.observatoires-des-loyers.org/decouvrir-le-reseau/lannuaire-des-observatoires) includes Grand Clermont. Verify the actual downloaded file's geography, year, property segments and suppression rules on day one.

These public data are aggregate benchmarks. Store available median €/m², quartiles, sample count, year and segment definitions. Do not invent dwelling-level training examples from aggregate statistics. Do not combine separate marginal breakdowns into a nonexistent joint segment. If a suitable benchmark is missing, display “No published benchmark for this selection.” See the [OLL data access explanation](https://www.observatoires-des-loyers.org/decouvrir-le-reseau/a-propos-des-donnees).

### C. Inflation: INSEE CPI / IPC

Select a monthly **France, all households, all items** series from the [INSEE CPI catalogue](https://www.insee.fr/fr/statistiques/series/129209311). Confirm the exact series identifier and metadata during ingestion; do not silently substitute an excluding-tobacco series.

Download a consistent series with enough back history. Record its base and unit. Never divide a raw base-2015 observation by a raw base-2025 observation. Use one consistently rebased series covering both requested months.

### D. Market index: Notaires–INSEE

Use a quarterly **Province apartments index level**, preferably seasonally adjusted. The [September 2026 housing-price publication](https://www.insee.fr/fr/statistiques/9040119) provides a source for locating the series and its downloadable history. Pin the exact series identifier in configuration after checking its title, geography, frequency, unit and adjustment status.

Use index levels, not a column containing quarterly percentage changes. Obtain the longest consistent history available, ideally at least 60 quarters. The [index methodology](https://www.insee.fr/fr/metadonnees/source/indicateur/p1643/description) explains why this is preferable to treating a changing mix of DVF sales as a constant-quality market index.

**Day-one data contract:** every source must have a reproducible file, checked schema, reference dates and documented meaning before model development starts. Exact INSEE series IDs and the OLL resource version are implementation checks, not identifiers assumed by this plan.

## 4. Repository structure

Create one repository, `homescope`, with these responsibilities:

| Path | Contents |
|---|---|
| `README.md` | Demo link, screenshots, quick start, results and architecture |
| `pyproject.toml`, lockfile | Pinned dependencies; separate training and serving dependencies |
| `configs/sources.yaml` | Download URLs, selected series IDs, schema expectations |
| `configs/model.yaml` | Features, splits, seeds, training budget and quality gates |
| `src/homescope/data/` | Fetch, validate, clean, split and manifest code |
| `src/homescope/models/` | Valuation, calibration, forecasting and evaluation |
| `src/homescope/services/` | Comparables, rental benchmarks, inflation and model loading |
| `src/homescope/api/` | Request schemas, routes and middleware |
| `src/homescope/web/` | Templates and static assets |
| `src/homescope/ops/` | Registry snapshots, source checks, monitoring and release helpers |
| `tests/fixtures/` | Small synthetic examples, including tricky transaction records |
| `tests/` | Data, model-contract, calculation and API checks |
| `infra/terraform/` | Bootstrap and application infrastructure |
| `monitoring/` | Prometheus configuration and exported Grafana dashboard |
| `.github/workflows/` | `ci.yml`, `refresh.yml`, `release.yml` |
| `docs/` | Data card, model cards, architecture decisions, runbook |
| `reports/` | Small evaluation summaries and plots suitable for Git |
| `Dockerfile`, `compose.yaml`, `Makefile` | Build and local operation |

Ignore raw data, trained binaries, credentials, Terraform state and local MLflow databases. Store large versioned artifacts in private Cloud Storage. Commit source manifests and small, non-sensitive reports.

## 5. Seven-day implementation sequence

### Day 1 — repository and trusted data • 7 hours

1. Create the repository, Python environment, dependency lockfile and configuration files. Add formatting/linting and a basic test command.
2. Download the scoped DVF files and the three supporting sources. Create a manifest for each snapshot.
3. Inspect DVF schema and transaction structure before filtering by property type.
4. Implement a conservative cleaning policy: initially retain unambiguous single-row, single-apartment sales; exclude records indicating additional units, non-residential property or unresolved mixed lots. Expand to multirow transactions only after explicit, tested reconstruction rules exist.
5. Group and inspect by mutation identifier within a snapshot before selecting apartments. A sale amount may be repeated across rows: never sum repeated prices or assign a mixed sale's total price to one apartment. Mutation IDs are not a cross-release identity guarantee.
6. Keep ordinary sales with positive price and surface. Set documented input bounds for the supported product, for example 15–200 m² and 1–8 rooms; these are scope choices, not universal definitions of valid housing.
7. Keep commune codes as strings, preserve dates, and reject unusable feature values. Record counts for each exclusion and compare retained versus excluded sales by commune and size.
8. Export `clean.parquet`, `data_manifest.json` and `data_quality.json`.

**Gate:** a meaningful sample remains across time periods and communes. A planning target is 5,000 training records and 500 evaluation records, not a guaranteed yield. If cleaning produces too little data, first inspect exclusions, then narrow supported communes or deliberately broaden the source scope. Do not lower quality rules merely to reach a row count.

**Learn:** ingestion, data contracts, transaction semantics, reproducibility and coverage bias.

### Day 2 — valuation model and honest evaluation • 7 hours

1. Define the prediction unit: one apartment sale. Target: `log(sale_price)`.
2. Start with surface, rooms, commune and transaction-time features. Use the same feature transformations in training and serving. Keep any location mapping fixed and versioned.
3. Exclude price, price per m², future neighborhood medians and unavailable amenities from inputs. Train-derived categorical mappings and statistics must use training rows only.
4. Build a baseline: training-set median €/m² by commune and room group, falling back to department level when support is low. Multiply by the requested surface.
5. Use the following chronological experiment, if the acquired snapshot supports it:

| Period | Role |
|---|---|
| 2021–2023 | Initial training |
| 2024 | Hyperparameter selection |
| 2025 H1 | Interval calibration |
| 2025 H2 | Final untouched test |

6. Try at most 5–10 small LightGBM configurations with a fixed seed. Select using 2024 validation. Refit the chosen configuration on 2021–2024, then calibrate on 2025 H1 and test once on 2025 H2. Do not reuse final test results to tune the model.
7. Fit preprocessing and the baseline again using the same final training window. Save them with the model. Deploy this exact evaluated bundle; silently refitting after evaluation invalidates its reported results.
8. Create a split-conformal interval from absolute log-price residuals on the calibration set. For nominal 90% coverage, use the finite-sample corrected order statistic at `ceil((n+1)*0.90)` when the sample permits it, then exponentiate the prediction bounds. Measure coverage and width on the test set. Temporal shift means nominal coverage is not assured.
9. Report euro MAE, median absolute percentage error, interval coverage/width and errors by commune and surface band, with group sample counts. Report unsupported or tiny groups clearly.
10. Keep the baseline as champion if LightGBM does not improve the predefined validation criteria. A complex model does not automatically deserve deployment.

Because this uses a current data snapshot, call the evaluation a **retrospective chronological backtest**. It is not a reconstruction of what information was published at every historic date. Preserve future release snapshots to enable stronger availability-aware evaluation later.

The application should display training end, source coverage and evaluation period. It must not advertise an unvalidated 2026 estimate as an exact current market appraisal. For the MVP, show the supported reference period; current-period nowcasting is a later evaluated feature.

**Gate:** saved baseline, chosen model, preprocessing, calibration artifact and reproducible report, with no transaction crossing splits.

**Learn:** leakage prevention, regression, model selection, temporal validation, uncertainty and segment-level evaluation.

### Day 3 — forecasting, rents and inflation • 6 hours

1. Parse the quarterly housing index; check duplicate quarters, gaps, adjustment status and revisions. Preserve the source vintage.
2. Reserve the latest eight quarters for final rolling-origin evaluation, if history is sufficient. Select models using earlier rolling origins, ideally starting with at least 40 quarters of training.
3. Compare a last-observed-value forecast with a small ARIMA set such as `(0,1,0)`, `(1,1,0)`, `(0,1,1)` and `(1,1,1)`. Fall back to the baseline if fitting fails or it performs better.
4. At every origin, use only preceding observations. Evaluate one-quarter and two-quarter horizons separately; ignore unavailable future targets. Report index-point MAE and forecast-interval coverage. Avoid seasonal terms solely because the data are quarterly: CVS data already have seasonality removed.
5. Refit the selected forecasting specification on the available index history and store the next two quarterly predictions. Label the evaluation's historical-vintage limitation, since revised index values can affect backtests.
6. Implement rental lookup using one published segment compatible with the selection. An indicative rent is `benchmark_euros_per_m2 * surface`. If published quartiles are shown after scaling, call them benchmark ranges, not calibrated dwelling-level prediction intervals. Always show geography, year and charges treatment.
7. Implement the inflation functions below. Require supported published months and positive CPI observations. Show the actual month used instead of quietly replacing it.

```text
cumulative_inflation = CPI_end / CPI_start - 1
adjusted_purchase_cost = purchase_price * CPI_end / CPI_start
real_value_change = estimated_value / adjusted_purchase_cost - 1
```

For the last calculation, the estimated value and `CPI_end` must refer to the same valuation period. Do not compare a stale valuation with today's CPI and call it current real growth. Users can separately calculate purchase-cost inflation through the latest published CPI month.

Synthetic test: €200,000 purchased at CPI 100 becomes €220,000 at CPI 110. A €240,000 valuation for that same ending period implies approximately 9.09% real value growth. This excludes fees, financing, tax and improvements; label it as a purchasing-power comparison, not realized profit. CPI is not a property-price forecast or a legal rent-revision formula.

**Gate:** forecast report, deterministic rental lookup and passing numerical inflation checks.

**Learn:** time-series baselines, rolling backtests, uncertainty, economic interpretation and separation of ML from ordinary application logic.

### Day 4 — working application and container • 7 hours

1. Build a single responsive page with a form and four result areas: valuation, rental context, inflation comparison and market trend.
2. Implement these API contracts:

| Route | Responsibility |
|---|---|
| `GET /healthz` | Process is alive |
| `GET /readyz` | Required model and data bundle loaded successfully |
| `GET /version` | Release, commit, models and source reference dates |
| `POST /api/valuation` | Validate commune/surface/rooms; return price, bounds and metadata |
| `GET /api/rent-benchmark` | Return a supported benchmark or explicit unavailable result |
| `POST /api/inflation` | Calculate the documented CPI comparisons |
| `GET /api/market-forecast` | Return index history, forecast and geography |
| `GET /metrics` | Local monitoring endpoint; disabled or protected in public deployment |

3. Load models once at startup. Do not fetch full datasets or train inside a request. Fail readiness if bundle checksums or schemas are incompatible.
4. Add comparable transactions: same commune, nearby surface and room count, clearly labeled transaction dates. Keep a compact lookup artifact; show a few examples and omit an exact address. Comparables support interpretation and are not an independently validated confidence measure.
5. Validate numeric ranges and supported geography. Return helpful errors for unknown communes and unavailable rental segments. Avoid invented results when a lookup fails.
6. Add a Docker image that runs as a non-root user, binds to `0.0.0.0` on the platform port and includes only required serving files. Provide an explicit local development command.
7. Test the container through actual HTTP requests, including invalid input, missing benchmark and bundle-loading failure. Check the UI on mobile width.

**Gate:** another person can run the container, enter a supported apartment and understand the result and its reference period.

**Learn:** API contracts, validation, model serving, startup behavior, containerization and user-facing communication.

### Day 5 — MLflow, persistent artifacts and cloud release • 9 hours

**A. Tracking and registry**

1. Create MLflow experiments for valuation and forecasting. Log parameters, source hashes, split boundaries, seed, Git commit, runtime, evaluation reports and model signature.
2. Register separate valuation and forecasting model versions. Use `candidate` and `champion` aliases, with a release manifest pinning exact version numbers, artifacts and image digest. MLflow supports this separation between runs and registered models; see its [tracking](https://mlflow.org/docs/latest/ml/tracking/) and [registry](https://mlflow.org/docs/latest/ml/model-registry/) documentation.
3. Use a deliberately small, **single-writer registry design** for the solo MVP: local SQLite for MLflow metadata, private Cloud Storage for artifacts and versioned metadata snapshots. MLflow supports a [SQLite backend](https://mlflow.org/docs/latest/self-hosting/architecture/backend-store/) and [GCS artifacts](https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/). The snapshot workflow below is this project's implementation choice, not a managed MLflow architecture.
4. In CI, restore the latest metadata snapshot to the runner, use a local `sqlite:///...` tracking URI, execute one writer, then create a consistent backup using SQLite's backup API. Persist an immutable snapshot and update a pointer using a storage-generation precondition. Never mount a live SQLite database on object storage.
5. Serialize all training and registry-writing release jobs with the same GitHub Actions concurrency group, with in-progress cancellation disabled. A local UI may inspect a restored copy but must not write back to the authoritative snapshot.
6. Test restoring the registry and loading an older model. Keep the serving application independent of this database. A later multi-user version should use a proper shared database and private MLflow service.

**B. Cloud infrastructure**

7. Create a Google Cloud project and choose one European region, such as `europe-west1`. Enable the required Cloud Run, Artifact Registry, Storage and IAM services. Set a budget alert before deployment.
8. Bootstrap a private versioned Terraform state bucket, then configure a GCS backend. Keep state out of Git. Google provides a [versioned bucket Terraform example](https://docs.cloud.google.com/storage/docs/samples/storage-bucket-tf-with-versioning).
9. Define the artifact bucket, container repository, deployment/runtime identities and Cloud Run service in Terraform. The runtime identity needs no artifact-bucket access when all serving files are baked into the image.
10. Configure GitHub OIDC / Workload Identity Federation scoped to the repository and trusted branch. Grant only required deployment and artifact permissions. Follow the official [Google GitHub authentication action](https://github.com/google-github-actions/auth); do not commit a service-account JSON key.
11. Start with 1 vCPU, 1 GiB RAM, minimum instances 0, maximum instances 2 and concurrency 8. These are initial settings to benchmark, not guaranteed sizing. Increase memory if the measured bundle requires it. Cloud Run documents its [autoscaling behavior](https://docs.cloud.google.com/run/docs/about-instance-autoscaling).
12. Push an image identified by commit and digest. Deploy the first revision, verify health and the user flow, and record its URL. Public access should apply to the demo service, while artifacts, registry snapshots and state remain private. See [Cloud Run access management](https://docs.cloud.google.com/run/docs/securing/managing-access).

**Gate:** public HTTPS application, pinned release manifest, reproducible infrastructure and a successful registry-restore check.

### Day 6 — automation, monitoring and rollback • 8 hours

**CI on every pull request**

1. Run formatting, linting, unit tests, schema tests and a small fixture-based pipeline. Build the serving image and run HTTP smoke checks. Untrusted pull requests receive no cloud deployment credentials.
2. Test meaningful failure cases: duplicated multirow sale amounts, leakage across splits, unseen commune, inconsistent CPI bases, unsupported rental segment and a missing model artifact.

**Scheduled refresh**

3. Schedule weekly source checks and add a manual trigger. Compare hashes and source metadata. If nothing changed, exit without training.
4. Refresh only affected components: CPI/OLL changes update lookup data; a new index observation updates forecasting; new usable DVF data can trigger valuation retraining. Do not retrain the valuation model simply because CPI changed.
5. Run validation before training. Reject broken schema, invalid units and overlapping splits. Warn on major row-count changes and inspect them before accepting a new dataset.
6. Train a candidate and compare it with the incumbent on the same fresh, agreed evaluation window. Predefine acceptable MAE, interval coverage, subgroup and latency regressions in configuration. Keep a final holdout separate from repeated tuning; the 2025 test does not remain an endlessly reusable source of unbiased improvement claims.

**Controlled release**

7. Build a new immutable image for an accepted candidate. Use Terraform as the owner of image and traffic configuration; avoid unmanaged console changes that create drift.
8. Probe the candidate revision before public traffic. For later releases, shift 10% to the candidate and retain 90% on the previous revision. Run a bounded smoke/load test, for example 100 requests with at most five concurrent clients.
9. Promote to 100% only when service checks pass. Low demo traffic cannot establish live model accuracy; offline evaluation is the model-quality gate. On failure, return 100% to the previous revision. Cloud Run supports [traffic splitting and rollback](https://docs.cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration).
10. Change the `champion` alias only after successful promotion, and persist the registry snapshot. If metadata persistence fails after deployment, recover using the deployed release manifest; do not lose track of which model is serving. Keep deployment retries idempotent.

**Monitoring**

| Signal | How to measure | Action |
|---|---|---|
| Service health | Request counts, 5xx errors, p50/p95 latency, startup failures | Investigate or roll back a faulty release |
| Input quality | Missing fields, invalid values, unknown communes | Validate inputs and inspect product coverage |
| Input drift | Recent surface/room distributions and commune mix versus reference data | Flag for investigation after sufficient traffic |
| Valuation quality | Offline errors on newly available labeled transactions | Evaluate a retrained candidate |
| Forecast quality | Error when a predicted quarter's index is published | Update report and compare forecasting models |
| Data freshness | Latest source observation and retrieval dates | Refresh or display a stale-data notice |

11. Use managed cloud logs and metrics for the deployed service. Log request ID, route, duration, release and coarse diagnostics; avoid raw addresses and high-cardinality metrics.
12. Run Prometheus and Grafana locally through Compose and export a dashboard into the repository. Label local demonstrations clearly. Do not assume one scraped Cloud Run instance represents an autoscaling service.
13. Require a minimum sample before drift checks, for example 200 requests. If traffic is insufficient, show “insufficient data.” Replay historical or deliberately shifted data to demonstrate the alert, labeled as a simulation.

**Critical distinction:** input drift does not prove prediction error. User-entered properties usually have no subsequent verified sale label. New DVF releases support retrospective population-level evaluation; they do not automatically reveal the error of every user request. Automatic retraining can create a candidate when new labeled data arrive, but automatic promotion must still pass evaluation and service checks.

**Gate:** one automated refresh run, one demonstrated blocked bad candidate, and one successful deployment rollback.

### Day 7 — verification, documentation and portfolio evidence • 6 hours

1. Reproduce the pipeline from the documented source snapshot in a clean environment. Check that release metadata resolves to the right artifacts and commit.
2. Measure actual training time and serving latency on named hardware/configuration. Separate warm requests from cold starts. Report the workload and sample count beside results.
3. Finish the data card, both model cards and the operations runbook. Explain data exclusions, geographic limits, retrospective evaluation, inflation interpretation and the distinction between rental benchmarks and predictions.
4. Put the demo URL, one screenshot, quick-start commands and a compact results table near the top of the README. Include architecture, CI status and rollback instructions below.
5. Record a short demonstration: enter an apartment, explain the reference dates, show MLflow results, trigger a source check and show a revision rollback.
6. Inspect cloud storage/image retention and remove disposable test resources. Preserve the live release and the previous known-good release.

**Gate:** the user flow works, someone else can run the repository, and every public performance claim is backed by a report.

## 6. Command interface to implement

These are proposed Makefile targets to build, not commands from an existing repository:

```bash
make setup          # install locked dependencies
make fetch          # download configured source snapshots
make validate       # schemas, dates, units and data-quality rules
make prepare        # clean transactions and create temporal splits
make train          # train valuation and forecasting experiments
make evaluate       # generate metrics and candidate-gate report
make package        # create immutable serving bundle and manifest
make serve          # start local API and UI
make test           # meaningful unit and integration checks
make monitor        # local Prometheus and Grafana
make infra-plan     # review Terraform changes
make deploy         # release the selected image and traffic configuration
make rollback       # restore the recorded previous release
```

Keep the implementation in Python modules; the Makefile should call those modules rather than contain the application logic. Each pipeline stage should accept explicit input/output paths, fail clearly and avoid mutating raw files.

## 7. Costs, training speed and scope controls

- **Training:** CPU-only. A moderate LightGBM fit on tens of thousands of rows should be a small task, often seconds to minutes, but this is an estimate to benchmark. Data preparation and repeated experiments can take longer. No GPU or paid LLM API is required.
- **Local development:** the selected software can run locally without cloud compute fees. Use small fixtures in CI and cap the experiment count.
- **Cloud trial:** eligible new Google Cloud users currently receive $300 credit over 90 days; signup requires payment verification. The free trial is not an indefinite hosting guarantee. Services stop when the trial ends unless the account is upgraded. See the [official trial terms](https://docs.cloud.google.com/free/docs/free-cloud-features).
- **Ongoing cloud:** Cloud Run has free allowances, but storage, images, builds and network use can still cost money. Check the [current pricing](https://cloud.google.com/run/pricing) for the chosen region. Set a small personal budget, such as $5–10, as a target to monitor rather than a promised bill. Budget alerts are not hard spending caps.
- **Cost controls:** scale to zero, cap instance count, keep artifacts small, bound load tests and configure storage/image lifecycle cleanup. Avoid an always-on GPU or database for this solo MVP.

If the schedule slips, reduce styling, comparable-search sophistication and tuning first. Keep both models, truthful evaluation, the deployed application and a working deployment pipeline. If those still do not fit, extend the calendar; do not call unfinished monitoring or rollback complete.

## 8. Acceptance checklist

- [ ] Geographic and property-type scope is visible in the UI.
- [ ] Four official sources are pinned by resource, date and hash.
- [ ] Multirow and mixed-property DVF sales are handled conservatively.
- [ ] Cleaning exclusions and resulting coverage are documented.
- [ ] Training transformations cannot access future targets.
- [ ] Valuation baseline and LightGBM are compared chronologically.
- [ ] Interval coverage and width are measured on untouched data.
- [ ] Time-series backtests evaluate one- and two-quarter horizons separately.
- [ ] Forecast geography is clearly distinguished from the property's location.
- [ ] Rents are labeled as aggregate benchmarks with source year and coverage.
- [ ] CPI calculations use consistent units and matching reference periods.
- [ ] Unsupported inputs return useful errors or unavailable results.
- [ ] A saved serving bundle reproduces offline predictions.
- [ ] MLflow runs and registry metadata survive a restore.
- [ ] GitHub CI passes from a clean environment.
- [ ] Cloud resources and traffic configuration are defined in Terraform.
- [ ] Public application and private artifacts have appropriate access settings.
- [ ] Weekly source checks skip unnecessary training.
- [ ] A candidate that fails quality checks cannot become champion.
- [ ] Monitoring distinguishes service errors, drift and labeled model errors.
- [ ] Canary release and rollback have both been demonstrated.
- [ ] Actual training time, test errors and measured latency appear in reports.
- [ ] README includes demo, reproduction instructions, limitations and evidence.

## 9. What this earns on your CV

Use a title such as **HomeScope — Property Valuation, Forecasting & MLOps Platform**.

After completing the work, describe the demonstrated behavior:

- Built a deployed French property application combining sale-price estimation, rental benchmarks, inflation comparisons and housing-index forecasts.
- Implemented reproducible data pipelines, chronological evaluation, MLflow model versioning and automated candidate validation.
- Provisioned Cloud Run infrastructure with Terraform and delivered containerized releases with monitoring, traffic splitting and rollback.

Add measured results only after they exist: transactions retained, improvement versus baseline, MAE, interval coverage, forecast error, training time and latency. A credible modest result with excellent engineering is stronger than an unsubstantiated accuracy claim.

## 10. Later extensions

1. Broaden coverage deliberately, with additional geographic evaluation.
2. Add publication-time snapshots for stronger historical backtests.
3. Validate a current-market adjustment using the relevant housing index; keep CPI separate.
4. Add individual rental prediction only if a suitable lawful dwelling-level dataset becomes available.
5. Move MLflow to a private service backed by PostgreSQL for concurrent users.
6. Add Airflow when pipeline dependencies justify it, or port serving to Kubernetes/Helm as a separate infrastructure exercise.
7. Add DPE or neighborhood features only after establishing a reliable join and matching inference-time availability.

**First implementation task:** download one department-63 DVF file, inspect mutation groups, and produce a cleaning report. That establishes whether the chosen scope supports the rest of the plan.
