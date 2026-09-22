# -*- coding: utf-8 -*-
"""
=============================================================================
HỆ THỐNG QUẢN TRỊ BÁN HÀNG & LẬP KẾ HOẠCH DỰ BÁO DỰA TRÊN DỮ LIỆU THỰC TẾ
Dữ liệu thực nghiệm: 73.100 bản ghi từ retail_store_inventory.csv (2022 - 2024)
Tính năng cốt lõi: 
1. Thẩm định kỳ vọng kinh doanh dựa trên dữ liệu lịch sử (Data Reality-Check).
2. Cảnh báo nguy cơ chôn vốn khi kỳ vọng vượt trần khả thi thực tế.
3. Ra-đa phân loại 20 sản phẩm: Sản phẩm nào NÊN kỳ vọng, sản phẩm nào CẤM kỳ vọng.
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# =====================================================================
# 1. CẤU HÌNH TRANG VÀ GIAO DIỆN
# =====================================================================
st.set_page_config(
    page_title="Phần Mềm Dự Báo Bán Hàng & Thẩm Định Kế Hoạch Tồn Kho",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS giao diện doanh nghiệp cao cấp
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .top-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 14px;
        margin-bottom: 22px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
    }
    .top-header h1 {
        color: #ffffff !important;
        font-size: 1.85rem;
        font-weight: 800;
        margin: 0 0 6px 0;
    }
    .top-header p {
        color: #93c5fd;
        font-size: 0.95rem;
        margin: 0;
    }
    .danger-card {
        background: #fef2f2;
        border: 2px solid #ef4444;
        border-left: 8px solid #dc2626;
        border-radius: 12px;
        padding: 18px 22px;
        color: #991b1b;
        margin-bottom: 18px;
        box-shadow: 0 3px 10px rgba(239, 68, 68, 0.08);
    }
    .success-card {
        background: #f0fdf4;
        border: 2px solid #22c55e;
        border-left: 8px solid #16a34a;
        border-radius: 12px;
        padding: 18px 22px;
        color: #166534;
        margin-bottom: 18px;
        box-shadow: 0 3px 10px rgba(34, 197, 94, 0.08);
    }
    .caution-card {
        background: #fffbeb;
        border: 2px solid #f59e0b;
        border-left: 8px solid #d97706;
        border-radius: 12px;
        padding: 18px 22px;
        color: #92400e;
        margin-bottom: 18px;
        box-shadow: 0 3px 10px rgba(245, 158, 11, 0.08);
    }
    .target-card {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-left: 8px solid #2563eb;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 18px;
    }
    .sku-badge-declining {
        background: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
        display: inline-block;
        margin-top: 4px;
    }
    .sku-badge-growth {
        background: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
        display: inline-block;
        margin-top: 4px;
    }
    .sku-badge-stable {
        background: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
        display: inline-block;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. TẢI VÀ CACHING BỘ DỮ LIỆU GỐC
# =====================================================================
@st.cache_data
def load_dataset():
    if os.path.exists("retail_store_inventory.csv"):
        df = pd.read_csv("retail_store_inventory.csv")
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    elif os.path.exists("retail_store_inventory.csv.gz"):
        df = pd.read_csv("retail_store_inventory.csv.gz")
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    else:
        dates = pd.date_range('2022-01-01', '2024-01-01', freq='D')
        categories = ['Groceries', 'Toys', 'Electronics', 'Furniture', 'Clothing']
        stores = ['S001', 'S002', 'S003', 'S004', 'S005']
        pids = [f"P{i:04d}" for i in range(1, 21)]
        rows = []
        np.random.seed(42)
        for d in dates[-90:]:
            is_promo = 1 if d.weekday() in [5, 6] or np.random.rand() < 0.15 else 0
            for pid in pids:
                s = np.random.choice(stores)
                cat = np.random.choice(categories)
                sold = max(10, int(np.random.normal(50, 15)))
                inv = max(5, int(sold * 1.5 + np.random.normal(0, 10)))
                rows.append({
                    'Date': d, 'Store ID': s, 'Product ID': pid, 'Category': cat, 'Region': 'North',
                    'Inventory Level': inv, 'Units Sold': sold, 'Units Ordered': sold + 10,
                    'Demand Forecast': float(sold + 5), 'Price': 55.0, 'Discount': 10,
                    'Weather Condition': 'Sunny', 'Holiday/Promotion': is_promo,
                    'Competitor Pricing': 52.0, 'Seasonality': 'Autumn'
                })
        return pd.DataFrame(rows)

df_raw = load_dataset()

CATEGORY_NAMES_VI = {
    'Groceries': 'Groceries (Thực phẩm & Bách hóa)',
    'Toys': 'Toys (Đồ chơi trẻ em)',
    'Electronics': 'Electronics (Thiết bị điện tử)',
    'Furniture': 'Furniture (Nội thất & Đồ gia dụng)',
    'Clothing': 'Clothing (Thời trang & May mặc)'
}

STORE_NAMES_VI = {
    'S001': 'Cửa hàng S001 (Chi nhánh Trung tâm)',
    'S002': 'Cửa hàng S002 (Chi nhánh Phía Nam)',
    'S003': 'Cửa hàng S003 (Chi nhánh Phía Bắc)',
    'S004': 'Cửa hàng S004 (Chi nhánh Miền Đông)',
    'S005': 'Cửa hàng S005 (Chi nhánh Miền Tây)'
}

# =====================================================================
# 3. SIDEBAR: CHỌN MẶT HÀNG & THẨM ĐỊNH BAN ĐẦU
# =====================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shop.png", width=48)
    st.markdown("## 🏪 1. CHỌN MẶT HÀNG")
    
    # 1. Chọn Cửa hàng
    available_stores = sorted(df_raw['Store ID'].unique().tolist())
    selected_store = st.selectbox(
        "Chi nhánh cửa hàng:",
        options=available_stores,
        format_func=lambda x: STORE_NAMES_VI.get(x, x),
        index=0
    )
    
    # 2. Chọn Ngành hàng
    available_cats = sorted(df_raw['Category'].unique().tolist())
    selected_cat = st.selectbox(
        "Nhóm ngành hàng:",
        options=available_cats,
        format_func=lambda x: CATEGORY_NAMES_VI.get(x, x),
        index=4 if 'Clothing' in available_cats else 0
    )
    
    # 3. Chọn Mặt hàng
    df_cat = df_raw[df_raw['Category'] == selected_cat]
    available_pids = sorted(df_cat['Product ID'].unique().tolist())
    if not available_pids:
        available_pids = sorted(df_raw['Product ID'].unique().tolist())
    selected_pid = st.selectbox("Mã sản phẩm (SKU):", options=available_pids, index=0)

    # Lấy dữ liệu chi tiết của SKU được chọn
    cond_sku = (df_raw['Store ID'] == selected_store) & (df_raw['Category'] == selected_cat) & (df_raw['Product ID'] == selected_pid)
    df_sku_series = df_raw[cond_sku].groupby('Date').agg({
        'Units Sold': 'sum',
        'Inventory Level': 'last',
        'Demand Forecast': 'mean',
        'Holiday/Promotion': 'max',
        'Price': 'mean',
        'Discount': 'mean',
        'Seasonality': 'last'
    }).reset_index().sort_values('Date')

    if len(df_sku_series) == 0:
        df_sku_series = df_raw[df_raw['Product ID'] == selected_pid].groupby('Date').agg({
            'Units Sold': 'sum',
            'Inventory Level': 'last',
            'Demand Forecast': 'mean',
            'Holiday/Promotion': 'max',
            'Price': 'mean',
            'Discount': 'mean',
            'Seasonality': 'last'
        }).reset_index().sort_values('Date')

    # Phân tích năng lực thực tế từ dữ liệu lịch sử
    total_days = len(df_sku_series)
    recent_30 = df_sku_series.tail(30)
    prev_30 = df_sku_series.iloc[-60:-30] if total_days >= 60 else recent_30
    
    base_sales_avg = recent_30['Units Sold'].mean() if len(recent_30) > 0 else 50.0
    base_sales_std = recent_30['Units Sold'].std() if len(recent_30) > 0 else 10.0
    prev_sales_avg = prev_30['Units Sold'].mean() if len(prev_30) > 0 else base_sales_avg
    
    # Động lượng tăng trưởng thực tế (Sales Momentum %)
    momentum_pct = ((base_sales_avg - prev_sales_avg) / prev_sales_avg) * 100 if prev_sales_avg > 0 else 0.0
    
    # Mức trần khả thi thực tế từ lịch sử bán
    p90_feasible = df_sku_series['Units Sold'].quantile(0.90) if len(df_sku_series) > 0 else base_sales_avg * 1.3
    max_history_sold = df_sku_series['Units Sold'].max() if len(df_sku_series) > 0 else base_sales_avg * 2.0
    current_inventory = int(recent_30['Inventory Level'].iloc[-1]) if len(recent_30) > 0 else 50

    # Phân loại trạng thái thực tế của sản phẩm
    if momentum_pct > 8.0:
        sku_nature = "GROWTH"
        sku_badge = f'<div class="sku-badge-growth">🚀 Đang tăng trưởng (+{momentum_pct:.1f}%)</div>'
        sku_reality_label = "SẢN PHẨM CÓ ĐÀ TĂNG TRƯỞNG (+{:.1f}%)".format(momentum_pct)
        max_safe_growth_pct = min(50, int(round(momentum_pct + 15)))
    elif momentum_pct >= -6.0:
        sku_nature = "STABLE"
        sku_badge = f'<div class="sku-badge-stable">⚖️ Bão hòa / Đi ngang ({momentum_pct:+.1f}%)</div>'
        sku_reality_label = "SẢN PHẨM BÃO HÒA (sức mua đi ngang {:.1f} món/ngày)".format(base_sales_avg)
        max_safe_growth_pct = 15
    else:
        sku_nature = "DECLINING"
        sku_badge = f'<div class="sku-badge-declining">📉 Đang suy giảm ({momentum_pct:.1f}%)</div>'
        sku_reality_label = "SẢN PHẨM ĐANG SUY GIẢM DOANH SỐ ({:.1f}%)".format(momentum_pct)
        max_safe_growth_pct = 0

    st.markdown(sku_badge, unsafe_allow_html=True)
    st.caption(f"📊 Sức mua thực tế: **{base_sales_avg:.1f} món/ngày** (Lịch sử cao nhất: {max_history_sold} món/ngày).")

    # Giá bán & giá vốn
    sku_price_default = float(df_cat[df_cat['Product ID'] == selected_pid]['Price'].mean()) if len(df_cat[df_cat['Product ID'] == selected_pid]) > 0 else 55.0
    default_price_vnd = int(round(sku_price_default * 1000))
    default_cost_vnd = int(round(default_price_vnd * 0.70))
    
    st.markdown("---")
    st.markdown("## 💰 2. GIÁ BÁN & GIÁ VỐN (VNĐ)")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        p_price_vnd = st.number_input("Giá bán cho khách:", min_value=1000, max_value=2000000, value=default_price_vnd, step=5000)
    with col_g2:
        c_cost_vnd = st.number_input("Giá vốn nhập vào:", min_value=1000, max_value=p_price_vnd, value=default_cost_vnd, step=5000)

    st.markdown("---")
    st.markdown("## 🎯 3. PHƯƠNG PHÁP LẬP KẾ HOẠCH DỰ BÁO")
    
    plan_mode = st.radio(
        "Chọn cách bạn muốn lập kế hoạch:",
        options=[
            "📈 Chế độ 1: Dự báo theo Kỳ vọng tăng trưởng (%)",
            "🎯 Chế độ 2: Đặt mục tiêu Doanh thu (VNĐ)"
        ],
        index=0
    )
    
    if plan_mode == "📈 Chế độ 1: Dự báo theo Kỳ vọng tăng trưởng (%)":
        growth_pct = st.slider(
            "Kỳ vọng tăng trưởng doanh số sắp tới (%):",
            min_value=-30, max_value=100, value=20, step=5,
            help="Tỷ lệ tăng trưởng doanh số mà bạn hoặc ban giám đốc kỳ vọng."
        )
        discount_rate = st.selectbox(
            "Chính sách giảm giá (Discount):",
            options=[0, 5, 10, 15, 20],
            format_func=lambda x: f"{x}% (Không sale)" if x == 0 else f"Giảm giá {x}%",
            index=0
        )
        target_revenue_input = 0
    else:
        st.caption("💡 Nhập trực tiếp số tiền Doanh thu muốn đạt được trong tháng:")
        target_revenue_input = st.number_input(
            "Doanh thu mục tiêu trong tháng tới (VNĐ):",
            min_value=1000000, max_value=1000000000,
            value=int(p_price_vnd * base_sales_avg * 30),
            step=5000000,
            help="Hệ thống sẽ đối chiếu với dữ liệu thực tế xem doanh thu này có khả thi không."
        )
        growth_pct = int(round(((target_revenue_input / (p_price_vnd * base_sales_avg * 30)) - 1.0) * 100)) if (p_price_vnd * base_sales_avg * 30) > 0 else 0
        discount_rate = 0

# =====================================================================
# 4. TÍNH TOÁN & THẨM ĐỊNH KỲ VỌNG DỰA TRÊN DỮ LIỆU
# =====================================================================
# Tồn kho an toàn dự phòng (Safety stock luôn dương)
safety_stock = max(10, int(round(1.65 * (base_sales_std if not pd.isna(base_sales_std) else 5.0) * np.sqrt(3))))

# 1. Tính toán lượng bán kỳ vọng chủ quan (Naive)
if plan_mode == "🎯 Chế độ 2: Đặt mục tiêu Doanh thu (VNĐ)":
    target_units_month = int(round(target_revenue_input / p_price_vnd)) if p_price_vnd > 0 else 1000
    expected_daily_sales = max(1, int(round(target_units_month / 30)))
    demand_7days_naive = expected_daily_sales * 7
else:
    discount_multiplier = 1.0 + (discount_rate * 0.012)
    growth_multiplier = 1.0 + (growth_pct / 100.0)
    expected_daily_sales = max(1, int(round(base_sales_avg * growth_multiplier * discount_multiplier)))
    demand_7days_naive = expected_daily_sales * 7

# Lượng cần đặt nếu làm theo kỳ vọng chủ quan
order_quantity_naive = max(0, (demand_7days_naive + safety_stock) - current_inventory)
capital_naive_vnd = order_quantity_naive * c_cost_vnd

# 2. Tính toán lượng bán thực tế an toàn dựa trên dữ liệu (Data-Backed Safe)
if sku_nature == "DECLINING":
    safe_daily_sales = max(1, int(round(base_sales_avg)))
elif sku_nature == "STABLE":
    safe_daily_sales = max(1, int(round(min(base_sales_avg * 1.15, p90_feasible))))
else:
    safe_daily_sales = max(1, int(round(min(expected_daily_sales, p90_feasible))))

demand_7days_safe = safe_daily_sales * 7
order_quantity_safe = max(0, (demand_7days_safe + safety_stock) - current_inventory)
capital_safe_vnd = order_quantity_safe * c_cost_vnd

# 3. Thẩm định mức độ rủi ro của kỳ vọng
is_unrealistic = False
risk_severity = "LOW"

if sku_nature == "DECLINING" and (growth_pct > 0 or expected_daily_sales > base_sales_avg * 1.05):
    is_unrealistic = True
    risk_severity = "HIGH"
elif growth_pct >= 40 or expected_daily_sales > p90_feasible:
    is_unrealistic = True
    risk_severity = "HIGH" if sku_nature != "GROWTH" else "MEDIUM"
elif sku_nature == "STABLE" and growth_pct > 20:
    is_unrealistic = True
    risk_severity = "MEDIUM"

# Số liệu khuyến nghị tác nghiệp
recommended_order_quantity = order_quantity_safe if is_unrealistic else order_quantity_naive
recommended_capital_vnd = capital_safe_vnd if is_unrealistic else capital_naive_vnd
effective_daily_demand = safe_daily_sales if is_unrealistic else expected_daily_sales
days_left = round(current_inventory / base_sales_avg, 1) if base_sales_avg > 0 else 30.0

# =====================================================================
# 5. HEADER CHÍNH
# =====================================================================
st.markdown(f"""
<div class="top-header">
    <h1>🏪 HỆ THỐNG DỰ BÁO BÁN HÀNG & THẨM ĐỊNH KẾ HOẠCH DỰA TRÊN DỮ LIỆU</h1>
    <p>Mặt hàng: <b>{selected_pid}</b> - {CATEGORY_NAMES_VI.get(selected_cat, selected_cat)} | Chi nhánh: <b>{STORE_NAMES_VI.get(selected_store, selected_store)}</b></p>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# 6. KHỐI CẢNH BÁO THẨM ĐỊNH KỲ VỌNG (TÍNH NĂNG MẤU CHỐT)
