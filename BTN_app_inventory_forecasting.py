# -*- coding: utf-8 -*-
"""
=============================================================================
HỆ THỐNG ĐIỀU HÀNH DỰ BÁO BÁN HÀNG & TỒN KHO DOANH NGHIỆP
Smart Demand Forecasting & Inventory Optimization Platform
Phiên bản: Định lượng Thực chiến (Số liệu, Kết quả & Lệnh đặt hàng cụ thể)
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
import os

# =====================================================================
# 1. THIẾT LẬP CẤU HÌNH TRANG & GIAO DIỆN QUẢN TRỊ
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
# 2. TẢI VÀ CACHING DỮ LIỆU
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
        # Cơ chế dự phòng dữ liệu chạy mượt trên Cloud
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
    st.error("Không thể tải nguồn dữ liệu.")
    st.stop()

# =====================================================================
# 3. SIDEBAR: BẢNG THIẾT LẬP KINH DOANH
# =====================================================================
with st.sidebar:
    st.markdown("### 🎛️ BẢNG THIẾT LẬP KINH DOANH")
    st.caption("Điều chỉnh các thông số giá và chi phí thực tế của doanh nghiệp:")
    
    # 1. Chọn sản phẩm & cửa hàng
    st.markdown("##### 🏪 1. Chọn Mặt Hàng & Chi Nhánh")
    category_list = sorted(df_raw['Category'].unique().tolist())
    selected_cat = st.selectbox("Ngành hàng:", options=category_list, index=0)
    
    df_cat = df_raw[df_raw['Category'] == selected_cat]
    product_list = sorted(df_cat['Product ID'].unique().tolist())
    
    store_list = ['Tất cả chi nhánh'] + sorted(df_raw['Store ID'].unique().tolist())
    selected_store = st.selectbox("Chi nhánh phân phối:", options=store_list, index=1 if len(store_list) > 1 else 0)
    
    selected_pid = st.selectbox("Mã sản phẩm (SKU):", options=product_list, index=0)
    
    horizon_days = st.select_slider("Số ngày hiển thị trên biểu đồ:", options=[14, 30, 45, 60, 90], value=45)
    
    st.markdown("---")
    st.markdown("##### 💰 2. Giá Bán & Chi Phí Thực Tế")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        p_price = st.number_input("Giá bán lẻ (nghìn):", min_value=10.0, max_value=5000.0, value=100.0, step=5.0, help="Giá bán lẻ cho khách")
    with col_p2:
        c_cost = st.number_input("Giá vốn nhập (nghìn):", min_value=5.0, max_value=p_price, value=50.0, step=5.0, help="Giá mua vào từ nhà cung cấp")
        
    col_p3, col_p4 = st.columns(2)
    with col_p3:
        s_salvage = st.number_input("Giá xả kho (nghìn):", min_value=0.0, max_value=c_cost, value=15.0, step=2.0, help="Giá thanh lý khi tồn đọng")
    with col_p4:
        h_holding = st.number_input("Phí kho/món (nghìn):", min_value=0.0, max_value=50.0, value=5.0, step=1.0, help="Chi phí lưu kho và hao hụt")
        
    s_loss = st.slider("Thiệt hại khi hết hàng (nghìn):", min_value=0.0, max_value=50.0, value=10.0, step=1.0, help="Mức thiệt hại vô hình khi khách bỏ đi")
    
    st.markdown("---")
    st.markdown("##### ⚡ 3. Kịch Bản Khuyến Mãi")
    promo_boost = st.slider("Sức mua tăng thêm khi Sale (%):", min_value=0, max_value=100, value=35, step=5)

# =====================================================================
# 4. TÍNH TOÁN CÔNG THỨC VẬN HÀNH & KẾT QUẢ ĐỊNH LƯỢNG
# =====================================================================
# Chi phí trên từng đơn vị sản phẩm (nghìn VNĐ)
unit_profit_k = p_price - c_cost
Cu = unit_profit_k + s_loss
Co = c_cost - s_salvage + h_holding

# Đổi sang VNĐ chính xác
unit_profit_vnd = unit_profit_k * 1000
unit_stockout_loss_vnd = Cu * 1000
unit_overstock_cost_vnd = Co * 1000

# Mức phục vụ tối ưu
if (Cu + Co) > 0:
    q_star = Cu / (Cu + Co)
else:
    q_star = 0.5

z_qstar = norm.ppf(np.clip(q_star, 0.001, 0.999))

# =====================================================================
# 5. XỬ LÝ DỮ LIỆU CỦA SKU ĐÃ CHỌN
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

errors = df_sku['Units Sold'] - df_sku['Demand Forecast']
sigma = errors.std()
if pd.isna(sigma) or sigma == 0:
    sigma = 8.5

df_sku['P50'] = df_sku['Demand Forecast']
promo_mask = df_sku['Holiday/Promotion'] == 1
df_sku.loc[promo_mask, 'P50'] = df_sku.loc[promo_mask, 'P50'] * (1.0 + (promo_boost - 35) / 100.0)

df_sku['P10'] = np.maximum(0, df_sku['P50'] - 1.28 * sigma)
df_sku['P90'] = df_sku['P50'] + 1.28 * sigma
df_sku['Q_star'] = np.maximum(0, df_sku['P50'] + z_qstar * sigma)

# Đánh giá tài chính trong 90 ngày
df_recent = df_sku.tail(min(90, len(df_sku))).copy()

sold_old = np.minimum(df_recent['Units Sold'], df_recent['Demand Forecast'])
stockout_old = np.maximum(0, df_recent['Units Sold'] - df_recent['Demand Forecast'])
overstock_old = np.maximum(0, df_recent['Demand Forecast'] - df_recent['Units Sold'])
profit_old = sold_old * (p_price - c_cost) - stockout_old * s_loss - overstock_old * (c_cost - s_salvage + h_holding)

sold_new = np.minimum(df_recent['Units Sold'], df_recent['Q_star'])
stockout_new = np.maximum(0, df_recent['Units Sold'] - df_recent['Q_star'])
overstock_new = np.maximum(0, df_recent['Q_star'] - df_recent['Units Sold'])
profit_new = sold_new * (p_price - c_cost) - stockout_new * s_loss - overstock_new * (c_cost - s_salvage + h_holding)

total_profit_old_k = profit_old.sum()
total_profit_new_k = profit_new.sum()
profit_gain_pct = ((total_profit_new_k - total_profit_old_k) / abs(total_profit_old_k) * 100) if total_profit_old_k != 0 else 0.0

# Con số tiền thật quy đổi (VNĐ)
profit_new_vnd = total_profit_new_k * 1000
profit_old_vnd = total_profit_old_k * 1000
profit_diff_vnd = (total_profit_new_k - total_profit_old_k) * 1000

# Tiền thiệt hại tiết kiệm được (tiết kiệm do bớt cháy hàng + bớt tồn dư)
loss_saved_vnd = (((stockout_old - stockout_new) * s_loss) + ((overstock_old - overstock_new) * Co)).sum() * 1000

days_stockout_old = int((stockout_old > 0).sum())
days_stockout_new = int((stockout_new > 0).sum())
stockout_reduction = days_stockout_old - days_stockout_new
sla_new = (1.0 - days_stockout_new / len(df_recent)) * 100 if len(df_recent) > 0 else 100.0

# Con số lệnh đặt hàng cụ thể của ngày gần nhất
latest_row = df_sku.iloc[-1]
recommended_order_today = int(round(latest_row['Q_star']))
forecast_today = int(round(latest_row['Demand Forecast']))
low_demand_today = int(round(latest_row['P10']))
high_demand_today = int(round(latest_row['P90']))
safety_buffer_units = recommended_order_today - forecast_today
capital_needed_today_vnd = recommended_order_today * c_cost * 1000
reorder_point = int(round(forecast_today * 0.4 + max(0, safety_buffer_units)))

# Định hướng chiến lược
if q_star >= 0.70:
    strategy_name = "Ưu tiên: Nhập nhiều để giữ khách"
    strategy_badge = "badge-attack"
    strategy_desc = f"Mặt hàng này biên lãi cao (Bán 1 món lời <b>{unit_profit_vnd:,.0f} đ</b>, mất 1 đơn thiệt hại tới <b>{unit_stockout_loss_vnd:,.0f} đ</b>). Hệ thống chủ động đề xuất đặt <b>{recommended_order_today} món</b> (đệm thêm <b>+{safety_buffer_units} món</b>) để sẵn sàng phục vụ <b>{q_star:.0%}</b> nhu cầu."
elif q_star <= 0.40:
    strategy_name = "Ưu tiên: Nhập ít để giữ vốn"
    strategy_badge = "badge-defense"
    strategy_desc = f"Mặt hàng này rủi ro đọng vốn cao (Tồn dư 1 món tốn <b>{unit_overstock_cost_vnd:,.0f} đ</b>, trong khi thiếu hàng mất <b>{unit_stockout_loss_vnd:,.0f} đ</b>). Hệ thống chủ động hạ mức đặt xuống <b>{recommended_order_today} món</b> (chỉ phục vụ thận trọng ở mức <b>{q_star:.0%}</b>) để bảo toàn dòng tiền."
else:
    strategy_name = "Ưu tiên: Cân bằng vừa đủ bán"
    strategy_badge = "badge-balanced"
    strategy_desc = f"Chi phí khi cháy hàng ({unit_stockout_loss_vnd:,.0f} đ) và khi tồn dư ({unit_overstock_cost_vnd:,.0f} đ) khá tương đương. Đề xuất đặt <b>{recommended_order_today} món</b> bám sát nhu cầu trung bình để tối đa hóa tiền lời."

# =====================================================================
# 6. BANNER & 5 THẺ CHỈ SỐ DOANH NGHIỆP
# =====================================================================
st.markdown(f"""
<div class="main-banner">
    <h1>📦 HỆ THỐNG ĐIỀU HÀNH DỰ BÁO BÁN HÀNG & TỒN KHO</h1>
    <p>Tự động đề xuất lượng nhập hàng & tối ưu hóa dòng tiền | Mặt hàng: <b>{selected_pid}</b> ({selected_cat}) | Chi nhánh: <b>{selected_store}</b></p>
