import os
import requests
import pandas as pd
import numpy as np

# Hệ thống lấy cấu hình bảo mật từ GitHub Secrets của bạn
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def gui_telegram(tin_nhan):
    """Hàm gửi tin nhắn định dạng chuyên nghiệp về Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": tin_nhan, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def tinh_xu_huong_va_vol(df):
    """Tính các đường trung bình MA và trạng thái Volume"""
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
    
    last = df.iloc[-1]
    gia = float(last['Close'])
    ma20 = float(last['MA20'])
    ma50 = float(last['MA50'])
    vol = float(last['Volume'])
    vol_ma20 = float(last['Vol_MA20'])
    
    if gia > ma20 > ma50:
        xh = "🟢 TĂNG MẠNH (Uptrend)"
    elif gia > ma20:
        xh = "🟡 TÍCH LŨY TĂNG (Trên MA20)"
    elif gia < ma20 and gia > ma50:
        xh = "🟠 ĐIỀU CHỈNH (Dưới MA20, trên MA50)"
    else:
        xh = "🔴 GIẢM GIÁ (Downtrend)"
        
    if vol > vol_ma20 * 1.15:
        v_status = "🔥 Lớn (Dòng tiền mạnh)"
    elif vol < vol_ma20 * 0.85:
        v_status = "📉 Kiệt (Lực bán yếu dần)"
    else:
        v_status = "📈 Ổn định (Mức trung bình)"
        
    return gia, xh, v_status, ma20, ma50

def phan_tich_tong_hop_vni():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    records = []
    nguon_thanh_cong = ""

    # ==================== NGUỒN 1: TCBS ====================
    try:
        url_tcbs = "https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/bars-ticker?ticker=VNINDEX&type=stock&resolution=D&from=1672531200&to=1893456000"
        response = requests.get(url_tcbs, headers=headers, timeout=10).json()
        if 'data' in response and response['data']:
            for item in response['data']:
                records.append({
                    'Date': item.get('tradingDate'),
                    'Open': float(item.get('open')),
                    'High': float(item.get('high')),
                    'Low': float(item.get('low')),
                    'Close': float(item.get('close')),
                    'Volume': float(item.get('volume'))
                })
            nguon_thanh_cong = "TCBS (Nguồn Chính)"
    except Exception as e:
        print(f"Nguồn TCBS lỗi: {e}. Hệ thống tự động chuyển sang nguồn dự phòng...")

    # ==================== NGUỒN 2: STOCKBIZ (DỰ PHÒNG 1) ====================
    if not records:
        try:
            url_sb = "https://api.stockbiz.vn/api/financial/index/history?ticker=VNINDEX&count=250"
            response = requests.get(url_sb, headers=headers, timeout=10).json()
            if 'data' in response and response['data']:
                for item in response['data']:
                    records.append({
                        'Date': item.get('date'),
                        'Open': float(item.get('openPrice')),
                        'High': float(item.get('highestPrice')),
                        'Low': float(item.get('lowestPrice')),
                        'Close': float(item.get('closePrice')),
                        'Volume': float(item.get('totalVolume'))
                    })
                nguon_thanh_cong = "StockBiz (Dự phòng 1)"
        except Exception as e:
            print(f"Nguồn StockBiz lỗi: {e}. Tiếp tục chuyển sang nguồn dự phòng cuối...")

    # ==================== NGUỒN 3: SHARESINSIGHT (DỰ PHÒNG 2) ====================
    if not records:
        try:
            url_si = "https://fapi.sharesinsight.com/api/v1/market/index/history?symbol=VNINDEX&size=250"
            response = requests.get(url_si, headers=headers, timeout=10).json()
            if 'data' in response and response['data'] and 'list' in response['data']:
                for item in response['data']['list']:
                    records.append({
                        'Date': item.get('tradingDate'),
                        'Open': float(item.get('open')),
                        'High': float(item.get('high')),
                        'Low': float(item.get('low')),
                        'Close': float(item.get('close')),
                        'Volume': float(item.get('volume'))
                    })
                nguon_thanh_cong = "SharesInsight (Dự phòng 2)"
        except Exception as e:
            print(f"Nguồn SharesInsight lỗi: {e}")

    # ==================== XỬ LÝ & PHÂN TÍCH DỮ LIỆU ====================
    if not records:
        gui_telegram("❌ Thất bại: Tất cả các nguồn dữ liệu (TCBS, StockBiz, SharesInsight) đều không thể kết nối hoặc đang bảo trì rộng rộng!")
        return

    try:
        df_daily = pd.DataFrame(records)
        df_daily['Date'] = pd.to_datetime(df_daily['Date'])
        df_daily = df_daily.sort_values('Date').reset_index(drop=True)
        df_daily.set_index('Date', inplace=True)
        
        # Tạo dữ liệu khung Tuần và Tháng
        df_weekly = df_daily.resample('W').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', '
