# Prometheus Configurator

Provides a simple interface for converting multiple YAML files into a single file for Prometheus to consume, designed to be used as an init container within a kubernetes pod

## Usage

Mount a ConfigMap `/etc/prometheus/conf.d/` and then create an `empty_dir` volume on `/etc/prometheus/`. 

Example: 
TODO: write example.
