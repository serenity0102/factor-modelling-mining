#!/bin/bash
set -e

# Update system packages
dnf update -y

# Download clickhouse
curl https://clickhouse.com/ | sh

# Install ClickHouse
sudo ./clickhouse install

# Start Clickhouse Server
clickhouse server

