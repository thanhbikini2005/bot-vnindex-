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

def phan_tich_vni_tu_tcbs():
    try:
        # Gọi trực tiếp đường link API mở của TCBS để lấy dữ liệu lịch sử VN-Index
        url = "https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/bars-ticker?ticker=VNINDEX&type=stock&resolution=D&from=1672531200&to=1893456000"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers).json()
        
        if 'data' not in response or not response['data']:
            gui_telegram("❌ Lỗi: API của TCBS không trả về dữ liệu hoặc đã đổi cấu trúc!")
            return
            
        data_list = response['data']
        
        # Chuyển đổi dữ liệu từ TCBS thành bảng số liệu để tính toán
        records = []
        for item in data_list:
            records.append({
                'Date': item.get('tradingDate'),
                'Open': float(item.get('open')),
                'High': float(item.get('high')),
                'Low': float(item.get('low')),
                'Close': float(item.get('close')),
                'Volume': float(item.get('volume'))
            })
            
        df_daily = pd.DataFrame(records)
        df_daily['Date'] = pd.to_datetime(df_daily['Date'])
        df_daily = df_daily.sort_values('Date').reset_index(drop=True)
        df_daily.set_index('Date', inplace=True)
        
        # Đảm bảo lấy đủ số phiên để phân tích
        if len(df_daily) < 100:
            gui_telegram("❌ Lỗi: Dữ liệu lịch sử từ TCBS trả về quá ngắn không đủ tính toán!")
            return

        # Tạo dữ liệu khung Tuần và khung Tháng từ dữ liệu gốc của TCBS
        df_weekly = df_daily.resample('W').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
        df_monthly = df_daily.resample('ME').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})

        # Tính toán phân tích các thông số kỹ thuật
        gia_d, xh_d, vol_d, ma20_d, ma50_d = tinh_xu_huong_va_vol(df_daily)
        _, xh_w, vol_w, _, _ = tinh_xu_huong_va_vol(df_weekly)
        _, xh_m, vol_m, _, _ = tinh_xu_huong_va_vol(df_monthly)

        # Tính tỷ lệ biến động phần trăm % so với phiên/tuần/tháng trước đó
        pct_d = ((gia_d - float(df_daily.iloc[-2]['Close'])) / float(df_daily.iloc[-2]['Close'])) * 100
        pct_w = ((gia_d - float(df_weekly.iloc[-2]['Close'])) / float(df_weekly.iloc[-2]['Close'])) * 100
        pct_m = ((gia_d - float(df_monthly.iloc[-2]['Close'])) / float(df_monthly.iloc[-2]['Close'])) * 100

        # TÍNH TOÁN FIBONACCI THOÁI LUI (Quét vùng đỉnh/đáy lớn trong 3 tháng qua ~ 60 phiên)
        df_3m = df_daily.tail(60)
        dinh_3m = float(df_3m['High'].max())
        day_3m = float(df_3m['Low'].min())
        khoang_cach = dinh_3m - day_3m

        fibo_236 = dinh_3m - 0.236 * khoang_cach
        fibo_382 = dinh_3m - 0.382 * khoang_cach
        fibo_500 = dinh_3m - 0.500 * khoang_cach
        fibo_618 = dinh_3m - 0.618 * khoang_cach

        # Tự động tìm Kháng cự động dựa trên mốc Fibonacci cao hơn giá hiện tại
        khang_cu = dinh_3m
        for muc in [fibo_236, fibo_382, fibo_500, fibo_618]:
            if muc > gia_d:
                khang_cu = muc
                break

        # Tự động tìm Hỗ trợ động dựa trên mốc Fibonacci hoặc MA50 trung hạn
        ho_tro = day_3m
        for muc in reversed([fibo_236, fibo_382, fibo_500, fibo_618]):
            if muc < gia_d:
                ho_tro = muc
                break
        ho_tro = max(ho_tro, ma50_d if ma50_d < gia_d else day_3m)

        # ĐÁNH GIÁ VÀ DỰ BÁO XU HƯỚNG TƯƠNG LAI 2 TUẦN TỚI
        if "🟢" in xh_d and "🟢" in xh_w:
            du_bao = "🚀 *XU HƯỚNG TỐT:* Cả ngắn hạn và trung hạn đồng thuận hướng lên. Dự báo 2 tuần tới VN-Index giữ vững đà tăng, tiếp tục hướng về các vùng cao hơn. Chiến lược: Ưu tiên nắm giữ danh mục mạnh."
        elif "🔴" in xh_d and "🔴" in xh_w:
            du_bao = "🚨 *RỦI RO CAO:* Xu hướng giảm điểm đồng thuận mạnh mẽ. Dự báo 2 tuần tới áp lực bán tháo vẫn lớn, chỉ số dễ thủng các mốc hỗ trợ tiếp theo. Chiến lược: Hạ tỷ trọng cổ phiếu, giữ tiền mặt phòng thủ."
        elif "🟢" in xh_w and ("🟠" in xh_d or "🔴" in xh_d):
            du_bao = "⏳ *ĐIỀU CHỈNH KỸ THUẬT:* Trung hạn xu hướng lớn vẫn tốt nhưng ngắn hạn đang gặp áp lực chốt lời. Dự báo 2 tuần tới thị trường sẽ rung lắc mạnh để tạo nền tích lũy mới quanh hỗ trợ cứng. Chiến lược: Kiên nhẫn chờ điểm cân bằng tại vùng hỗ trợ, không mua đuổi."
        else:
            du_bao = "⚖️ *THỊ TRƯỜNG PHÂN HÓA:* Dòng tiền giằng co đi ngang (Sideway) biên độ hẹp. Dự báo 2 tuần tới chỉ số khó bứt phá mạnh, dòng tiền luân chuyển liên tục giữa các nhóm ngành nhỏ. Chiến lược: Tỷ trọng thấp, tập trung trading lướt sóng ngắn hạn."

        # SOẠN BẢN TIN BÁO CÁO GỬI TELEGRAM
        tin_nhan = f"📊 *BÁO CÁO PHÂN TÍCH VN-INDEX ĐA KHUNG (NGUỒN TCBS)*\n\n"
        tin_nhan += f"💰 *Điểm số kết phiên:* `{gia_d:.2f}`\n\n"
        
        tin_nhan += f"🔄 *SO SÁNH BIẾN ĐỘNG & XU HƯỚNG:*\n"
        tin_nhan += f" 🔹 *Khung NGÀY:* `{pct_d:+.2f}%` | {xh_d} | Vol: {vol_d}\n"
        tin_nhan += f" 🔹 *Khung TUẦN:* `{pct_w:+.2f}%` | {xh_w} | Vol: {vol_w}\n"
        tin_nhan += f" 🔹 *Khung THÁNG:* `{pct_m:+.2f}%` | {xh_m} | Vol: {vol_m}\n\n"

        tin_nhan += f"📐 *MỐC FIBONACCI THOÁI LUI (3 Tháng qua):*\n"
        tin_nhan += f" - 🔺 Đỉnh cao nhất: `{dinh_3m:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 23.6%: `{fibo_236:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 38.2%: `{fibo_382:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 50.0%: `{fibo_500:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 61.8%: `{fibo_618:.2f}`\n"
        tin_nhan += f" - 🔻 Đáy thấp nhất: `{day_3m:.2f}`\n\n"

        tin_nhan += f"🛡️ *HỖ TRỢ & KHÁNG CỰ THỰC TẾ ĐỘNG:* \n"
        tin_nhan += f" - 🚧 Kháng cự gần: `{khang_cu:.2f} điểm`\n"
        tin_nhan += f" - 🧱 Hỗ trợ cứng: `{ho_tro:.2f} điểm`\n\n"

        tin_nhan += f"🔮 *ĐÁNH GIÁ & DỰ BÁO XU HƯỚNG 2 TUẦN TỚI:*\n"
        tin_nhan += f"{du_bao}\n\n"

        tin_nhan += f"⚠️ *NGUYÊN TẮC VÔ VI NHẮC NHỚ:*\n"
        tin_nhan += f"_\"Giao dịch theo cái thấy, không theo cái nghĩ\"_\n"
        tin_nhan += f"Hãy nhìn sự thật hiển thị trên bảng điện và hành động kỷ luật theo các mốc hỗ trợ/kháng cự thực tế của thị trường!"

        gui_telegram(tin_nhan)

    except Exception as e:
        gui_telegram(f"❌ Lỗi hệ thống khi phân tích dữ liệu TCBS: {str(e)}")

if __name__ == "__main__":
    phan_tich_vni_tu_tcbs()
