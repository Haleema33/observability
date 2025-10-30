# Observability Helm Charts

This repository contains Helm charts for a complete observability stack using Grafana, Loki, and Promtail.

## Charts Overview

### 1. Grafana Chart (`grafana-chart/`)
- **Purpose**: Visualization and dashboarding
- **Key Customization Values**:
  - `adminUser`/`adminPassword`: Default admin credentials (CHANGE THESE!)
  - `persistence.enabled`/`size`: Storage for dashboards and data
  - `datasources`: Configure Loki and other data sources
  - `service.type`: Set to `LoadBalancer` for external access

### 2. Loki Chart (`loki-chart/`)
- **Purpose**: Log aggregation and storage
- **Key Customization Values**:
  - `storage.type`: Use `filesystem` for dev, `s3`/`gcs`/`azure` for production
  - `config.limits_config.retention_period`: How long to keep logs (default: 7 days)
  - `persistence.size`: Local storage size for filesystem mode
  - `config.storage_config`: Configure object storage for production

### 3. Promtail Chart (`promtail-chart/`)
- **Purpose**: Log collection agent
- **Key Customization Values**:
  - `config.clients`: Loki endpoint configuration
  - `config.scrape_configs`: What logs to collect and how to label them
  - `daemonset.enabled`: Run on all nodes (recommended)
  - `volumes`/`volumeMounts`: Additional log paths to collect

## Quick Start

### Deploy the Stack

```bash
# Install Loki first (log storage)
helm install loki ./loki-chart

# Install Promtail (log collection)
helm install promtail ./promtail-chart

# Install Grafana (visualization)
helm install grafana ./grafana-chart
```

### Access Grafana

```bash
# Port forward to access Grafana
kubectl port-forward svc/grafana 3000:3000

# Default credentials: admin/admin123 (CHANGE THESE!)
```

## Production Considerations

### Loki Storage
For production, configure object storage in `loki-chart/values.yaml`:

```yaml
storage:
  type: s3
  s3:
    endpoint: s3.amazonaws.com
    bucket_name: loki-chunks
    region: us-east-1
    access_key_id: <your-access-key>
    secret_access_key: <your-secret-key>
```

### Grafana Security
- Change default admin credentials
- Enable TLS/HTTPS
- Configure proper authentication (LDAP, OAuth, etc.)
- Set up proper RBAC

### Promtail Configuration
- Adjust scrape configs for your specific log formats
- Add custom labels for better log organization
- Configure log parsing pipelines for structured logs

### Resource Scaling
- Increase resources based on log volume
- Consider running multiple Loki replicas
- Adjust retention policies based on compliance needs

## Customization Examples

### Custom Log Scraping
Add to `promtail-chart/values.yaml`:

```yaml
config:
  scrape_configs:
    - job_name: nginx-logs
      static_configs:
        - targets:
            - localhost
          labels:
            job: nginx
            __path__: /var/log/nginx/*.log
```

### Grafana Datasource
The Grafana chart automatically configures Loki as a datasource. To add more:

```yaml
datasources:
  - name: Loki
    type: loki
    url: http://loki:3100
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
```

## Troubleshooting

### Common Issues
1. **Promtail can't access logs**: Check volume mounts and security context
2. **Loki storage issues**: Verify PVC creation and storage class
3. **Grafana can't connect to Loki**: Check service names and ports
4. **High resource usage**: Adjust retention periods and resource limits

### Useful Commands
```bash
# Check pod logs
kubectl logs -f deployment/loki
kubectl logs -f daemonset/promtail
kubectl logs -f deployment/grafana

# Check storage
kubectl get pvc
kubectl describe pvc loki

# Test connectivity
kubectl exec -it deployment/grafana -- wget -qO- http://loki:3100/ready
```