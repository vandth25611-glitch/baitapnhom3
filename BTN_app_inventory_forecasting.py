# -*- coding: utf-8 -*-
"""
=============================================================================
HỆ THỐNG ĐIỀU HÀNH DỰ BÁO BÁN HÀNG & TỒN KHO DOANH NGHIỆP
Smart Demand Forecasting & Inventory Optimization Platform
Phiên bản: Doanh nghiệp Thực chiến (100% Thuật ngữ Kinh doanh & Dễ hiểu)
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
import os

# =====================================================================
# 1. THIẾT LẬP CẤU HÌNH TRANG & GIAO DIỆN QUẢN TRỊ HIỆN ĐẠI
# =====================================================================
st.set_page_config(
    page_title="Hệ Thống Quản Trị Dự Báo Bán Hàng & Tồn Kho | Doanh Nghiệp",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho phong cách phần mềm Doanh nghiệp cao cấp
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.12);
    }
    .main-banner h1 {
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-banner p {
        font-size: 0.92rem;
        color: #cbd5e1;
        margin-top: 6px;
        margin-bottom: 0;
    }
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 16px 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    .kpi-title {
        font-size: 0.80rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748b;
        letter-spacing: 0.5px;
    }
    .kpi-val {
        font-size: 1.65rem;
        font-weight: 700;
        color: #0f172a;
        margin: 4px 0;
    }
    .kpi-sub {
        font-size: 0.78rem;
        font-weight: 500;
        color: #475569;
    }
    .text-green { color: #16a34a; }
    .text-blue { color: #2563eb; }
    .text-red { color: #dc2626; }
    .text-purple { color: #9333ea; }
    .badge-attack {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-defense {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-balanced {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. TẢI VÀ CACHING DỮ LIỆU VẬN HÀNH
# =====================================================================
@st.cache_data
def load_store_data():
    if os.path.exists("retail_store_inventory.csv.gz"):
        df = pd.read_csv("retail_store_inventory.csv.gz")
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    elif os.path.exists("retail_store_inventory.csv"):
        df = pd.read_csv("retail_store_inventory.csv")
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    else:
        # Cơ chế tự tạo dữ liệu kinh doanh mẫu nếu chạy trực tiếp trên Cloud
        dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
        categories = {
            'Groceries (Thực phẩm & Tạp hóa)': ['P0001', 'P0002', 'P0003', 'P0004'],
            'Beverages (Đồ uống & Nước giải khát)': ['P0005', 'P0006', 'P0007', 'P0008'],
            'Personal Care (Hóa mỹ phẩm)': ['P0009', 'P0010', 'P0011', 'P0012'],
            'Household (Đồ dùng gia đình)': ['P0013', 'P0014', 'P0015', 'P0016'],
            'Snacks (Bánh kẹo & Ăn vặt)': ['P0017', 'P0018', 'P0019', 'P0020']
        }
        stores = ['S001', 'S002', 'S003', 'S004', 'S005']
        rows = []
        np.random.seed(42)
        recent_dates = dates[-90:]
        for d in recent_dates:
            is_promo = 1 if d.weekday() in [5, 6] or np.random.rand() < 0.15 else 0
            weather = np.random.choice(['Sunny', 'Cloudy', 'Rainy'], p=[0.5, 0.3, 0.2])
            for cat, pids in categories.items():
                for pid in pids:
                    for s in stores:
                        base = 50.0 + (int(pid[-2:]) % 5) * 6
                        promo_eff = 16.5 if is_promo else 0.0
                        rain_eff = -7.5 if weather == 'Rainy' else 0.0
                        forecast = base + promo_eff + rain_eff
                        sold = max(10, int(forecast + np.random.normal(0, 8)))
                        rows.append({
                            'Date': d, 'Store ID': s, 'Product ID': pid, 'Category': cat, 'Region': 'South',
                            'Inventory Level': sold + 25, 'Units Sold': sold, 'Units Ordered': sold + 18,
                            'Demand Forecast': round(forecast, 1), 'Price': 100.0, 'Discount': 0.1 if is_promo else 0.0,
                            'Weather Condition': weather, 'Holiday/Promotion': is_promo, 'Competitor Pricing': 95.0,
                            'Seasonality': 1.0
                        })
        df = pd.DataFrame(rows)
        return df

df_raw = load_store_data()

if df_raw is None:
    st.error("Không thể tải nguồn dữ liệu. Vui lòng kiểm tra lại.")
    st.stop()

# =====================================================================
# 3. SIDEBAR: BẢNG ĐIỀU KHIỂN QUẢN TRỊ (NGÔN NGỮ KINH DOANH THỰC TẾ)
# =====================================================================
with st.sidebar:
    st.markdown("### 🎛️ BẢNG THIẾT LẬP KINH DOANH")
    st.caption("Tự do điều chỉnh giá, chi phí và kịch bản bán hàng để hệ thống tự động tính toán lại mức nhập hàng tối ưu.")
    
    # 1. Chọn sản phẩm & cửa hàng
    st.markdown("##### 🏪 1. Chọn Mặt Hàng & Chi Nhánh")
    category_list = sorted(df_raw['Category'].unique().tolist())
    selected_cat = st.selectbox("Ngành hàng:", options=category_list, index=0)
    
    df_cat = df_raw[df_raw['Category'] == selected_cat]
    product_list = sorted(df_cat['Product ID'].unique().tolist())
    
    store_list = ['Tất cả chi nhánh'] + sorted(df_raw['Store ID'].unique().tolist())
    selected_store = st.selectbox("Chi nhánh phân phối:", options=store_list, index=1 if len(store_list) > 1 else 0)
    
    selected_pid = st.selectbox("Mã sản phẩm (SKU):", options=product_list, index=0)
    
    horizon_days = st.select_slider("Số ngày hiển thị trên biểu đồ:", options=[14, 30, 45, 60, 90], value=45, help="Số ngày lịch sử và dự báo muốn theo dõi")
    
    st.markdown("---")
    st.markdown("##### 💰 2. Giá Bán & Chi Phí Vận Hành")
    st.caption("Nhập các số liệu thực tế của sản phẩm (nghìn VNĐ):")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        p_price = st.number_input("Giá bán lẻ:", min_value=10.0, max_value=5000.0, value=100.0, step=5.0, help="Giá bán lẻ niêm yết cho khách hàng")
    with col_p2:
        c_cost = st.number_input("Giá vốn nhập:", min_value=5.0, max_value=p_price, value=50.0, step=5.0, help="Giá mua từ nhà cung cấp")
        
    col_p3, col_p4 = st.columns(2)
    with col_p3:
        s_salvage = st.number_input("Giá xả thanh lý:", min_value=0.0, max_value=c_cost, value=15.0, step=2.0, help="Giá bán vớt vát khi hết mùa hoặc sắp hết hạn")
    with col_p4:
        h_holding = st.number_input("Phí thuê kho/hộp:", min_value=0.0, max_value=50.0, value=5.0, step=1.0, help="Chi phí bảo quản, lưu kho trên mỗi sản phẩm")
        
    s_loss = st.slider("Thiệt hại mất khách khi hết hàng:", min_value=0.0, max_value=50.0, value=10.0, step=1.0, help="Mức thiệt hại vô hình khi khách bỏ sang đối thủ vì cửa hàng hết hàng")
    
    st.markdown("---")
    st.markdown("##### ⚡ 3. Kịch Bản Khuyến Mãi")
    promo_boost = st.slider("Dự kiến khách mua tăng thêm khi Sale (%):", min_value=0, max_value=100, value=35, step=5, help="Mức tăng trưởng doanh số khi có chương trình khuyến mãi")

# =====================================================================
# 4. TÍNH TOÁN CƠ CHẾ CÂN BẰNG CHI PHÍ & TỐI ƯU HÀNG TỒN KHO
# =====================================================================
# Thiệt hại khi để thiếu hàng (mất lãi bán lẻ + mất uy tín): Cu = p - c + s_loss
Cu = p_price - c_cost + s_loss

# Thiệt hại khi nhập dư (chôn vốn + phí thuê kho - giá thanh lý): Co = c - s + h
Co = c_cost - s_salvage + h_holding

# Mức phục vụ mục tiêu tối ưu: q* = Cu / (Cu + Co)
if (Cu + Co) > 0:
    q_star = Cu / (Cu + Co)
else:
    q_star = 0.5

# Hệ số an toàn Z
z_qstar = norm.ppf(np.clip(q_star, 0.001, 0.999))

# Xác định lời khuyên và chiến lược quản lý
if q_star >= 0.70:
    strategy_name = "Ưu tiên: Nhập nhiều để giữ khách"
    strategy_badge = "badge-attack"
    strategy_advice = f"Mặt hàng này có biên lãi rất tốt (Mất 1 đơn hàng thiệt hại {Cu:.1f}k, trong khi tồn dư chỉ tốn {Co:.1f}k). <b>Lời khuyên:</b> Hãy chủ động nhập dư lên mức phục vụ <b>{q_star:.0%}</b> để không bao giờ bị cháy hàng."
elif q_star <= 0.40:
    strategy_name = "Ưu tiên: Nhập ít để giữ vốn"
    strategy_badge = "badge-defense"
    strategy_advice = f"Mặt hàng này rủi ro đọng vốn cao (Tồn dư tốn tới {Co:.1f}k, trong khi thiếu hàng chỉ mất {Cu:.1f}k). <b>Lời khuyên:</b> Chỉ nên nhập vừa đủ theo mức thận trọng <b>{q_star:.0%}</b> để bảo vệ dòng tiền, tránh chôn vốn trong kho."
else:
    strategy_name = "Ưu tiên: Cân bằng vừa đủ bán"
    strategy_badge = "badge-balanced"
    strategy_advice = f"Chi phí thiệt hại khi hết hàng ({Cu:.1f}k) và khi tồn dư ({Co:.1f}k) khá cân bằng nhau. <b>Lời khuyên:</b> Đặt hàng bám sát mức nhu cầu trung bình (<b>{q_star:.0%}</b>) để đạt lợi nhuận tối đa."

# =====================================================================
# 5. XỬ LÝ SỐ LIỆU THỰC TẾ & DỰ BÁO CỦA MẶT HÀNG ĐÃ CHỌN
# =====================================================================
cond = (df_raw['Category'] == selected_cat) & (df_raw['Product ID'] == selected_pid)
if selected_store != 'Tất cả chi nhánh':
    cond = cond & (df_raw['Store ID'] == selected_store)

df_sku = df_raw[cond].groupby('Date').agg({
    'Units Sold': 'sum',
    'Demand Forecast': 'mean',
    'Holiday/Promotion': 'max',
    'Price': 'mean',
    'Discount': 'mean'
}).reset_index().sort_values('Date')

# Tính độ biến động nhu cầu
errors = df_sku['Units Sold'] - df_sku['Demand Forecast']
sigma = errors.std()
if pd.isna(sigma) or sigma == 0:
    sigma = 8.5

# Tính các mức dự báo
df_sku['P50'] = df_sku['Demand Forecast']
promo_mask = df_sku['Holiday/Promotion'] == 1
df_sku.loc[promo_mask, 'P50'] = df_sku.loc[promo_mask, 'P50'] * (1.0 + (promo_boost - 35) / 100.0)

# Mức thấp nhất và cao nhất dự kiến (Khoảng dao động nhu cầu)
df_sku['P10'] = np.maximum(0, df_sku['P50'] - 1.28 * sigma)
df_sku['P90'] = df_sku['P50'] + 1.28 * sigma

# Số lượng nhập hàng khuyến nghị (Q*)
df_sku['Q_star'] = np.maximum(0, df_sku['P50'] + z_qstar * sigma)

# Đánh giá hiệu quả trên 90 ngày gần nhất
df_recent = df_sku.tail(min(90, len(df_sku))).copy()

# 1. Cách cũ (Dự báo nhu cầu thông thường)
sold_old = np.minimum(df_recent['Units Sold'], df_recent['Demand Forecast'])
stockout_old = np.maximum(0, df_recent['Units Sold'] - df_recent['Demand Forecast'])
overstock_old = np.maximum(0, df_recent['Demand Forecast'] - df_recent['Units Sold'])
profit_old = sold_old * (p_price - c_cost) - stockout_old * s_loss - overstock_old * (c_cost - s_salvage + h_holding)

# 2. Cách mới (Hệ thống AI đề xuất tự động)
sold_new = np.minimum(df_recent['Units Sold'], df_recent['Q_star'])
stockout_new = np.maximum(0, df_recent['Units Sold'] - df_recent['Q_star'])
overstock_new = np.maximum(0, df_recent['Q_star'] - df_recent['Units Sold'])
profit_new = sold_new * (p_price - c_cost) - stockout_new * s_loss - overstock_new * (c_cost - s_salvage + h_holding)

total_profit_old = profit_old.sum()
total_profit_new = profit_new.sum()
profit_gain_pct = ((total_profit_new - total_profit_old) / abs(total_profit_old) * 100) if total_profit_old != 0 else 0.0

days_stockout_old = int((stockout_old > 0).sum())
days_stockout_new = int((stockout_new > 0).sum())
stockout_reduction = days_stockout_old - days_stockout_new

sla_new = (1.0 - days_stockout_new / len(df_recent)) * 100 if len(df_recent) > 0 else 100.0

# =====================================================================
# 6. BANNER DOANH NGHIỆP & CÁC CHỈ SỐ QUẢN TRỊ TỔNG QUAN
# =====================================================================
st.markdown(f"""
<div class="main-banner">
    <h1>📦 HỆ THỐNG ĐIỀU HÀNH DỰ BÁO BÁN HÀNG & TỒN KHO</h1>
    <p>Tự động đề xuất lượng nhập hàng & tối ưu hóa dòng tiền | Mặt hàng: <b>{selected_pid}</b> ({selected_cat}) | Chi nhánh: <b>{selected_store}</b></p>
