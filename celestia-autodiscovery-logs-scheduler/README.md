# Enhancements: CDP logs + Fallbacks + Hourly Scheduler

- CDP endpoints are logged to `logs/cdp/cdp_<source>_<timestamp>.json`.
- Fallback ladder: HTTP primary → HTTP alt → (placeholder) Selenium-only.
- Hourly jobs for GRU→MCO, CGH→SDU, GRU→LIS:
  - Script: `infra/scheduler/setup_hourly.sh`
  - GitHub Action (manual): `Ops - Provision Cloud Scheduler (Hourly Jobs)`