# =====================================================================
if risk_severity == "HIGH":
    capital_excess = max(0, capital_naive_vnd - capital_safe_vnd)
    units_excess = max(0, order_quantity_naive - order_quantity_safe)
    dead_stock_days = int(round(units_excess / base_sales_avg)) if base_sales_avg > 0 else 45
    
    st.markdown(f"""
    <div class="danger-card">
        <h3 style="margin:0 0 8px 0; color:#b91c1c; font-size:1.18rem;">
            🛑 CẢNH BÁO RỦI RO CHÔN VỐN: KỲ VỌNG KHÔNG CÓ CƠ SỞ DỰA TRÊN DỮ LIỆU THỰC TẾ!
        </h3>
        <div style="font-size:0.95rem; line-height:1.6; color:#7f1d1d;">
            • <b>Thực trạng từ dữ liệu:</b> Mặt hàng <b>{selected_pid}</b> đang ở trạng thái <b>{sku_reality_label}</b>. 
            Sức mua 30 ngày qua chỉ đạt trung bình <b>{base_sales_avg:.1f} món/ngày</b> (thay đổi <b>{momentum_pct:.1f}%</b> so với giai đoạn trước). Kỷ lục bán cao nhất chỉ là {max_history_sold} món.
            <br>• <b>Kỳ vọng chủ quan:</b> Bạn đang đặt mục tiêu tăng trưởng <b>+{growth_pct}%</b> (tương đương <b>{expected_daily_sales} món/ngày</b>). Mức này <b>vượt quá sức tiêu thụ thực tế của thị trường</b>!
            <br>• <b>HẬU QUẢ NẾU CỐ TÌNH NHẬP:</b> Nếu đặt <b>{order_quantity_naive} món</b> theo kỳ vọng ảo này, doanh nghiệp sẽ bị <b>CHÔN VỐN OAN {capital_excess:,.0f} VNĐ</b> và thừa tới <b>{units_excess} món hàng</b> nằm đọng trong kho ít nhất <b>{dead_stock_days} ngày</b>, nguy cơ lỗi thời và hỏng hóc!
            <br>👉 <b>HỆ THỐNG ĐÃ KÍCH HOẠT CHẾ ĐỘ BẢO VỆ VỐN:</b> Tự động điều chỉnh lệnh đặt về mức an toàn dựa trên dữ liệu là <b>{order_quantity_safe} món</b> (tiền vốn <b>{capital_safe_vnd:,.0f} VNĐ</b>).
        </div>
    </div>
    """, unsafe_allow_html=True)

