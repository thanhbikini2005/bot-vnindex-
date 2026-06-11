import os
import requests
import pandas as pd

# Hệ thống lấy chìa khóa bí mật bạn đã cài
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
    
    # Xác định xu hướng ngắn và trung hạn
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

def phan_tich_cuoi_ngay_vni():
    try:
        # Sử dụng đường link tải dữ liệu dự phòng trực tiếp từ Yahoo Finance tránh bị lỗi chặn
        url_download = "https://query1.finance.yahoo.com/v7/finance/download/^VNINDEX?period1=1700000000&period2=2500000000&interval=1d&events=history"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url_download, headers=headers)
        
        with open("vni.csv", "wb") as f:
            f.write(res.content)
            
        df_daily = pd.read_csv("vni.csv")
        if df_daily.empty or len(df_daily) < 100:
            gui_telegram("❌ Lỗi dữ liệu: Không thể đọc được file CSV từ nguồn!")
            return
            
        # Chuẩn hóa bảng dữ liệu
        df_daily['Date'] = pd.to_datetime(df_daily['Date'])
        df_daily.set_index('Date', inplace=True)
        
        # Tạo dữ liệu khung Tuần và khung Tháng từ dữ liệu gốc
        df_weekly = df_daily.resample('W').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
        df_monthly = df_daily.resample('ME').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})

        # Tính toán phân tích
        gia_d, xh_d, vol_d, ma20_d, ma50_d = tinh_xu_huong_va_vol(df_daily)
        _, xh_w, vol_w, _, _ = tinh_xu_huong_va_vol(df_weekly)
        _, xh_m, vol_m, _, _ = tinh_xu_huong_va_vol(df_monthly)

        # Tính tỷ lệ biến động phần trăm %
        pct_d = ((gia_d - float(df_daily.iloc[-2]['Close'])) / float(df_daily.iloc[-2]['Close'])) * 100
        pct_w = ((gia_d - float(df_weekly.iloc[-2]['Close'])) / float(df_weekly.iloc[-2]['Close'])) * 100
        pct_m = ((gia_d - float(df_monthly.iloc[-2]['Close'])) / float(df_monthly.iloc[-2]['Close'])) * 100

        # TÍNH TOÁN FIBONACCI (Quét đỉnh/đáy trong 3 tháng qua ~ 60 phiên)
        df_3m = df_daily.tail(60)
        dinh_3m = float(df_3m['High'].max())
        day_3m = float(df_3m['Low'].min())
        khoang_cach = dinh_3m - day_3m

        fibo_236 = dinh_3m - 0.236 * khoang_cach
        fibo_382 = dinh_3m - 0.382 * khoang_cach
        fibo_500 = dinh_3m - 0.500 * khoang_cach
        fibo_618 = dinh_3m - 0.618 * khoang_cach

        # Xác định Kháng cự / Hỗ trợ động
        khang_cu = dinh_3m
        for muc in [fibo_236, fibo_382, fibo_500, fibo_618]:
            if muc > gia_d:
                khang_cu = muc
                break

        ho_tro = day_3m
        for muc in reversed([fibo_236, fibo_382, fibo_500, fibo_618]):
            if muc < gia_d:
                ho_tro = muc
                break
        ho_tro = max(ho_tro, ma50_d if ma50_d < gia_d else day_3m)

        # DỰ BÁO XU HƯỚNG 2 TUẦN TỚI
        if "🟢" in xh_d and "🟢" in xh_w:
            du_bao = "🚀 *XU HƯỚNG TỐT:* Ngắn hạn và trung hạn đồng thuận đi lên. Dự báo 2 tuần tới VN-Index giữ quán tính tăng, hướng về các mốc cao hơn. Chiến lược: Tiếp tục nắm giữ danh mục mạnh."
        elif "🔴" in xh_d and "🔴" in xh_w:
            du_bao = "🚨 *RỦI RO CAO:* Xu hướng sụt giảm đồng thuận nghiêm trọng. Dự báo 2 tuần tới áp lực bán vẫn lớn, chỉ số có nguy cơ giảm về các mốc Fibo sâu hơn. Chiến lược: Hạ tỷ trọng tối đa."
        elif "🟢" in xh_w and ("🟠" in xh_d or "🔴" in xh_d):
            du_bao = "⏳ *ĐIỀU CHỈNH KỸ THUẬT:* Trung hạn vẫn ổn nhưng ngắn hạn đang bị chốt lời. Dự báo 2 tuần tới thị trường sẽ tích lũy lại quanh vùng hỗ trợ cứng. Chiến lược: Canh gom khi giá về vùng hỗ trợ cứng."
        else:
            du_bao = "⚖️ *THỊ TRƯỜNG PHÂN HÓA:* Dòng tiền giằng co đi ngang (Sideway). Dự báo 2 tuần tới chỉ số khó bứt phá mạnh, phân hóa dòng tiền. Chiến lược: Lướt sóng ngắn hạn, tỷ trọng thấp."

        # SOẠN BẢN TIN SỐ LIỆU CUỐI NGÀY
        tin_nhan = f"📊 *BÁO CÁO PHÂN TÍCH VN-INDEX CUỐI NGÀY*\n\n"
        tin_nhan += f"💰 *Điểm số kết phiên:* `{gia_d:.2f}`\n\n"
        
        tin_nhan += f"🔄 *SO SÁNH BIẾN ĐỘNG & XU HƯỚNG:*\n"
        tin_nhan += f" 🔹 *Khung NGÀY:* `{pct_d:+.2f}%` | {xh_d} | Vol: {vol_d}\n"
        tin_nhan += f" 🔹 *Khung TUẦN:* `{pct_w:+.2f}%` | {xh_w} | Vol: {vol_w}\n"
        tin_nhan += f" 🔹 *Khung THÁNG:* `{pct_m:+.2f}%` | {xh_m} | Vol: {vol_m}\n\n"

        tin_nhan += f"📐 *MỐC FIBONACCI (3 Tháng qua):*\n"
        tin_nhan += f" - 🔺 Đỉnh cao: `{dinh_3m:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 23.6%: `{fibo_236:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 38.2%: `{fibo_382:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 50.0%: `{fibo_500:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 61.8%: `{fibo_618:.2f}`\n"
        tin_nhan += f" - 🔻 Đáy sâu: `{day_3m:.2f}`\n\n"

        tin_nhan += f"🛡️ *HỖ TRỢ & KHÁNG CỰ THỰC TẾ:* \n"
        tin_nhan += f" - 🚧 Kháng cự gần: `{khang_cu:.2f} điểm`\n"
        tin_nhan += f" - 🧱 Hỗ trợ cứng: `{ho_tro:.2f} điểm`\n\n"

        tin_nhan += f"🔮 *ĐÁNH GIÁ & DỰ BÁO 2 TUẦN TỚI:*\n"
        tin_nhan += f"{du_bao}\n\n"

        tin_nhan += f"⚠️ *NGUYÊN TẮC VÔ VI NHẮC NHỚ:*\n"
        tin_nhan += f"_\"Giao dịch theo cái thấy, không theo cái nghĩ\"_\n"
        tin_nhan += f"Luôn bám sát hành động giá thực tế tại các mốc hỗ trợ/kháng cự phía trên để ra quyết định kỷ luật!"

        gui_telegram(tin_nhan)

    except Exception as e:
        gui_telegram(f"❌ Lỗi hệ thống khi quét dữ liệu: {str(e)}")

if __name__ == "__main__":
    phan_tich_cuoi_ngay_vni()
