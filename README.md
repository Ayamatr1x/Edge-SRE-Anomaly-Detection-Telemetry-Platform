# Edge SRE & Anomaly Detection Telemetry Platform

A self-hosted observability and anomaly detection platform built for a resource-constrained (4GB RAM) Ubuntu Server. Telemetry flows from bare metal, through a lightweight metrics pipeline, into a statistical ML model that flags abnormal system behavior — with automated alerting to Discord/Slack and dashboards in Grafana.

## Architecture

```
┌─────────────────────┐
│   Administrator      │
│ (SSH / kubectl/helm) │
└──────────┬───────────┘
           │
           ▼
┌─────────────────────────────┐        ┌────────────────────────────┐
│   Bare-Metal Host             │        │  Dockerized Microservices   │
│   Ubuntu Server 24.04          │──────▶│                              │
│   (4GB RAM)                    │        │  Stack A: Secure Access      │
│   - OS & kernel tuning          │        │   Nginx Proxy Manager        │
│   - System monitoring (Glances) │        │   → Cloudflare Tunnel        │
│   - Docker Engine + bridge net  │        │                              │
└─────────────────────────────┘        │  Stack B: Telemetry & ML     │
                                          │   Vector → VictoriaMetrics   │
                                          │   → Python Anomaly Worker    │
                                          │      (Isolation Forest)      │
                                          │                              │
                                          │  Stack C: Visualization       │
                                          │   Grafana → Alerting Engine  │
                                          │   → Discord / Slack          │
                                          └────────────────────────────┘
```

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Host OS | Ubuntu Server 24.04 | Bare-metal base, kernel-tuned for a 4GB RAM footprint |
| Containerization | Docker Engine + Compose | Isolated, reproducible microservices on a bridge network |
| Metrics Shipper | [Vector](https://vector.dev/) | Lightweight collection of host metrics (CPU, memory, disk, network, load) |
| Time-Series DB | [VictoriaMetrics](https://victoriametrics.com/) | Prometheus-compatible TSDB, <100MB RAM footprint |
| Anomaly Detection | Python + scikit-learn | Isolation Forest model scoring recent metric windows |
| Dashboards | [Grafana](https://grafana.com/) | Visualizes host metrics and anomaly scores |
| Alerting | Grafana Alerting + Webhooks | Pushes detected anomalies to Discord/Slack |
| Reverse Proxy | Nginx Proxy Manager | SSL/TLS termination and routing |
| Ingress | Cloudflare Tunnel | Zero-trust external access, no exposed inbound ports |

## Features

- **Bare-metal optimization** — tuned to run the full observability stack on just 4GB of RAM
- **SRE observability** — real-time host metrics via Vector and VictoriaMetrics
- **Statistical anomaly detection** — unsupervised Isolation Forest model flags abnormal system behavior without labeled training data
- **Proactive alerting pipeline** — anomalies automatically pushed to Discord/Slack, no manual dashboard-watching required
- **Zero-trust ingress** — Grafana exposed externally through Cloudflare Tunnel with no open inbound ports on the host

## Getting Started

### Prerequisites

- Ubuntu Server 24.04 (or similar Linux distro)
- Docker Engine and Docker Compose
- (Optional) A Cloudflare account for tunnel-based external access

### Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/Ayamatr1x/Edge-SRE-Anomaly-Detection-Telemetry-Platform.git
   cd Edge-SRE-Anomaly-Detection-Telemetry-Platform
   ```

2. Create a `.env` file for secrets (never commit this):
   ```bash
   echo "TUNNEL_TOKEN=your_cloudflare_tunnel_token" > .env
   ```

3. Bring up the stack:
   ```bash
   docker compose up -d --build
   ```

4. Verify all services are healthy:
   ```bash
   docker compose ps
   ```

5. Access Grafana at `http://<server-ip>:3000` (default login `admin`/`admin`, forces a password reset on first login).

6. Add VictoriaMetrics as a Prometheus-compatible data source in Grafana:
   - URL: `http://victoriametrics:8428`

7. Confirm metrics are flowing via **Explore**, e.g.:
   ```
   sum by (mode) (rate(host_cpu_seconds_total[5m]))
   ```

8. Confirm anomaly scores are being generated:
   ```bash
   docker compose logs -f anomaly-worker
   ```

9. Set up alerting: Grafana → Alerting → Contact points → add a Discord/Slack webhook, then create an alert rule on `anomaly_score == 1`.

## Project Structure

```
.
├── docker-compose.yaml
├── vector.yaml
├── anomaly-worker/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── worker.py
├── grafana-data/       (gitignored — runtime state)
├── vmdata/             (gitignored — runtime state)
├── npm/                (gitignored — runtime state)
└── .env                (gitignored — secrets)
```

## Roadmap

- [ ] GitOps-driven deployment via CI/CD
- [ ] Kubernetes/Helm chart for multi-node deployment
- [ ] Additional anomaly models (seasonal decomposition, LSTM-based detection)
- [ ] Expanded Grafana dashboards (per-service resource breakdowns)

## License

MIT