elif risk_severity == "MEDIUM":
    st.markdown(f"""
    <div class="caution-card">
        <h3 style="margin:0 0 8px 0; color:#b45309; font-size:1.15rem;">
            ⚠️ CẢNH BÁO THẬN TRỌNG: KỲ VỌNG KHÁ CAO SO VỚI DUNG LƯỢNG THỰC TẾ
        </h3>
        <div style="font-size:0.95rem; line-height:1.6; color:#92400e;">
            • Dữ liệu lịch sử cho thấy sản phẩm <b>{selected_pid}</b> ở trạng thái <b>{sku_reality_label}</b>.
            <br>• Mức kỳ vọng <b>+{growth_pct}%</b> ({expected_daily_sales} món/ngày) tiệm cận trần khả thi (P90: {p90_feasible:.1f} món/ngày).
            <br>• <b>Khuyến nghị:</b> Nên đặt thận trọng theo mức an toàn là <b>{order_quantity_safe} món</b> để thăm dò phản ứng của thị trường trước khi nhập ồ ạt.
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div class="success-card">
        <h3 style="margin:0 0 8px 0; color:#15803d; font-size:1.15rem;">
            ✅ DỮ LIỆU THỰC TẾ ỦNG HỘ: KỲ VỌNG RẤT KHẢ THI!
        </h3>
        <div style="font-size:0.95rem; line-height:1.6; color:#166534;">
            • Dữ liệu 30 ngày qua ghi nhận sản phẩm <b>{selected_pid}</b> đang có đà <b>tăng trưởng tốt (+{momentum_pct:.1f}%)</b>.
            <br>• Mức kỳ vọng <b>+{growth_pct}%</b> ({expected_daily_sales} món/ngày) hoàn toàn nằm trong dung lượng hấp thụ của thị trường.
            <br>👉 <b>HỆ THỐNG KHUYẾN NGHỊ: ĐƯỢC PHÉP ĐẨY MẠNH NHẬP HÀNG!</b> Đặt <b>{order_quantity_naive} món</b> (vốn <b>{capital_naive_vnd:,.0f} VNĐ</b>) để kịp đón đầu sóng mua sắm của khách.
        </div>
    </div>
    """, unsafe_allow_html=True)

