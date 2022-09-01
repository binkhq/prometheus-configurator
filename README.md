# yamlmerge

Provides an easy to use mechanism for merging multiple YAML files into a single file, designed for Prometheus but can be used by pretty much anything where splitting yaml files might be helpful.

## Usage

### Kubernetes / Kustomize / Flux 2

The below example shows deployment of Prometheus to a Kubernetes Cluster with a global config, and two additional sets of scraping config. Kustomize will create a Config Map which gets mounted inside the `yamlmerge` container, `yamlmerge` will then output a single file (`/etc/prometheus/prometheus.yaml`) to an `emptydir` volume, which then gets mounted inside the main prometheus container.

This process is useful for if you have a common prometheus config intended to be shared between all clusters, but want to use `configMapGenerator` with the `behavior: merge` option to add additional config in a specific cluster.

`kustomization.yaml`:
```yaml
---
resources:
  - deploy.yaml

configMapGenerator:
  - name: prometheus-config-source
    files:
      - config/global.yaml
      - config/kube-state-metrics.yaml
      - config/pods.yaml
```

`deploy.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: default
  labels:
    app: prometheus
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      initContainers:
        - name: yamlmerge-prometheus
          image: ghcr.io/binkhq/yamlmerge:latest
          env:
            - name: source_directory
              value: /etc/prometheus/conf.d/
            - name: destination_file
              value: /etc/prometheus/prometheus.yaml
          volumeMounts:
            - mountPath: /etc/prometheus/
              name: prometheus-config
            - mountPath: /etc/prometheus/conf.d/
              name: prometheus-config-source
      containers:
        - name: prometheus
          image: docker.io/prom/prometheus:v2.38.0
          args:
            - --config.file=/etc/prometheus/prometheus.yaml
          ports:
            - containerPort: 9090
              name: prometheus
          volumeMounts:
            - name: prometheus-config
              mountPath: /etc/prometheus/
      volumes:
        - name: prometheus-config-source
          configMap:
            name: prometheus-config-source
        - name: prometheus-config
          emptyDir: {}
      serviceAccountName: prometheus
```

`config/global.yaml`:
```yaml
global:
  evaluation_interval: 10s
  scrape_interval: 10s
  scrape_timeout: 10s

```

`config/kube-state-metrics.yaml`
```yaml
---
scrape_configs:
  - job_name: kube-state-metrics
    static_configs:
      - targets: [kube-state-metrics.kube-system.svc.cluster.local:9100]
```

`config/pods.yaml`:
```yaml
scrape_configs:
  - job_name: pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_job]
        action: replace
        target_label: job
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_instance]
        action: replace
        target_label: instance
```

## How Bink uses this

Bink deploys a Prometheus instance in a very similar style to the above example. We have common config that is shared between all of our clusters such as the scraping of `kube-state-metrics`. However, some clusters have specific monitoring requirements, such as keeping an eye on the expiration of a specific TLS Certificate - this allows us to `merge` that config with a few lines added to that environments `kustomization.yaml`.