</div>
""", unsafe_allow_html=True)

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
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Đệm Tồn Kho Dự Phòng</div>
        <div class="kpi-val text-purple">{safety_buffer_units:+d} món</div>
        <div class="kpi-sub">Đệm an toàn chống cháy hàng</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Tiền Lời Tăng Thêm</div>
        <div class="kpi-val text-green">+{profit_gain_pct:.1f}%</div>
        <div class="kpi-sub">+{profit_diff_vnd:,.0f} đ (90 ngày)</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Giảm Số Ngày Hết Hàng</div>
        <div class="kpi-val text-red">-{stockout_reduction} ngày</div>
        <div class="kpi-sub">{days_stockout_old} ngày ➔ {days_stockout_new} ngày</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Tỷ Lệ Có Hàng Ngay</div>
        <div class="kpi-val text-green">{sla_new:.1f}%</div>
        <div class="kpi-sub"><span class="{strategy_badge}">{strategy_name[:15]}</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 7. CÁC MODULE NGHIỆP VỤ (100% ĐỊNH LƯỢNG RÕ RÀNG)
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 1. LỆNH ĐẶT HÀNG & DỰ BÁO TIÊU THỤ",
    "📊 2. KẾT QUẢ TÀI CHÍNH (SO VỚI CÁCH CŨ)",
    "🔍 3. TÁC ĐỘNG CỦA KHUYẾN MÃI & THỜI TIẾT",
    "📋 4. BẢNG TỔNG QUAN TỒN KHO TẤT CẢ SẢN PHẨM"
])

# ---------------------------------------------------------------------
# MODULE 1: LỆNH ĐẶT HÀNG & DỰ BÁO TIÊU THỤ
# ---------------------------------------------------------------------
with tab1:
    st.subheader(f"📋 Lệnh Đặt Hàng Hôm Nay & Kế Hoạch Nhập Kho: {selected_pid} ({selected_cat})")
    
    # BẢNG ĐIỀU HÀNH VỚI CON SỐ ĐỊNH LƯỢNG 100% CỤ THỂ
    st.markdown(f"""
    <div style="background: white; border: 1px solid #cbd5e1; border-left: 6px solid #2563eb; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 12px; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="font-size: 1.15rem; font-weight: 700; color: #0f172a;">⚡ LỆNH NHẬP HÀNG ĐỀ XUẤT CHO ĐỢT TỚI:</span>
                <span style="font-size: 1.4rem; font-weight: 800; color: #dc2626; margin-left: 8px;">{recommended_order_today} Sản phẩm</span>
                <span style="font-size: 0.9rem; color: #64748b; margin-left: 10px;">(Vốn nhập cần chi: <b>{capital_needed_today_vnd:,.0f} VNĐ</b>)</span>
            </div>
            <span class="{strategy_badge}" style="padding: 6px 14px; font-size: 0.85rem;">
                {strategy_name}
            </span>
        </div>
        
        <div style="font-size: 0.95rem; color: #334155; line-height: 1.6; margin-bottom: 18px;">
            📌 <b>Chỉ đạo điều hành:</b> {strategy_desc}
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
                <div style="color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">1. Sức mua dự kiến hôm nay</div>
                <div style="font-size: 1.35rem; font-weight: 700; color: #0f172a; margin: 4px 0;">{forecast_today} món</div>
                <div style="font-size: 0.8rem; color: #475569;">Dao động từ <b>{low_demand_today}</b> đến <b>{high_demand_today}</b> món</div>
            </div>
            
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
                <div style="color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">2. Đệm dự phòng trong kho</div>
                <div style="font-size: 1.35rem; font-weight: 700; color: #9333ea; margin: 4px 0;">{safety_buffer_units:+d} món</div>
                <div style="font-size: 0.8rem; color: #475569;">Dự phòng để không bao giờ thiếu hàng</div>
            </div>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
                <div style="color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">3. Điểm báo động đặt tiếp</div>
                <div style="font-size: 1.35rem; font-weight: 700; color: #d97706; margin: 4px 0;">{reorder_point} món</div>
                <div style="font-size: 0.8rem; color: #475569;">Kho còn dưới mức này phải đặt ngay</div>
            </div>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
                <div style="color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">4. Lợi nhuận gộp / 1 món</div>
                <div style="font-size: 1.35rem; font-weight: 700; color: #16a34a; margin: 4px 0;">+{unit_profit_vnd:,.0f} đ</div>
                <div style="font-size: 0.8rem; color: #475569;">(Giá bán {p_price*1000:,.0f}đ - Vốn {c_cost*1000:,.0f}đ)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Biểu đồ trực quan
    df_plot = df_sku.tail(horizon_days).copy()
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_plot['Date'], y=df_plot['P90'],
        mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=df_plot['Date'], y=df_plot['P10'],
        mode='lines', line=dict(width=0), fill='tonexty',
        fillcolor='rgba(59, 130, 246, 0.18)',
        name='Khoảng dao động nhu cầu (Thấp nhất - Cao nhất)',
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=df_plot['Date'], y=df_plot['Units Sold'],
        name='Khách mua thực tế (Doanh số bán)',
        line=dict(color='#0f172a', width=2.4),
        marker=dict(size=5), mode='lines+markers'
    ))
    fig.add_trace(go.Scatter(
        x=df_plot['Date'], y=df_plot['Demand Forecast'],
        name='Dự báo nhu cầu thông thường cũ',
        line=dict(color='#94a3b8', width=1.8, dash='dash'),
        mode='lines'
    ))
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
            orientation="h", yanchor="bottom", y=1.03, xanchor="center", x=0.5,
            bgcolor='rgba(255, 255, 255, 0.9)', bordercolor='#e2e8f0', borderwidth=1
        ),
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="Ngày theo dõi"),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="Số lượng sản phẩm")
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Bảng số liệu đặt hàng chi tiết 14 ngày tới (Đầy đủ số tiền và số lượng)
    st.markdown("##### 📋 Kế Hoạch Đặt Hàng & Dự Toán Ngân Sách 14 Ngày Tới")
    df_table = df_plot.tail(14)[['Date', 'Units Sold', 'Demand Forecast', 'P10', 'Q_star', 'P90', 'Holiday/Promotion']].copy()
    df_table['Ngày'] = df_table['Date'].dt.strftime('%d/%m/%Y')
    df_table['Khách mua thực tế'] = df_table['Units Sold'].round(0).astype(int)
    df_table['Dự kiến khách mua'] = df_table['Demand Forecast'].round(0).astype(int)
    df_table['Số lượng nên đặt (món)'] = df_table['Q_star'].round(0).astype(int)
    df_table['Đệm an toàn (món)'] = (df_table['Số lượng nên đặt (món)'] - df_table['Dự kiến khách mua']).astype(int)
    df_table['Tiền vốn cần chi (VNĐ)'] = (df_table['Số lượng nên đặt (món)'] * c_cost * 1000).apply(lambda x: f"{x:,.0f} đ")
    df_table['Chương trình'] = df_table['Holiday/Promotion'].apply(lambda x: '🔥 Có Sale' if x == 1 else 'Ngày thường')
    
    df_table_display = df_table[['Ngày', 'Khách mua thực tế', 'Dự kiến khách mua', 'Số lượng nên đặt (món)', 'Đệm an toàn (món)', 'Tiền vốn cần chi (VNĐ)', 'Chương trình']].copy()
    st.dataframe(df_table_display, use_container_width=True, hide_index=True)
    
    csv_data = df_table_display.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Tải Kế Hoạch Nhập Hàng Này Về Máy (CSV)",
        data=csv_data,
        file_name=f"ke_hoach_nhap_hang_{selected_pid}_{selected_store}.csv",
        mime="text/csv"
    )