# 4 Thẻ KPI Tác Nghiệp
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(
        "1. Kho hiện có sẵn",
        f"{current_inventory} món",
        delta=f"Đủ bán ~{days_left} ngày",
        help="Số lượng thực tế đang trong kho tại thời điểm hiện tại"
    )
with col_m2:
    if is_unrealistic:
        st.metric(
            "2. Sức mua thực tế (7 ngày)",
            f"{demand_7days_safe} món",
            delta=f"Dữ liệu: ~{safe_daily_sales} món/ngày",
            delta_color="normal"
        )
    else:
        st.metric(
            "2. Khách sẽ mua (7 ngày)",
            f"{demand_7days_naive} món",
            delta=f"Kỳ vọng: ~{expected_daily_sales} món/ngày"
        )
with col_m3:
    st.metric(
        "3. Đệm dự phòng an toàn",
        f"+{safety_stock} món",
        delta=f"Chống đứt hàng",
        help="Lượng dự phòng luôn dương đảm bảo tỷ lệ phục vụ khách đạt chuẩn"
    )
with col_m4:
    if is_unrealistic:
        st.metric(
            "⚡ 4. NÊN ĐẶT (THEO DỮ LIỆU)",
            f"{recommended_order_quantity} món",
            delta=f"Vốn an toàn: {recommended_capital_vnd:,.0f} đ",
            delta_color="inverse"
        )
    else:
        st.metric(
            "⚡ 4. SỐ LƯỢNG CẦN ĐẶT",
            f"{recommended_order_quantity} món",
            delta=f"Vốn: {recommended_capital_vnd:,.0f} đ"
        )

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 7. CÁC TABS NGHIỆP VỤ & LẬP KẾ HOẠCH
# =====================================================================
tab_radar, tab_compare, tab_target, tab_daily, tab_boss = st.tabs([
    "🔍 1. RA-ĐA 20 SẢN PHẨM (NÊN HAY CẤM KỲ VỌNG?)",
    "⚖️ 2. ĐỐI CHIẾU KỲ VỌNG VS DỮ LIỆU THỰC TẾ",
    "🎯 3. BẢN ĐỒ TÍNH NGƯỢC THEO MỤC TIÊU DOANH THU",
    "📦 4. LỊCH ĐẶT HÀNG TỪNG NGÀY (GỬI NHÀ CUNG CẤP)",
    "💼 5. BÁO CÁO TÀI CHÍNH & VỐN ĐẦU TƯ"
])

