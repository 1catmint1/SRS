"""
趋势对比图表算法服务
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import json


class ChartDataGenerator:
    """图表数据生成器"""
    
    @staticmethod
    def generate_line_chart_data(
        time_series: List[Dict[str, Any]],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """
        生成折线图数据
        
        Args:
            time_series: 时间序列数据
            metrics: 要显示的指标列表
        
        Returns:
            折线图数据结构
        """
        datasets = []
        labels = [item["period"] for item in time_series]
        
        colors = [
            "rgba(54, 162, 235, 1)",
            "rgba(255, 99, 132, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
            "rgba(255, 159, 64, 1)"
        ]
        
        background_colors = [
            "rgba(54, 162, 235, 0.2)",
            "rgba(255, 99, 132, 0.2)",
            "rgba(75, 192, 192, 0.2)",
            "rgba(153, 102, 255, 0.2)",
            "rgba(255, 159, 64, 0.2)"
        ]
        
        metric_names = {
            "total_employees": "员工总数",
            "employed_count": "就业人数",
            "unemployed_count": "失业人数",
            "unemployment_rate": "失业率(%)",
            "new_employees": "新增就业",
            "lost_employees": "减少就业",
            "net_change": "净变化"
        }
        
        for idx, metric in enumerate(metrics):
            data = [item.get(metric, 0) for item in time_series]
            
            dataset = {
                "label": metric_names.get(metric, metric),
                "data": data,
                "borderColor": colors[idx % len(colors)],
                "backgroundColor": background_colors[idx % len(background_colors)],
                "fill": False,
                "tension": 0.1
            }
            
            datasets.append(dataset)
        
        return {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "就业趋势分析"
                    },
                    "legend": {
                        "display": True,
                        "position": "top"
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
    
    @staticmethod
    def generate_bar_chart_data(
        dimension_data: List[Dict[str, Any]],
        x_field: str,
        y_field: str,
        title: str = "柱状图"
    ) -> Dict[str, Any]:
        """
        生成柱状图数据
        
        Args:
            dimension_data: 维度数据
            x_field: X轴字段
            y_field: Y轴字段
            title: 图表标题
        
        Returns:
            柱状图数据结构
        """
        labels = [item[x_field] for item in dimension_data]
        data = [item[y_field] for item in dimension_data]
        
        return {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": y_field,
                    "data": data,
                    "backgroundColor": [
                        "rgba(255, 99, 132, 0.6)",
                        "rgba(54, 162, 235, 0.6)",
                        "rgba(255, 206, 86, 0.6)",
                        "rgba(75, 192, 192, 0.6)",
                        "rgba(153, 102, 255, 0.6)",
                        "rgba(255, 159, 64, 0.6)"
                    ],
                    "borderColor": [
                        "rgba(255, 99, 132, 1)",
                        "rgba(54, 162, 235, 1)",
                        "rgba(255, 206, 86, 1)",
                        "rgba(75, 192, 192, 1)",
                        "rgba(153, 102, 255, 1)",
                        "rgba(255, 159, 64, 1)"
                    ],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": title
                    },
                    "legend": {
                        "display": False
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
    
    @staticmethod
    def generate_pie_chart_data(
        dimension_data: List[Dict[str, Any]],
        label_field: str,
        value_field: str,
        title: str = "饼图"
    ) -> Dict[str, Any]:
        """
        生成饼图数据
        
        Args:
            dimension_data: 维度数据
            label_field: 标签字段
            value_field: 数值字段
            title: 图表标题
        
        Returns:
            饼图数据结构
        """
        labels = [item[label_field] for item in dimension_data]
        data = [item[value_field] for item in dimension_data]
        
        return {
            "type": "pie",
            "data": {
                "labels": labels,
                "datasets": [{
                    "data": data,
                    "backgroundColor": [
                        "rgba(255, 99, 132, 0.7)",
                        "rgba(54, 162, 235, 0.7)",
                        "rgba(255, 206, 86, 0.7)",
                        "rgba(75, 192, 192, 0.7)",
                        "rgba(153, 102, 255, 0.7)",
                        "rgba(255, 159, 64, 0.7)"
                    ],
                    "borderColor": [
                        "rgba(255, 99, 132, 1)",
                        "rgba(54, 162, 235, 1)",
                        "rgba(255, 206, 86, 1)",
                        "rgba(75, 192, 192, 1)",
                        "rgba(153, 102, 255, 1)",
                        "rgba(255, 159, 64, 1)"
                    ],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": title
                    },
                    "legend": {
                        "display": True,
                        "position": "right"
                    }
                }
            }
        }
    
    @staticmethod
    def generate_multi_axis_chart_data(
        time_series: List[Dict[str, Any]],
        primary_metrics: List[str],
        secondary_metrics: List[str]
    ) -> Dict[str, Any]:
        """
        生成多轴图表数据
        
        Args:
            time_series: 时间序列数据
            primary_metrics: 主轴指标
            secondary_metrics: 次轴指标
        
        Returns:
            多轴图表数据结构
        """
        labels = [item["period"] for item in time_series]
        datasets = []
        
        metric_names = {
            "total_employees": "员工总数",
            "employed_count": "就业人数",
            "unemployed_count": "失业人数",
            "unemployment_rate": "失业率(%)",
            "new_employees": "新增就业",
            "lost_employees": "减少就业",
            "net_change": "净变化"
        }
        
        # 主轴数据
        primary_colors = ["rgba(54, 162, 235, 1)", "rgba(75, 192, 192, 1)"]
        for idx, metric in enumerate(primary_metrics):
            data = [item.get(metric, 0) for item in time_series]
            datasets.append({
                "label": metric_names.get(metric, metric),
                "data": data,
                "borderColor": primary_colors[idx % len(primary_colors)],
                "backgroundColor": primary_colors[idx % len(primary_colors)].replace("1", "0.2"),
                "fill": False,
                "yAxisID": "y"
            })
        
        # 次轴数据
        secondary_colors = ["rgba(255, 99, 132, 1)", "rgba(255, 159, 64, 1)"]
        for idx, metric in enumerate(secondary_metrics):
            data = [item.get(metric, 0) for item in time_series]
            datasets.append({
                "label": metric_names.get(metric, metric),
                "data": data,
                "borderColor": secondary_colors[idx % len(secondary_colors)],
                "backgroundColor": secondary_colors[idx % len(secondary_colors)].replace("1", "0.2"),
                "fill": False,
                "yAxisID": "y1"
            })
        
        return {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "多维度趋势分析"
                    },
                    "legend": {
                        "display": True,
                        "position": "top"
                    }
                },
                "scales": {
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "beginAtZero": True
                    },
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "grid": {
                            "drawOnChartArea": False
                        },
                        "beginAtZero": True
                    }
                }
            }
        }
    
    @staticmethod
    def generate_comparison_chart_data(
        comparison_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成对比图表数据
        
        Args:
            comparison_data: 对比数据
        
        Returns:
            对比图表数据结构
        """
        metrics = comparison_data.get("metrics", {})
        labels = list(metrics.keys())
        
        metric_names = {
            "total_employees": "员工总数",
            "employed_count": "就业人数",
            "unemployed_count": "失业人数",
            "unemployment_rate": "失业率(%)",
            "new_employees": "新增就业"
        }
        
        period1_data = [metrics[metric]["period1"] for metric in labels]
        period2_data = [metrics[metric]["period2"] for metric in labels]
        
        return {
            "type": "bar",
            "data": {
                "labels": [metric_names.get(label, label) for label in labels],
                "datasets": [
                    {
                        "label": comparison_data.get("period1", "周期1"),
                        "data": period1_data,
                        "backgroundColor": "rgba(54, 162, 235, 0.6)",
                        "borderColor": "rgba(54, 162, 235, 1)",
                        "borderWidth": 1
                    },
                    {
                        "label": comparison_data.get("period2", "周期2"),
                        "data": period2_data,
                        "backgroundColor": "rgba(255, 99, 132, 0.6)",
                        "borderColor": "rgba(255, 99, 132, 1)",
                        "borderWidth": 1
                    }
                ]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "周期对比分析"
                    },
                    "legend": {
                        "display": True,
                        "position": "top"
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
    
    @staticmethod
    def generate_heatmap_data(
        region_data: List[Dict[str, Any]],
        time_data: List[Dict[str, Any]],
        metric: str = "unemployment_rate"
    ) -> Dict[str, Any]:
        """
        生成热力图数据
        
        Args:
            region_data: 地区数据
            time_data: 时间数据
            metric: 指标名称
        
        Returns:
            热力图数据结构
        """
        regions = [item["region"] for item in region_data]
        periods = [item["period"] for item in time_data]
        
        # 生成模拟的热力图数据
        data = []
        for period_idx, period in enumerate(periods):
            for region_idx, region in enumerate(regions):
                # 模拟数据波动
                base_value = region_data[region_idx].get(metric, 5.0)
                variation = (period_idx - len(periods) / 2) * 0.5
                value = max(0, base_value + variation)
                
                data.append({
                    "x": period_idx,
                    "y": region_idx,
                    "v": value
                })
        
        return {
            "type": "heatmap",
            "data": {
                "labels": {
                    "x": periods,
                    "y": regions
                },
                "datasets": [{
                    "label": metric,
                    "data": data,
                    "backgroundColor": function="heatmapColor"
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "地区-时间热力图"
                    },
                    "legend": {
                        "display": True
                    }
                },
                "scales": {
                    "x": {
                        "type": "category",
                        "labels": periods
                    },
                    "y": {
                        "type": "category",
                        "labels": regions
                    }
                }
            }
        }


class TrendAnalyzer:
    """趋势分析器"""
    
    @staticmethod
    def calculate_moving_average(data: List[float], window: int = 3) -> List[float]:
        """计算移动平均值"""
        if len(data) < window:
            return data
        
        moving_avg = []
        for i in range(len(data) - window + 1):
            window_data = data[i:i + window]
            avg = sum(window_data) / window
            moving_avg.append(avg)
        
        return moving_avg
    
    @staticmethod
    def calculate_growth_rate(data: List[float]) -> List[float]:
        """计算增长率"""
        if len(data) < 2:
            return []
        
        growth_rates = []
        for i in range(1, len(data)):
            if data[i - 1] != 0:
                rate = ((data[i] - data[i - 1]) / data[i - 1]) * 100
                growth_rates.append(rate)
            else:
                growth_rates.append(0)
        
        return growth_rates
    
    @staticmethod
    def detect_trend(data: List[float], threshold: float = 0.05) -> str:
        """检测趋势方向"""
        if len(data) < 2:
            return "stable"
        
        growth_rates = TrendAnalyzer.calculate_growth_rate(data)
        avg_growth = sum(growth_rates) / len(growth_rates)
        
        if avg_growth > threshold:
            return "up"
        elif avg_growth < -threshold:
            return "down"
        else:
            return "stable"
    
    @staticmethod
    def calculate_seasonality(data: List[float], period: int = 12) -> Dict[str, Any]:
        """计算季节性"""
        if len(data) < period * 2:
            return {
                "has_seasonality": False,
                "seasonal_pattern": []
            }
        
        # 简单的季节性分析
        seasonal_pattern = []
        for i in range(period):
            period_values = [data[j] for j in range(i, len(data), period)]
            if period_values:
                avg = sum(period_values) / len(period_values)
                seasonal_pattern.append(avg)
        
        # 检测季节性
        pattern_variance = max(seasonal_pattern) - min(seasonal_pattern)
        overall_variance = max(data) - min(data)
        
        has_seasonality = pattern_variance > overall_variance * 0.3
        
        return {
            "has_seasonality": has_seasonality,
            "seasonal_pattern": seasonal_pattern,
            "pattern_variance": pattern_variance,
            "overall_variance": overall_variance
        }
    
    @staticmethod
    def forecast_next_value(data: List[float], periods: int = 1) -> List[float]:
        """预测下一个值（简单线性回归）"""
        if len(data) < 2:
            return [data[-1]] if data else [0]
        
        n = len(data)
        x = list(range(n))
        y = data
        
        # 计算线性回归
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # 预测
        forecasts = []
        for i in range(1, periods + 1):
            next_x = n + i - 1
            forecast = slope * next_x + intercept
            forecasts.append(max(0, forecast))  # 确保非负
        
        return forecasts


class ChartRenderer:
    """图表渲染器"""
    
    @staticmethod
    def render_chart_json(chart_data: Dict[str, Any]) -> str:
        """渲染图表为JSON格式"""
        return json.dumps(chart_data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def generate_chart_config(
        chart_type: str,
        title: str,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成图表配置"""
        config = {
            "type": chart_type,
            "data": data,
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": title,
                        "font": {
                            "size": 16,
                            "weight": "bold"
                        }
                    },
                    "legend": {
                        "display": True,
                        "position": "top",
                        "labels": {
                            "font": {
                                "size": 12
                            }
                        }
                    },
                    "tooltip": {
                        "enabled": True,
                        "mode": "index",
                        "intersect": False
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "grid": {
                            "display": True
                        }
                    },
                    "x": {
                        "grid": {
                            "display": False
                        }
                    }
                }
            }
        }
        
        if options:
            config["options"].update(options)
        
        return config