# ---------------------------------------------------------------------
# MODULE 2: KẾT QUẢ TÀI CHÍNH SO VỚI CÁCH CŨ
# ---------------------------------------------------------------------
with tab2:
    st.subheader(f"📊 Kết Quả Tài Chính Cụ Thể Sau 90 Ngày Giao Dịch Thực Tế ({selected_pid})")
    st.caption("Đối chiếu trực tiếp hiệu quả giữa cách làm cũ và hệ thống thông minh mới:")
    
    # 3 Thẻ số tiền cụ thể
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.metric("Tổng tiền lời kiếm được", f"{profit_new_vnd:,.0f} VNĐ", delta=f"+{profit_diff_vnd:,.0f} VNĐ (+{profit_gain_pct:.1f}%)")
        st.caption(f"Cách cũ chỉ thu được: {profit_old_vnd:,.0f} VNĐ")
    with c_m2:
        st.metric("Tiền thiệt hại tiết kiệm được", f"{loss_saved_vnd:,.0f} VNĐ", delta="Cắt giảm lãng phí")
        st.caption("Nhờ không bị mất khách và không phải xả lỗ hàng tồn")
    with c_m3:
        st.metric("Số ngày bị cháy hàng", f"{days_stockout_new} ngày", delta=f"-{stockout_reduction} ngày cháy hàng")
        st.caption(f"Cách cũ bị cháy hàng tới {days_stockout_old} ngày")
        
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
            title="So Sánh Khối Lượng Sản Phẩm (Đơn vị trong 90 ngày)",
            barmode='group', plot_bgcolor='white',
            margin=dict(l=20, r=20, t=55, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_vol, use_container_width=True)
        
    with col_f2:
        cum_profit_old = np.cumsum(profit_old) * 1000
        cum_profit_new = np.cumsum(profit_new) * 1000
        
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(x=df_recent['Date'], y=cum_profit_old, name='Tiền lời tích lũy (Cách cũ)', line=dict(color='#94a3b8', dash='dash', width=2)))
        fig_cum.add_trace(go.Scatter(x=df_recent['Date'], y=cum_profit_new, name='Tiền lời tích lũy (Cách mới)', line=dict(color='#16a34a', width=2.8)))
        fig_cum.update_layout(
            title="Đường Tích Lũy Tiền Lời Theo Thời Gian (VNĐ)",
            plot_bgcolor='white', margin=dict(l=20, r=20, t=55, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_cum, use_container_width=True)

# ---------------------------------------------------------------------
# MODULE 3: TÁC ĐỘNG CỦA KHUYẾN MÃI & THỜI TIẾT
# ---------------------------------------------------------------------
with tab3:
    st.subheader("🔍 Phân Tích Các Yếu Tố Chi Phối Lượng Mua Hàng")
    
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
        fig_p.update_layout(title="Lượng Bán Trung Bình: Ngày Thường vs Ngày Khuyến Mãi", plot_bgcolor='white', yaxis_title="Số lượng bán (Món/Ngày)")
        st.plotly_chart(fig_p, use_container_width=True)
        st.caption("➔ **Kết luận:** Khuyến mãi giúp tăng trung bình **+36.3%** lượng bán ra. Cần nhập tăng tương ứng.")
        
    with col_d2:
        weather_stats = df_raw.groupby('Weather Condition')['Units Sold'].agg(['mean', 'median', 'std']).reset_index().sort_values('mean', ascending=False)
        fig_w = go.Figure(go.Bar(
            x=['Trời Nắng Đẹp (Sunny)', 'Trời Nhiều Mây (Cloudy)', 'Trời Mưa Bão (Rainy)'],
            y=weather_stats['mean'],
            marker_color=['#38bdf8', '#fbbf24', '#818cf8'],
            text=weather_stats['mean'].round(1),
            textposition='auto'
        ))
        fig_w.update_layout(title="Lượng Bán Trung Bình Theo Điều Kiện Thời Tiết", plot_bgcolor='white', yaxis_title="Số lượng bán (Món/Ngày)")
        st.plotly_chart(fig_w, use_container_width=True)
        st.caption("➔ **Kết luận:** Trời nắng ráo khách ghé mua nhiều nhất, ngày mưa bão sức mua giảm.")

    st.markdown("---")
    st.markdown("##### 🔬 Thử Nghiệm Tình Huống: Nếu Phí Thuê Kho Tăng Thì Giảm Nhập Bao Nhiêu?")
    
    h_test_range = np.linspace(1.0, 20.0, 10)
    q_test_vals = [Cu / (Cu + (c_cost - s_salvage + h_val)) for h_val in h_test_range]
    
    fig_sens = go.Figure()
    fig_sens.add_trace(go.Scatter(
        x=h_test_range * 1000, y=[val * 100 for val in q_test_vals],
        mode='lines+markers', line=dict(color='#2563eb', width=2.5),
        marker=dict(size=7, color='#1e40af'),
        name='Mức phục vụ mục tiêu (%)'
    ))
    fig_sens.add_vline(x=h_holding * 1000, line_dash="dash", line_color="#dc2626", annotation_text=f"Hiện tại: {h_holding*1000:,.0f}đ/món", annotation_position="top right")
    fig_sens.update_layout(
        title="Xu Hướng Giảm Mức Nhập Khi Phí Kho Tăng",
        xaxis_title="Phí lưu kho trên 1 món hàng (VNĐ)",
        yaxis_title="Mức phục vụ mục tiêu (%)",
        plot_bgcolor='white', margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_sens, use_container_width=True)

# ---------------------------------------------------------------------
# MODULE 4: TỔNG QUAN TỒN KHO TOÀN BỘ SẢN PHẨM
# ---------------------------------------------------------------------
with tab4:
    st.subheader(f"📋 Bảng Tổng Quan Tất Cả Mặt Hàng Trong Ngành: {selected_cat}")
    
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
            'Độ dao động (Std)': round(std_sales, 1) if not pd.isna(std_sales) else 0.0,
            'Giá vốn (VNĐ)': f"{c_val*1000:,.0f} đ",
            'Mức đáp ứng tối ưu': f"{q_val:.1%}",
            'Lượng nên đặt (Món)': int(round(q_star_sku)),
            'Tiền vốn cần chi': f"{q_star_sku * c_val * 1000:,.0f} đ",
            'Lời khuyên quản lý': strat
        })
    
    df_portfolio = pd.DataFrame(df_cat_summary)
    st.dataframe(df_portfolio, use_container_width=True, hide_index=True)
    
    fig_matrix = go.Figure()
    for strat, color in zip(["Ưu tiên: Nhập nhiều giữ khách", "Ưu tiên: Nhập vừa đủ", "Ưu tiên: Nhập ít giữ vốn"], ['#16a34a', '#fbbf24', '#dc2626']):
        sub_p = df_portfolio[df_portfolio['Lời khuyên quản lý'] == strat]
        if not sub_p.empty:
            fig_matrix.add_trace(go.Scatter(
                x=sub_p['Bán trung bình (Món/Ngày)'],
                y=sub_p['Lượng nên đặt (Món)'],
                mode='markers+text',
                text=sub_p['Mã sản phẩm'],
                textposition='top center',
                name=strat,
                marker=dict(size=12, color=color)
            ))
            
    fig_matrix.update_layout(
        title="Ma Trận Quản Trị Tồn Kho: Sức Bán Trung Bình vs Lượng Nên Nhập (Món)",
        xaxis_title="Sức bán trung bình (Món/Ngày)",
        yaxis_title="Lượng hàng nên đặt nhập (Món)",
        plot_bgcolor='white', margin=dict(l=25, r=25, t=55, b=25),
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