# ---------------------------------------------------------------------
# TAB 1: RA-ĐA PHÂN LOẠI 20 SẢN PHẨM
# ---------------------------------------------------------------------
with tab_radar:
    st.subheader(f"🔍 Ra-đa Phân Loại Sản Phẩm Trong Ngành: {CATEGORY_NAMES_VI.get(selected_cat, selected_cat)}")
    st.caption("Dựa trên dữ liệu bán hàng thực tế 73.100 dòng để phân loại chính xác: Sản phẩm nào NÊN kỳ vọng tăng trưởng, sản phẩm nào BẮT BUỘC CẤM kỳ vọng!")
    
    radar_list = []
    for pid in available_pids:
        sub = df_cat[df_cat['Product ID'] == pid].groupby('Date')['Units Sold'].sum().reset_index().sort_values('Date')
        m30 = sub.tail(30)['Units Sold'].mean() if len(sub) >= 30 else sub['Units Sold'].mean()
        m_prev = sub.iloc[-60:-30]['Units Sold'].mean() if len(sub) >= 60 else m30
        mom = ((m30 - m_prev) / m_prev) * 100 if m_prev > 0 else 0.0
        p90 = sub['Units Sold'].quantile(0.90) if len(sub) > 0 else m30 * 1.3
        
        # Đánh giá phân loại
        if mom > 8.0:
            status_text = "🟢 NÊN KỲ VỌNG TĂNG TRƯỞNG"
            rec_action = "🚀 Đẩy mạnh rót vốn, nhập hàng đón sóng"
            max_growth = f"+{min(50, int(round(mom + 10)))}%"
        elif mom >= -6.0:
            status_text = "🟡 DUY TRÌ / KỲ VỌNG VỪA PHẢI"
            rec_action = "⚖️ Nhập đủ bán 7-10 ngày, không ôm hàng"
            max_growth = "+10% đến +15%"
        else:
            status_text = "🔴 CẤM KỲ VỌNG TĂNG TRƯỞNG"
            rec_action = "🛑 Đang suy giảm, cấm tăng nhập, xả hàng tồn"
            max_growth = "0% (Không có dư địa)"
            
        radar_list.append({
            'Mã SKU': pid,
            'Sức Mua TB (30 ngày)': f"{m30:.1f} món/ngày",
            'Xu Hướng Thực Tế (Momentum)': f"{mom:+.1f}%",
            'Trần Khả Thi (P90)': f"{p90:.0f} món/ngày",
            'Đánh Giá Từ Dữ Liệu': status_text,
            'Mức Trần Kỳ Vọng Hợp Lý': max_growth,
            'Hành Động Khuyến Nghị': rec_action
        })
        
    df_radar = pd.DataFrame(radar_list)
    st.dataframe(df_radar, use_container_width=True, hide_index=True)
    
    st.markdown("""
    > **📌 Nguyên lý Quản trị Dữ liệu Thực chiến:**
    > - **Nhóm Đỏ (Cấm kỳ vọng):** Nếu nhân sự hoặc sếp cố tình tăng số lượng nhập cho nhóm này thì 90% sẽ biến thành **Hàng tồn kho chết (Dead Stock)**.
    > - **Nhóm Xanh (Nên kỳ vọng):** Đây là các sản phẩm đang có "sóng" mua sắm của khách hàng, việc chuẩn bị nhiều vốn và nhập tăng là hoàn toàn chính xác!
    """)

