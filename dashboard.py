import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json

# 页面配置
st.set_page_config(
    page_title="云南省企业就业失业数据采集系统",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 30px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
    }
    .status-approved {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .status-rejected {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
    .sidebar-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# API基础URL
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# 模拟数据
MOCK_ENTERPRISES = pd.DataFrame([
    {"id": 1001, "name": "昆明市某制造企业", "status": 0, "city": "昆明", "employees": 1200},
    {"id": 1002, "name": "大理州某服务企业", "status": 1, "city": "大理", "employees": 850},
    {"id": 1003, "name": "曲靖市某科技企业", "status": 0, "city": "曲靖", "employees": 560},
    {"id": 1004, "name": "玉溪市某农业企业", "status": 2, "city": "玉溪", "employees": 2100},
    {"id": 1005, "name": "保山市某建材企业", "status": 0, "city": "保山", "employees": 320},
])

STATUS_MAP = {
    0: "待备案",
    1: "已备案",
    2: "已退回"
}

STATUS_COLOR = {
    0: "status-pending",
    1: "status-approved", 
    2: "status-rejected"
}

# 侧边栏
with st.sidebar:
    st.markdown('<div class="sidebar-title">🔐 系统登录</div>', unsafe_allow_html=True)
    
    # 模拟登录
    username = st.text_input("用户名", value="admin")
    password = st.text_input("密码", value="password123", type="password")
    
    if st.button("登录系统"):
        st.success(f"✅ 欢迎回来，{username}！")
        st.session_state.logged_in = True
    
    st.divider()
    
    st.markdown('<div class="sidebar-title">📊 功能导航</div>', unsafe_allow_html=True)
    
    page = st.radio(
        "选择功能模块",
        ["📈 数据概览", "🏢 企业管理", "✅ 审批中心", "📋 统计分析"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.markdown('<div class="sidebar-title">ℹ️ 系统信息</div>', unsafe_allow_html=True)
    st.info(f"**当前版本**: v0.5 Alpha\n**登录用户**: {username}\n**访问时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 主页面头部
st.markdown('<div class="main-header">🏢 云南省企业就业失业数据采集系统</div>', unsafe_allow_html=True)

# 根据选择显示不同页面
if page == "📈 数据概览":
    st.subheader("📊 全省企业数据概览")
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("企业总数", "5", "+2")
    
    with col2:
        st.metric("待备案企业", "3", "-1")
    
    with col3:
        st.metric("已备案企业", "1", "+1")
    
    with col4:
        st.metric("总就业人数", "5,030", "+150")
    
    st.divider()
    
    # 企业列表
    st.subheader("📋 企业备案状态列表")
    
    for idx, row in MOCK_ENTERPRISES.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
            col1.write(f"**{row['id']}**")
            col2.write(f"**{row['name']}**")
            col3.write(f"📍 {row['city']}")
            col4.write(f"👥 {row['employees']}人")
            col5.markdown(f'<div class="{STATUS_COLOR[row["status"]]}">{STATUS_MAP[row["status"]]}</div>', unsafe_allow_html=True)
            st.divider()

elif page == "🏢 企业管理":
    st.subheader("🏢 企业信息管理")
    
    # 搜索和筛选
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 搜索企业", placeholder="输入企业名称...")
    with col2:
        status_filter = st.selectbox("状态筛选", ["全部", "待备案", "已备案", "已退回"])
    
    # 新增企业按钮
    if st.button("➕ 新增企业"):
        st.info("📝 企业信息录入功能开发中...")
    
    st.divider()
    
    # 企业数据表格
    display_df = MOCK_ENTERPRISES.copy()
    if search_term:
        display_df = display_df[display_df['name'].str.contains(search_term, case=False, na=False)]
    
    if status_filter != "全部":
        status_map_rev = {"待备案": 0, "已备案": 1, "已退回": 2}
        display_df = display_df[display_df['status'] == status_map_rev[status_filter]]
    
    display_df['status'] = display_df['status'].map(STATUS_MAP)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

elif page == "✅ 审批中心":
    st.subheader("✅ 企业备案审批中心")
    
    # 待审批企业列表
    pending_enterprises = MOCK_ENTERPRISES[MOCK_ENTERPRISES['status'] == 0]
    
    if len(pending_enterprises) > 0:
        for idx, row in pending_enterprises.iterrows():
            with st.expander(f"🏢 {row['name']} (ID: {row['id']})", expanded=True):
                col1, col2, col3 = st.columns(3)
                col1.info(f"📍 **地区**: {row['city']}")
                col2.info(f"👥 **员工数**: {row['employees']}")
                col3.info(f"📊 **当前状态**: {STATUS_MAP[row['status']]}")
                
                st.divider()
                
                # 审批操作
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ 批准备案", key=f"approve_{row['id']}"):
                        st.success(f"🎉 企业【{row['name']}】已成功备案！")
                        MOCK_ENTERPRISES.loc[idx, 'status'] = 1
                        st.rerun()
                
                with col2:
                    if st.button(f"❌ 退回申请", key=f"reject_{row['id']}"):
                        with st.expander("📝 填写退回原因"):
                            reason = st.text_area("退回原因", key=f"reason_{row['id']}")
                            if st.button("确认退回", key=f"confirm_reject_{row['id']}"):
                                if reason:
                                    st.warning(f"⚠️ 企业【{row['name']}】已被退回")
                                    MOCK_ENTERPRISES.loc[idx, 'status'] = 2
                                    st.rerun()
                                else:
                                    st.error("❌ 请填写退回原因！")
    else:
        st.info("📋 当前没有待审批的企业")

elif page == "📋 统计分析":
    st.subheader("📋 数据统计分析")
    
    # 按地区统计
    st.write("### 📍 按地区企业分布")
    city_stats = MOCK_ENTERPRISES.groupby('city').agg({
        'id': 'count',
        'employees': 'sum'
    }).rename(columns={'id': '企业数量', 'employees': '总员工数'})
    
    st.bar_chart(city_stats['企业数量'])
    
    st.divider()
    
    # 按状态统计
    st.write("### 📊 企业备案状态分布")
    status_stats = MOCK_ENTERPRISES['status'].value_counts().sort_index()
    status_stats.index = status_stats.index.map(STATUS_MAP)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("待备案", status_stats.get("待备案", 0))
    with col2:
        st.metric("已备案", status_stats.get("已备案", 0))
    with col3:
        st.metric("已退回", status_stats.get("已退回", 0))
    
    st.divider()
    
    # 员工规模统计
    st.write("### 👥 企业员工规模分布")
    employee_ranges = pd.cut(MOCK_ENTERPRISES['employees'], 
                            bins=[0, 500, 1000, 2000, float('inf')],
                            labels=['小型(<500)', '中型(500-1000)', '大型(1000-2000)', '超大型(>2000)'])
    employee_stats = employee_ranges.value_counts()
    
    st.bar_chart(employee_stats)

# 页脚
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🏢 云南省企业就业失业数据采集系统 | v0.5 Alpha</p>
    <p>💻 技术支持: FastAPI + Streamlit | 📅 数据更新: 2026年3月30日</p>
</div>
""", unsafe_allow_html=True)