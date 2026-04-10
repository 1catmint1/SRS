"""
云南省企业就业失业数据采集系统 - 数据可视化大屏
"""
import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# 配置页面
st.set_page_config(
    page_title="云南省企业就业失业数据采集系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# API基础URL
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# 模拟数据（当API不可用时使用）
def get_mock_time_series_data():
    """获取模拟时间序列数据"""
    months = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
    return [
        {"period": m, "total_employees": 100000 + i*5000, "employed_count": 95000 + i*4800, 
         "unemployed_count": 5000 + i*200, "unemployment_rate": 5.0 - i*0.1,
         "new_employees": 2000 + i*100, "lost_employees": 1500 + i*50, "net_change": 500 + i*50}
        for i, m in enumerate(months)
    ]

def get_mock_dimension_data():
    """获取模拟维度数据"""
    return [
        {"dimension_name": "region", "dimension_value": "昆明市", "total_employees": 30000,
         "employed_count": 28500, "unemployed_count": 1500, "unemployment_rate": 5.0,
         "new_employees": 600, "lost_employees": 450, "net_change": 150},
        {"dimension_name": "region", "dimension_value": "大理州", "total_employees": 20000,
         "employed_count": 19000, "unemployed_count": 1000, "unemployment_rate": 5.0,
         "new_employees": 400, "lost_employees": 300, "net_change": 100},
        {"dimension_name": "region", "dimension_value": "曲靖市", "total_employees": 15000,
         "employed_count": 14250, "unemployed_count": 750, "unemployment_rate": 5.0,
         "new_employees": 300, "lost_employees": 225, "net_change": 75},
        {"dimension_name": "region", "dimension_value": "玉溪市", "total_employees": 12000,
         "employed_count": 11400, "unemployed_count": 600, "unemployment_rate": 5.0,
         "new_employees": 240, "lost_employees": 180, "net_change": 60},
        {"dimension_name": "region", "dimension_value": "保山市", "total_employees": 10000,
         "employed_count": 9500, "unemployed_count": 500, "unemployment_rate": 5.0,
         "new_employees": 200, "lost_employees": 150, "net_change": 50}
    ]

def get_mock_overall_stats():
    """获取模拟总体统计"""
    return {
        "total_enterprises": 1250,
        "total_employees": 87000,
        "employed_count": 82650,
        "unemployed_count": 4350,
        "unemployment_rate": 5.0,
        "new_employees": 1740,
        "lost_employees": 1305,
        "net_change": 435
    }

# 侧边栏配置
st.sidebar.title("📊 系统配置")

# 选择调查期
st.sidebar.subheader("调查期选择")
survey_period = st.sidebar.selectbox(
    "选择调查期",
    ["2026年第一季度", "2026年第二季度"],
    index=0
)

# 选择分析维度
st.sidebar.subheader("分析维度")
dimension_options = st.sidebar.multiselect(
    "选择分析维度",
    ["地区维度", "行业维度", "企业规模维度"],
    default=["地区维度"]
)

# 时间范围
st.sidebar.subheader("时间范围")
start_date = st.sidebar.date_input("开始日期", date(2026, 1, 1))
end_date = st.sidebar.date_input("结束日期", date(2026, 6, 30))

# 刷新按钮
if st.sidebar.button("🔄 刷新数据"):
    st.rerun()

# 主标题
st.markdown('<div class="main-header">云南省企业就业失业数据采集系统</div>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align: center; color: #666;">{survey_period} | 数据实时更新</p>', unsafe_allow_html=True)

# 获取数据
try:
    # 尝试从API获取数据
    # 这里使用模拟数据，实际应用中应该调用API
    time_series_data = get_mock_time_series_data()
    dimension_data = get_mock_dimension_data()
    overall_stats = get_mock_overall_stats()
except Exception as e:
    st.error(f"获取数据失败: {e}")
    time_series_data = []
    dimension_data = []
    overall_stats = {}

# 关键指标卡片
st.markdown("### 📈 关键指标")
col1, col2, col3, col4 = st.columns(4)

if overall_stats:
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{overall_stats['total_employees']:,}</div>
            <div class="metric-label">员工总数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-value">{overall_stats['employed_count']:,}</div>
            <div class="metric-label">就业人数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-value">{overall_stats['unemployment_rate']:.2f}%</div>
            <div class="metric-label">失业率</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="metric-value">{overall_stats['net_change']:+,}</div>
            <div class="metric-label">净变化</div>
        </div>
        """, unsafe_allow_html=True)

# 图表区域
st.markdown("---")
st.markdown("### 📊 趋势分析")

# 时间序列图
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 就业人数趋势")
    if time_series_data:
        df_time = pd.DataFrame(time_series_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_time['period'],
            y=df_time['employed_count'],
            mode='lines+markers',
            name='就业人数',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=df_time['period'],
            y=df_time['total_employees'],
            mode='lines+markers',
            name='员工总数',
            line=dict(color='#ff7f0e', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="就业人数与员工总数趋势",
            xaxis_title="月份",
            yaxis_title="人数",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### 失业率趋势")
    if time_series_data:
        df_time = pd.DataFrame(time_series_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_time['period'],
            y=df_time['unemployment_rate'],
            mode='lines+markers',
            name='失业率',
            line=dict(color='#d62728', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(214, 39, 40, 0.1)'
        ))
        
        fig.update_layout(
            title="失业率趋势变化",
            xaxis_title="月份",
            yaxis_title="失业率 (%)",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# 地区分析
st.markdown("---")
st.markdown("### 🗺️ 地区分析")

if "地区维度" in dimension_options and dimension_data:
    df_region = pd.DataFrame(dimension_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 各地区就业分布")
        fig = px.bar(
            df_region,
            x='dimension_value',
            y='total_employees',
            title="各地区员工总数分布",
            labels={'dimension_value': '地区', 'total_employees': '员工总数'},
            color='total_employees',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 各地区失业率对比")
        fig = px.bar(
            df_region,
            x='dimension_value',
            y='unemployment_rate',
            title="各地区失业率对比",
            labels={'dimension_value': '地区', 'unemployment_rate': '失业率 (%)'},
            color='unemployment_rate',
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

# 就业变化分析
st.markdown("---")
st.markdown("### 📈 就业变化分析")

if time_series_data:
    df_time = pd.DataFrame(time_series_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 新增与减少就业")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_time['period'],
            y=df_time['new_employees'],
            name='新增就业',
            marker_color='#2ca02c'
        ))
        fig.add_trace(go.Bar(
            x=df_time['period'],
            y=df_time['lost_employees'],
            name='减少就业',
            marker_color='#d62728'
        ))
        
        fig.update_layout(
            title="新增与减少就业对比",
            xaxis_title="月份",
            yaxis_title="人数",
            barmode='group',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 净变化趋势")
        fig = go.Figure()
        
        colors = ['#2ca02c' if x >= 0 else '#d62728' for x in df_time['net_change']]
        
        fig.add_trace(go.Bar(
            x=df_time['period'],
            y=df_time['net_change'],
            name='净变化',
            marker_color=colors
        ))
        
        fig.update_layout(
            title="就业净变化趋势",
            xaxis_title="月份",
            yaxis_title="净变化人数",
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# 数据表格
st.markdown("---")
st.markdown("### 📋 详细数据")

if dimension_data:
    df_region = pd.DataFrame(dimension_data)
    
    # 选择要显示的列
    display_columns = [
        'dimension_value', 'total_employees', 'employed_count',
        'unemployed_count', 'unemployment_rate', 'new_employees',
        'lost_employees', 'net_change'
    ]
    
    column_mapping = {
        'dimension_value': '地区',
        'total_employees': '员工总数',
        'employed_count': '就业人数',
        'unemployed_count': '失业人数',
        'unemployment_rate': '失业率(%)',
        'new_employees': '新增就业',
        'lost_employees': '减少就业',
        'net_change': '净变化'
    }
    
    df_display = df_region[display_columns].copy()
    df_display.columns = [column_mapping[col] for col in display_columns]
    
    # 格式化数值
    df_display['员工总数'] = df_display['员工总数'].apply(lambda x: f"{x:,}")
    df_display['就业人数'] = df_display['就业人数'].apply(lambda x: f"{x:,}")
    df_display['失业人数'] = df_display['失业人数'].apply(lambda x: f"{x:,}")
    df_display['失业率(%)'] = df_display['失业率(%)'].apply(lambda x: f"{x:.2f}%")
    df_display['新增就业'] = df_display['新增就业'].apply(lambda x: f"{x:+,}")
    df_display['减少就业'] = df_display['减少就业'].apply(lambda x: f"{x:+,}")
    df_display['净变化'] = df_display['净变化'].apply(lambda x: f"{x:+,}")
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>云南省企业就业失业数据采集系统 v0.5 Alpha</p>
    <p>数据更新时间: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)