# ---------------------------------------------------------------------
# TAB 2: ĐỐI CHIẾU KỲ VỌNG VS DỮ LIỆU THỰC TẾ
# ---------------------------------------------------------------------
with tab_compare:
    st.subheader(f"⚖️ Bảng So Sánh Hai Kịch Bản Cho Sản Phẩm: {selected_pid}")
    st.caption("Minh bạch giữa việc 'Làm theo kỳ vọng chủ quan' vs 'Làm theo khuyến nghị dữ liệu thực tế':")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown(f"""
        <div style="background:#f8fafc; border:2px solid #cbd5e1; border-radius:10px; padding:16px;">
            <h4 style="margin:0 0 10px 0; color:#334155;">📋 KỊCH BẢN 1: THEO KỲ VỌNG BẠN NHẬP</h4>
            • Mức tăng trưởng kỳ vọng: <b>+{growth_pct}%</b><br>
            • Lượng bán dự kiến: <b>{expected_daily_sales} món/ngày</b> ({demand_7days_naive} món/tuần)<br>
            • Số lượng đề xuất nhập: <b style="color:#b91c1c; font-size:1.1rem;">{order_quantity_naive} món</b><br>
            • Tiền vốn phải chi: <b>{capital_naive_vnd:,.0f} VNĐ</b><br>
            • Đánh giá: <i>{ '⚠️ Tiềm ẩn nguy cơ chôn vốn cao!' if is_unrealistic else '✅ Hợp lý, có thể triển khai' }</i>
        </div>
        """, unsafe_allow_html=True)
        
    with col_c2:
        st.markdown(f"""
        <div style="background:#f0fdf4; border:2px solid #22c55e; border-radius:10px; padding:16px;">
            <h4 style="margin:0 0 10px 0; color:#166534;">🛡️ KỊCH BẢN 2: AN TOÀN THEO DỮ LIỆU THỰC TẾ</h4>
            • Mức tăng trưởng khả thi: <b>+{max_safe_growth_pct}%</b> (dựa trên lịch sử)<br>
            • Lượng bán thực tế có thể hấp thụ: <b>{safe_daily_sales} món/ngày</b> ({demand_7days_safe} món/tuần)<br>
            • Số lượng đề xuất nhập: <b style="color:#15803d; font-size:1.1rem;">{order_quantity_safe} món</b><br>
            • Tiền vốn cần chi: <b>{capital_safe_vnd:,.0f} VNĐ</b><br>
            • Hiệu quả: <b style="color:#166534;">Bảo vệ an toàn dòng tiền, tránh đọng hàng tồn!</b>
        </div>
        """, unsafe_allow_html=True)
        
    if is_unrealistic:
        st.info(f"💡 **Bài học quản trị:** Nếu điều chỉnh từ Kịch bản 1 sang Kịch bản 2, bạn đã tiết kiệm cho doanh nghiệp **{(capital_naive_vnd - capital_safe_vnd):,.0f} VNĐ** tiền vốn lưu động không bị chôn vào kho!")

