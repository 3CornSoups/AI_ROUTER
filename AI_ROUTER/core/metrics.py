from prometheus_client import Counter, Histogram, Gauge, start_http_server
from config.settings import settings
import time

class MetricsExporter:
    """暴露网关监控指标。"""
    
    def __init__(self):
        # QPS 计数
        self.request_counter = Counter(
            "gateway_requests_total",
            "Total number of requests",
            ["method", "path", "model", "status"]
        )
        
        # 延迟直方图
        self.request_latency = Histogram(
            "gateway_request_latency_seconds",
            "Request latency in seconds",
            ["model"]
        )
        
        # Token 消耗计数
        self.token_counter = Counter(
            "gateway_tokens_consumed_total",
            "Total tokens consumed",
            ["model", "type"] # type: prompt, completion, total
        )
        
        # 成本累计
        self.cost_gauge = Gauge(
            "gateway_cost_total",
            "Total cost in local currency",
            ["tenant_id"]
        )

    def start_exporter(self, port: int = 8000):
        if settings.ENABLE_METRICS:
            start_http_server(port)
            print(f"Metrics exporter started on port {port}")

metrics = MetricsExporter()