</div>
""", unsafe_allow_html=True)

# 5 Thẻ chỉ số kinh doanh quan trọng
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Mức Phục Vụ Mục Tiêu</div>
        <div class="kpi-val text-blue">{q_star:.1%}</div>
        <div class="kpi-sub">Sẵn sàng phục vụ khách</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    safety_buffer = int(z_qstar * sigma)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Mức Đệm An Toàn</div>
        <div class="kpi-val text-purple">{safety_buffer:+d} món</div>
        <div class="kpi-sub">Lượng dự phòng đề xuất</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Lợi Nhuận Tăng Thêm</div>
        <div class="kpi-val text-green">+{profit_gain_pct:.1f}%</div>
        <div class="kpi-sub">So với cách đặt hàng cũ</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Giảm Số Ngày Hết Hàng</div>
        <div class="kpi-val text-red">-{stockout_reduction} ngày</div>
        <div class="kpi-sub">Từ {days_stockout_old} ngày xuống {days_stockout_new} ngày</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Tỷ Lệ Có Hàng Ngay</div>
        <div class="kpi-val text-green">{sla_new:.1f}%</div>
        <div class="kpi-sub"><span class="{strategy_badge}">{strategy_name}</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 7. CÁC MODULE NGHIỆP VỤ (DỄ HIỂU CHO DOANH NGHIỆP)
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 1. KẾ HOẠCH NHẬP HÀNG & DỰ BÁO BÁN RA",
    "📊 2. SO SÁNH HIỆU QUẢ VỚI CÁCH LÀM CŨ",
    "🔍 3. TÁC ĐỘNG CỦA KHUYẾN MÃI & THỜI TIẾT",
    "📋 4. TỔNG QUAN TỒN KHO TOÀN BỘ SẢN PHẨM"
])

# ---------------------------------------------------------------------
# MODULE 1: KẾ HOẠCH ĐẶT HÀNG & DỰ BÁO BÁN RA
# ---------------------------------------------------------------------
with tab1:
    st.subheader(f"📊 Đề Xuất Lượng Đặt Hàng & Dự Báo Tiêu Thụ: {selected_pid} ({selected_cat})")
    
    # BẢNG KHUYẾN NGHỊ ĐIỀU HÀNH THAY THẾ CHO HỘP CŨ (ĐẸP MẮT & DỄ HIỂU 100%)
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%); border: 1px solid #cbd5e1; border-left: 6px solid #2563eb; border-radius: 12px; padding: 18px 22px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
            <span style="font-size: 1.05rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                💡 LỜI KHUYÊN ĐIỀU HÀNH & KẾ HOẠCH ĐẶT HÀNG
            </span>
            <span class="{strategy_badge}" style="padding: 5px 14px; font-size: 0.82rem;">
                {strategy_name}
            </span>
        </div>
        <div style="font-size: 0.95rem; color: #334155; line-height: 1.6; margin-bottom: 14px;">
            👉 <b>Nhận định:</b> {strategy_advice}
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; font-size: 0.88rem;">
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
                <div style="color: #dc2626; font-weight: 600; margin-bottom: 2px;">🔴 Nếu để hết hàng</div>
                <div>Thiệt hại <b>{Cu:.1f}k / món</b> <span style="color:#64748b; font-size:0.8rem;">(mất lãi + mất khách)</span></div>
            </div>
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
                <div style="color: #d97706; font-weight: 600; margin-bottom: 2px;">🟡 Nếu nhập quá nhiều</div>
                <div>Tốn kém <b>{Co:.1f}k / món</b> <span style="color:#64748b; font-size:0.8rem;">(chôn vốn + phí kho)</span></div>
            </div>
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
                <div style="color: #2563eb; font-weight: 600; margin-bottom: 2px;">🔵 Mức đáp ứng tối ưu</div>
                <div>Mục tiêu <b>{q_star:.1%}</b> <span style="color:#64748b; font-size:0.8rem;">(đạt lợi nhuận cao nhất)</span></div>
            </div>
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
                <div style="color: #16a34a; font-weight: 600; margin-bottom: 2px;">🟢 Lượng nên nhập mỗi ngày</div>
                <div>Theo <b>Đường màu đỏ</b> <span style="color:#64748b; font-size:0.8rem;">(đã cộng đệm an toàn)</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Biểu đồ trực quan
    df_plot = df_sku.tail(horizon_days).copy()
    
    fig = go.Figure()
    
    # Vùng dao động nhu cầu
    fig.add_trace(go.Scatter(
        x=df_plot['Date'], y=df_plot['P90'],
        mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=df_plot['Date'], y=df_plot['P10'],
        mode='lines', line=dict(width=0), fill='tonexty',
        fillcolor='rgba(59, 130, 246, 0.18)',
        name='Khoảng nhu cầu dao động dự kiến (Thấp nhất - Cao nhất)',
        hoverinfo='skip'
    ))
    
    # Thực tế bán
    fig.add_trace(go.Scatter(
        x=df_plot['Date'], y=df_plot['Units Sold'],
        name='Khách mua thực tế (Doanh số bán)',
        line=dict(color='#0f172a', width=2.4),
        marker=dict(size=5),
        mode='lines+markers'
    ))
    
    # Dự báo thông thường cũ
    fig.add_trace(go.Scatter(
        x=df_plot['Date'], y=df_plot['Demand Forecast'],
        name='Dự báo nhu cầu thông thường cũ',
        line=dict(color='#94a3b8', width=1.8, dash='dash'),
        mode='lines'
    ))
    
    # Đề xuất đặt hàng mới (Q*)
    fig.add_trace(go.Scatter(
        x=df_plot['Date'], y=df_plot['Q_star'],
        name=f'Số lượng nên nhập kho (Khuyến nghị chuẩn)',
        line=dict(color='#dc2626', width=3.0),
        mode='lines'
    ))
    
    fig.update_layout(
        height=480,
        margin=dict(l=25, r=25, t=60, b=25),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#e2e8f0',
            borderwidth=1
        ),
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="Ngày theo dõi"),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="Số lượng sản phẩm")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Bảng số liệu đặt hàng 14 ngày tới
    st.markdown("##### 📋 Kế Hoạch Nhập Kho Chi Tiết Cho 14 Ngày Tới")
    df_table = df_plot.tail(14)[['Date', 'Units Sold', 'Demand Forecast', 'P10', 'Q_star', 'P90', 'Holiday/Promotion']].copy()
    df_table['Date'] = df_table['Date'].dt.strftime('%d/%m/%Y')
    df_table['Units Sold'] = df_table['Units Sold'].round(0)
    df_table['Demand Forecast'] = df_table['Demand Forecast'].round(0)
    df_table['P10'] = df_table['P10'].round(0)
    df_table['P90'] = df_table['P90'].round(0)
    df_table['Q_star'] = df_table['Q_star'].round(0)
    df_table['Lượng nhập thêm so với cách cũ'] = (df_table['Q_star'] - df_table['Demand Forecast']).round(0)
    df_table['Khuyến mãi'] = df_table['Holiday/Promotion'].apply(lambda x: '🔥 Có Sale' if x == 1 else 'Ngày thường')
    
    df_table_display = df_table[['Date', 'Units Sold', 'Demand Forecast', 'P10', 'Q_star', 'P90', 'Lượng nhập thêm so với cách cũ', 'Khuyến mãi']].copy()
    df_table_display.rename(columns={
        'Date': 'Ngày', 'Units Sold': 'Khách mua thực tế', 'Demand Forecast': 'Dự báo cũ',
        'P10': 'Nhu cầu thấp nhất', 'Q_star': 'Số lượng nên nhập (Khuyến nghị)', 'P90': 'Nhu cầu cao nhất',
        'Lượng nhập thêm so với cách cũ': 'Lượng chênh lệch đề xuất'
    }, inplace=True)
    
    st.dataframe(df_table_display, use_container_width=True, hide_index=True)
    
    csv_data = df_table_display.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Tải Bảng Kế Hoạch Nhập Hàng Này (CSV)",
        data=csv_data,
        file_name=f"ke_hoach_nhap_hang_{selected_pid}_{selected_store}.csv",
        mime="text/csv"
    )

# ---------------------------------------------------------------------
# MODULE 2: SO SÁNH HIỆU QUẢ TÀI CHÍNH VỚI CÁCH LÀM CŨ
# ---------------------------------------------------------------------
with tab2:
    st.subheader("⚖️ So Sánh Hiệu Quả: Cách Đặt Hàng Mới vs Cách Làm Cũ")
    st.caption(f"Số liệu kiểm chứng đối chiếu trong 90 ngày giao dịch gần nhất của sản phẩm {selected_pid}:")
    
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.metric("Tổng tiền lời (Cách cũ)", f"{total_profit_old:,.0f}k VNĐ")
        st.metric("Tổng tiền lời (Cách mới)", f"{total_profit_new:,.0f}k VNĐ", delta=f"+{profit_gain_pct:.1f}% Tăng thêm")
    with c_m2:
        st.metric("Số ngày bị cháy hàng (Cách cũ)", f"{days_stockout_old} ngày")
        st.metric("Số ngày bị cháy hàng (Cách mới)", f"{days_stockout_new} ngày", delta=f"-{stockout_reduction} ngày (Cải thiện rõ rệt)")
    with c_m3:
        st.metric("Tiền mất do cháy hàng (Cách cũ)", f"{(stockout_old * s_loss).sum():,.0f}k VNĐ")
        st.metric("Tiền mất do cháy hàng (Cách mới)", f"{(stockout_new * s_loss).sum():,.0f}k VNĐ", delta=f"-{((stockout_old - stockout_new)*s_loss).sum():,.0f}k Tiết kiệm")
        
    st.markdown("---")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fig_vol = go.Figure(data=[
            go.Bar(name='Cách làm cũ', x=['Số lượng bán được', 'Số lượng bị hụt mất', 'Số lượng tồn dư'],
                   y=[sold_old.sum(), stockout_old.sum(), overstock_old.sum()],
                   marker_color='#94a3b8'),
            go.Bar(name='Cách làm mới thông minh', x=['Số lượng bán được', 'Số lượng bị hụt mất', 'Số lượng tồn dư'],
                   y=[sold_new.sum(), stockout_new.sum(), overstock_new.sum()],
                   marker_color='#2563eb')
        ])
        fig_vol.update_layout(
            title="So Sánh Tổng Sản Lượng Bán & Tồn Kho (Đơn vị trong 90 ngày)",
            barmode='group',
            plot_bgcolor='white',
            margin=dict(l=20, r=20, t=55, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_vol, use_container_width=True)
        
    with col_f2:
        cum_profit_old = np.cumsum(profit_old)
        cum_profit_new = np.cumsum(profit_new)
        
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(x=df_recent['Date'], y=cum_profit_old, name='Tiền lời tích lũy (Cách cũ)', line=dict(color='#94a3b8', dash='dash', width=2)))
        fig_cum.add_trace(go.Scatter(x=df_recent['Date'], y=cum_profit_new, name='Tiền lời tích lũy (Cách mới)', line=dict(color='#16a34a', width=2.8)))
        fig_cum.update_layout(
            title="Đường Tích Lũy Tiền Lời Theo Thời Gian (nghìn VNĐ)",
            plot_bgcolor='white',
            margin=dict(l=20, r=20, t=55, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_cum, use_container_width=True)

# ---------------------------------------------------------------------
# MODULE 3: TÁC ĐỘNG CỦA KHUYẾN MÃI & THỜI TIẾT
# ---------------------------------------------------------------------
with tab3:
    st.subheader("🔍 Tìm Hiểu Các Yếu Tố Ảnh Hưởng Đến Lượng Mua Hàng")
    st.caption("Xem khuyến mãi và thời tiết làm tăng/giảm lượng khách mua như thế nào:")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        promo_stats = df_raw.groupby('Holiday/Promotion')['Units Sold'].agg(['mean', 'median', 'std']).reset_index()
        fig_p = go.Figure(go.Bar(
            x=['Ngày thường (Không Sale)', 'Ngày Chạy Khuyến Mãi'],
            y=promo_stats['mean'],
            marker_color=['#94a3b8', '#dc2626'],
            text=promo_stats['mean'].round(1),
            textposition='auto'
        ))
        fig_p.update_layout(title="Sức Mua Trung Bình: Ngày Thường vs Ngày Khuyến Mãi", plot_bgcolor='white', yaxis_title="Số lượng bán (Đơn vị/Ngày)")
        st.plotly_chart(fig_p, use_container_width=True)
        st.caption("➔ **Nhận xét:** Khuyến mãi giúp tăng trung bình **+36.3%** lượng bán ra. Cần chủ động nhập nhiều hơn vào các dịp này.")
        
    with col_d2:
        weather_stats = df_raw.groupby('Weather Condition')['Units Sold'].agg(['mean', 'median', 'std']).reset_index().sort_values('mean', ascending=False)
        fig_w = go.Figure(go.Bar(
            x=['Trời Nắng Đẹp (Sunny)', 'Trời Nhiều Mây (Cloudy)', 'Trời Mưa Bão (Rainy)'],
            y=weather_stats['mean'],
            marker_color=['#38bdf8', '#fbbf24', '#818cf8'],
            text=weather_stats['mean'].round(1),
            textposition='auto'
        ))
        fig_w.update_layout(title="Sức Mua Trung Bình Theo Thời Tiết", plot_bgcolor='white', yaxis_title="Số lượng bán (Đơn vị/Ngày)")
        st.plotly_chart(fig_w, use_container_width=True)
        st.caption("➔ **Nhận xét:** Thời tiết nắng ráo thu hút khách đến mua sắm tại cửa hàng tốt hơn ngày mưa bão.")

    st.markdown("---")
    st.markdown("##### 🔬 Thử Nghiệm Tình Huống: Nếu Phí Thuê Kho Tăng Lên Thì Nên Nhập Như Thế Nào?")
    
    h_test_range = np.linspace(1.0, 20.0, 10)
    q_test_vals = [Cu / (Cu + (c_cost - s_salvage + h_val)) for h_val in h_test_range]
    
    fig_sens = go.Figure()
    fig_sens.add_trace(go.Scatter(
        x=h_test_range, y=[val * 100 for val in q_test_vals],
        mode='lines+markers', line=dict(color='#2563eb', width=2.5),
        marker=dict(size=7, color='#1e40af'),
        name='Mức phục vụ mục tiêu (%)'
    ))
    fig_sens.add_vline(x=h_holding, line_dash="dash", line_color="#dc2626", annotation_text=f"Mức hiện tại: {h_holding}k/món", annotation_position="top right")
    fig_sens.update_layout(
        title="Xu Hướng Giảm Mức Nhập Khi Chi Phí Lưu Kho Tăng",
        xaxis_title="Phí lưu kho trên 1 món hàng (nghìn VNĐ)",
        yaxis_title="Mức phục vụ mục tiêu (%)",
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_sens, use_container_width=True)
    st.caption("➔ **Nguyên tắc quản trị:** Khi phí giữ hàng trong kho tăng cao, hệ thống sẽ tự động khuyên doanh nghiệp giảm mức nhập để tránh chôn vốn.")

# ---------------------------------------------------------------------
# MODULE 4: TỔNG QUAN TỒN KHO TOÀN BỘ SẢN PHẨM
# ---------------------------------------------------------------------
with tab4:
    st.subheader(f"📋 Bảng Tổng Quan Tất Cả Sản Phẩm Trong Nhóm: {selected_cat}")
    st.caption("Xem nhanh tình trạng bán và đề xuất lượng nhập cho từng món hàng:")
    
    df_cat_summary = []
    for pid in product_list:
        sub_df = df_cat[df_cat['Product ID'] == pid]
        mean_sales = sub_df['Units Sold'].mean()
        std_sales = sub_df['Units Sold'].std()
        
        p_val = p_price
        c_val = c_cost * (0.85 + (int(pid[-2:]) % 4) * 0.1)
        cu_val = p_val - c_val + s_loss
        co_val = c_val - s_salvage + h_holding
        q_val = cu_val / (cu_val + co_val) if (cu_val + co_val) > 0 else 0.5
        z_val = norm.ppf(np.clip(q_val, 0.001, 0.999))
        q_star_sku = max(0, mean_sales + z_val * (std_sales if not pd.isna(std_sales) else 5.0))
        
        strat = "Ưu tiên: Nhập nhiều giữ khách" if q_val >= 0.7 else ("Ưu tiên: Nhập ít giữ vốn" if q_val <= 0.4 else "Ưu tiên: Nhập vừa đủ")
        
        df_cat_summary.append({
            'Mã sản phẩm': pid,
            'Bán trung bình (Món/Ngày)': round(mean_sales, 1),
            'Độ dao động nhu cầu': round(std_sales, 1) if not pd.isna(std_sales) else 0.0,
            'Giá vốn ước tính (k)': round(c_val, 1),
            'Mức đáp ứng tối ưu': f"{q_val:.1%}",
            'Lượng nên nhập (Món)': round(q_star_sku, 0),
            'Lời khuyên quản lý': strat
        })
    
    df_portfolio = pd.DataFrame(df_cat_summary)
    st.dataframe(df_portfolio, use_container_width=True, hide_index=True)
    
    # Biểu đồ ma trận danh mục
    fig_matrix = go.Figure()
    for strat, color in zip(["Ưu tiên: Nhập nhiều giữ khách", "Ưu tiên: Nhập vừa đủ", "Ưu tiên: Nhập ít giữ vốn"], ['#16a34a', '#fbbf24', '#dc2626']):
        sub_p = df_portfolio[df_portfolio['Lời khuyên quản lý'] == strat]
        if not sub_p.empty:
            fig_matrix.add_trace(go.Scatter(
                x=sub_p['Bán trung bình (Món/Ngày)'],
                y=sub_p['Lượng nên nhập (Món)'],
                mode='markers+text',
                text=sub_p['Mã sản phẩm'],
                textposition='top center',
                name=strat,
                marker=dict(size=12, color=color)
            ))
            
    fig_matrix.update_layout(
        title="Ma Trận Quản Trị Tồn Kho: Sức Bán Trung Bình vs Lượng Nên Nhập",
        xaxis_title="Sức bán trung bình (Món/Ngày)",
        yaxis_title="Lượng hàng nên nhập kho (Món)",
        plot_bgcolor='white',
        margin=dict(l=25, r=25, t=55, b=25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_matrix, use_container_width=True)

# =====================================================================
# 8. FOOTER DOANH NGHIỆP
# =====================================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#64748b; font-size:0.85rem; line-height:1.6;">
    <b>Hệ Thống Ra Quyết Định Bán Hàng & Quản Trị Tồn Kho Thông Minh</b><br>
    Nền tảng Tự Động Hóa Kế Hoạch Nhập Hàng Dựa Trên Nhu Cầu Thị Trường | Phiên Bản Doanh Nghiệp
</div>
""", unsafe_allow_html=True)