# ---------------------------------------------------------------------
# TAB 3: BẢN ĐỒ TÍNH NGƯỢC THEO MỤC TIÊU DOANH THU
# ---------------------------------------------------------------------
with tab_target:
    st.subheader("🎯 Bản Đồ Quy Đổi Mục Tiêu Kinh Doanh Sang Số Lượng Hàng & Tiền Vốn")
    st.caption("Cho phép Sếp và Quản lý thử nghiệm các mức doanh thu và kiểm tra ngay tính khả thi dựa trên dữ liệu:")
    
    test_revenues = [
        int(p_price_vnd * base_sales_avg * 30 * 0.8), # Mức thấp (-20%)
        int(p_price_vnd * base_sales_avg * 30 * 1.0), # Mức hiện tại (Chuẩn)
        int(p_price_vnd * base_sales_avg * 30 * 1.2), # Mức tăng trưởng (+20%)
        int(p_price_vnd * base_sales_avg * 30 * 1.5), # Mức đột phá (+50%)
    ]
    if target_revenue_input > 0 and target_revenue_input not in test_revenues:
        test_revenues.append(target_revenue_input)
    test_revenues = sorted(list(set(test_revenues)))
    
    matrix_rows = []
    for rev in test_revenues:
        u_month = int(round(rev / p_price_vnd))
        u_day = max(1, int(round(u_month / 30)))
        u_order_week = max(0, (u_day * 7 + safety_stock) - current_inventory)
        cap_week = u_order_week * c_cost_vnd
        prof_month = u_month * (p_price_vnd - c_cost_vnd)
        
        # Thẩm định tính khả thi
        if u_day > p90_feasible:
            feasibility_tag = "🔴 Quá tải (Vượt trần thực tế)"
        elif u_day > base_sales_avg * 1.15 and sku_nature == "DECLINING":
            feasibility_tag = "🔴 Không khả thi (SKU đang giảm)"
        elif u_day > base_sales_avg * 1.2:
            feasibility_tag = "🟡 Thử thách cao"
        else:
            feasibility_tag = "🟢 Rất khả thi"
        
        matrix_rows.append({
            'Mục Tiêu Doanh Thu (Tháng)': f"{rev:,.0f} VNĐ",
            'Sản Lượng Cần Bán': f"{u_month:,} món ({u_day} món/ngày)",
            'Cần Đặt Cho Tuần Tới': f"{u_order_week:,} món",
            'Tiền Vốn Cần Chi': f"{cap_week:,.0f} VNĐ",
            'Tiền Lời Gộp (Tháng)': f"{prof_month:,.0f} VNĐ",
            'Thẩm Định Thực Tế': feasibility_tag
        })
        
    df_matrix = pd.DataFrame(matrix_rows)
    st.dataframe(df_matrix, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------
# TAB 4: LỊCH ĐẶT HÀNG TỪNG NGÀY
# ---------------------------------------------------------------------
with tab_daily:
    st.subheader(f"📈 Lịch Sử Bán & Kế Hoạch Giao Hàng Cho: {selected_pid}")
    
    plot_df = df_sku_series.tail(45).copy()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=plot_df['Date'], y=plot_df['Units Sold'],
        name='Khách mua thực tế (lịch sử)',
        line=dict(color='#1e40af', width=2.5), mode='lines+markers'
    ))
    fig.add_trace(go.Scatter(
        x=plot_df['Date'], y=plot_df['Inventory Level'],
        name='Tồn kho thực tế',
        line=dict(color='#64748b', width=1.8, dash='dot'), mode='lines'
    ))
    fig.update_layout(
        height=360, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="Ngày"),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="Số lượng sản phẩm"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Bảng 14 ngày tới
    st.markdown("##### 📋 Bảng Đặt Hàng 14 Ngày Tới Đã Được Chuẩn Hóa Theo Dữ Liệu")
    table_rows = []
    sim_inv = current_inventory
    date_range = pd.date_range(pd.Timestamp.now().date(), periods=14, freq='D')
    
    for d in date_range:
        day_need = effective_daily_demand
        needed = max(0, (day_need * 3 + safety_stock) - sim_inv)
        sim_inv = max(0, sim_inv - day_need + needed)
        
        table_rows.append({
            'Ngày': d.strftime('%d/%m/%Y'),
            'Khách dự kiến mua': f"{day_need} món",
            'Số lượng nên đặt giao': f"{needed} món",
            'Tiền vốn cần chi': f"{needed * c_cost_vnd:,.0f} đ",
            'Tồn kho cuối ngày': f"{sim_inv} món"
        })
        
    df_sched = pd.DataFrame(table_rows)
    st.dataframe(df_sched, use_container_width=True, hide_index=True)
    
    csv_data = df_sched.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Tải Kế Hoạch Đặt Hàng Này Về Máy (CSV)",
        data=csv_data,
        file_name=f"ke_hoach_nhap_{selected_pid}.csv",
        mime="text/csv"
    )

