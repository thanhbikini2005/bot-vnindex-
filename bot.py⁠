import os
import requests
import yfinance as yf
import pandas as pd

# Hệ thống tự động bốc chìa khóa bạn đã giấu ở Phần 2
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def gui_telegram(tin_nhan):
    """Hàm gửi tin nhắn định dạng chuyên nghiệp về Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": tin_nhan, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def tinh_khoi_luong_va_xu_huong(df):
    """Hàm tính toán các đường MA xu hướng và khối lượng trung bình"""
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
    
    last = df.iloc[-1]
    gia = float(last['Close'])
    ma20 = float(last['MA20'])
    ma50 = float(last['MA50'])
    vol = float(last['Volume'])
    vol_ma20 = float(last['Vol_MA20'])
    
    # Đo lường xu hướng dựa trên MA
    if gia > ma20 > ma50:
        xh = "🟢 TĂNG MẠNH (Uptrend)"
    elif gia > ma20:
        xh = "🟡 TÍCH LŨY TĂNG (Trên MA20)"
    elif gia < ma20 and gia > ma50:
        xh = "🟠 ĐIỀU CHỈNH (Dưới MA20, trên MA50)"
    else:
        xh = "🔴 GIẢM GIÁ (Downtrend)"
        
    # Đo lường trạng thái dòng tiền (Volume)
    if vol > vol_ma20 * 1.15:
        v_status = "🔥 Lớn (Dòng tiền vào mạnh)"
    elif vol < vol_ma20 * 0.85:
        v_status = "📉 Kiệt (Lực mua/bán yếu)"
    else:
        v_status = "📈 Ổn định (Mức trung bình)"
        
    return gia, xh, v_status, ma20, ma50

def phan_tich_da_khung_vni():
    try:
        # Tải dữ liệu chính xác từ Yahoo Finance (^VNINDEX)
        vni_d = yf.download("^VNINDEX", period="1y", interval="1d")  # Khung Ngày
        vni_w = yf.download("^VNINDEX", period="2y", interval="1wk") # Khung Tuần
        vni_m = yf.download("^VNINDEX", period="5y", interval="1mo") # Khung Tháng

        if vni_d.empty or vni_w.empty or vni_m.empty:
            gui_telegram("❌ Lỗi: Hệ thống không lấy được dữ liệu VN-Index!")
            return

        # Tính toán số liệu của từng khung thời gian
        gia_d, xh_d, vol_d, ma20_d, ma50_d = tinh_khoi_luong_va_xu_huong(vni_d)
        _, xh_w, vol_w, _, _ = tinh_khoi_luong_va_xu_huong(vni_w)
        _, xh_m, vol_m, _, _ = tinh_khoi_luong_va_xu_huong(vni_m)

        # Tính toán phần trăm tăng/giảm so với phiên trước, tuần trước, tháng trước
        pct_d = ((gia_d - float(vni_d.iloc[-2]['Close'])) / float(vni_d.iloc[-2]['Close'])) * 100
        pct_w = ((gia_d - float(vni_w.iloc[-2]['Close'])) / float(vni_w.iloc[-2]['Close'])) * 100
        pct_m = ((gia_d - float(vni_m.iloc[-2]['Close'])) / float(vni_m.iloc[-2]['Close'])) * 100

        # TỰ ĐỘNG VẼ THƯỚC ĐO FIBONACCI (Quét đỉnh/đáy trong 3 tháng qua)
        df_3m = vni_d.tail(60)
        dinh_3m = float(df_3m['High'].max())
        day_3m = float(df_3m['Low'].min())
        khoang_cach = dinh_3m - day_3m

        fibo_236 = dinh_3m - 0.236 * khoang_cach
        fibo_382 = dinh_3m - 0.382 * khoang_cach
        fibo_500 = dinh_3m - 0.500 * khoang_cach
        fibo_618 = dinh_3m - 0.618 * khoang_cach

        # Tự động tìm mốc Kháng cự / Hỗ trợ dựa vào các mức Fibo
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

        # ĐÁNH GIÁ VÀ DỰ BÁO XU HƯỚNG 2 TUẦN TỚI
        if "🟢" in xh_d and "🟢" in xh_w:
            du_bao = "🚀 *XU HƯỚNG TỐT:* Cả ngắn hạn và trung hạn đều đồng thuận đi lên. Dự báo 2 tuần tới VN-Index sẽ tiếp tục quán tính tăng điểm, hướng về mốc kháng cự cao hơn. Chiến lược: Tập trung tối ưu lợi nhuận, tiếp tục nắm giữ."
        elif "🔴" in xh_d and "🔴" in xh_w:
            du_bao = "🚨 *RỦI RO CAO:* Xu hướng sụt giảm đồng thuận trên các khung thời gian. Dự báo trong 2 tuần tới áp lực bán tháo vẫn duy trì, chỉ số có nguy cơ test các mốc Fibo sâu hơn. Chiến lược: Hạ tỷ trọng, phòng thủ nghiêm ngặt."
        elif "🟢" in xh_w and ("🟠" in xh_d or "🔴" in xh_d):
            du_bao = "⏳ *ĐIỀU CHỈNH KỸ THUẬT:* Xu hướng dài hạn (Tuần/Tháng) vẫn ổn định nhưng ngắn hạn (Ngày) đang gặp áp lực chốt lời. Dự báo 2 tuần tới thị trường sẽ rung lắc mạnh và tích lũy lại quanh vùng hỗ trợ cứng. Chiến lược: Không mua đuổi, canh gom khi giá về vùng hỗ trợ."
        else:
            du_bao = "⚖️ *THỊ TRƯỜNG PHÂN HÓA:* Các khung thời gian đang mâu thuẫn nhau, dòng tiền có sự giằng co biên độ hẹp (Sideway). Dự báo 2 tuần tới chỉ số khó bứt phá mạnh. Chiến lược: Giao dịch tỷ trọng thấp, ưu tiên lướt sóng ngắn hạn."

        # SOẠN BẢN TIN GỬI VỀ TELEGRAM
        tin_nhan = f"📊 *BÁO CÁO ĐA KHUNG THỜI GIAN VN-INDEX*\n\n"
        tin_nhan += f"💰 *Điểm số đóng cửa:* `{gia_d:.2f}`\n\n"
        
        tin_nhan += f"🔄 *SO SÁNH BIẾN ĐỘNG & XU HƯỚNG:*\n"
        tin_nhan += f" 🔹 *Khung NGÀY:* `{pct_d:+.2f}%` | Xu hướng: {xh_d} | Vol: {vol_d}\n"
        tin_nhan += f" 🔹 *Khung TUẦN:* `{pct_w:+.2f}%` | Xu hướng: {xh_w} | Vol: {vol_w}\n"
        tin_nhan += f" 🔹 *Khung THÁNG:* `{pct_m:+.2f}%` | Xu hướng: {xh_m} | Vol: {vol_m}\n\n"

        tin_nhan += f"📐 *THƯỚC ĐO FIBONACCI (3 Tháng qua):*\n"
        tin_nhan += f" - 🔺 Đỉnh lớn: `{dinh_3m:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 23.6%: `{fibo_236:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 38.2%: `{fibo_382:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 50.0%: `{fibo_500:.2f}`\n"
        tin_nhan += f" - 🔹 Fibo 61.8%: `{fibo_618:.2f}`\n"
        tin_nhan += f" - 🔻 Đáy lớn: `{day_3m:.2f}`\n\n"

        tin_nhan += f"🛡️ *VÙNG GIÁ TRỌNG YẾU TỰ ĐỘNG:* \n"
        tin_nhan += f" - 🚧 Kháng cự gần: `{khang_cu:.2f} điểm`\n"
        tin_nhan += f" - 🧱 Hỗ trợ cứng: `{ho_tro:.2f} điểm`\n\n"

        tin_nhan += f"🔮 *ĐÁNH GIÁ & DỰ BÁO 2 TUẦN TỚI:*\n"
        tin_nhan += f"{du_bao}\n\n"

        tin_nhan += f"⚠️ *NGUYÊN TẮC VÔ VI NHẮC NHỚ:*\n"
        tin_nhan += f"_\"Giao dịch theo cái thấy, không theo cái nghĩ\"_\n"
        tin_nhan += f"Luôn bám sát hành động giá tại vùng hỗ trợ/kháng cự thực tế để đưa ra quyết định cắt lỗ hoặc chốt lời kỷ luật!"

        gui_telegram(tin_nhan)

    except Exception as e:
        gui_telegram(f"❌ Lỗi xử lý hệ thống: {str(e)}")

if __name__ == "__main__":
    phan_tich_da_khung_vni()