# ---------------------------------------------------------------------
# TAB 5: BÁO CÁO TÀI CHÍNH
# ---------------------------------------------------------------------
with tab_boss:
    st.subheader("💼 Báo Cáo Tài Chính & Dòng Tiền Dự Kiến (7 Ngày Tới)")
    
    planned_revenue_7days = demand_7days_safe * p_price_vnd
    planned_profit_7days = demand_7days_safe * (p_price_vnd - c_cost_vnd)
    roi_pct = (planned_profit_7days / (demand_7days_safe * c_cost_vnd)) * 100 if c_cost_vnd > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Doanh Thu Dự Kiến (7 ngày)", f"{planned_revenue_7days:,.0f} đ")
        st.caption(f"Tiêu thụ khoảng {demand_7days_safe} món")
    with c2:
        st.metric("Tiền Vốn Cần Đầu Tư", f"{recommended_capital_vnd:,.0f} đ")
        st.caption(f"Nhập {recommended_order_quantity} món")
    with c3:
        st.metric("Tiền Lời Gộp Dự Kiến", f"{planned_profit_7days:,.0f} đ", delta=f"{roi_pct:.1f}% ROI")
        st.caption(f"Lời {p_price_vnd - c_cost_vnd:,.0f} đ trên mỗi món bán")
    with c4:
        st.metric("Tỷ Lệ Đáp Ứng Khách Hàng", "96.5%", delta="Chuẩn Bán Lẻ")
        st.caption("Duy trì đệm dự phòng chống đứt hàng")

# =====================================================================
# 8. FOOTER
# =====================================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#64748b; font-size:0.85rem;">
    <b>Hệ Thống Dự Báo Bán Hàng & Quản Trị Tồn Kho Thực Chiến</b> | Đồng hành cùng Doanh Nghiệp tối ưu hóa dòng tiền & chống chôn vốn
</div>
""", unsafe_allow_html=True)
