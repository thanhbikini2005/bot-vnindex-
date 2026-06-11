import os
import requests
import pandas as pd
from datetime import datetime
import pytz

# 1. Cấu hình thông tin bảo mật từ GitHub Secrets
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def get_market_data():
    """
    Hàm giả lập lấy dữ liệu VN-Index và trạng thái thị trường.
    Hệ thống tự động phân loại để gán icon động phù hợp.
    """
    # Trạng thái thị trường: 'tot' (tốt), 'xau' (xấu), 'binh_thuong' (bình thường)
    data = {
        "index_value": 1798.61,
        "change": -5.1,
        "volume_hoan_thien": "10,100 tỷ VNĐ (Thấp kỷ lục)",
        "fibo_382": 1790,
        "fibo_50": 1745,
        "ma20": 1825,
        "rsi": 42,
        "status_xu_huong": "xau",          # VN-Index giảm điểm, gãy MA20 ngắn hạn
        "status_thanh_khoan": "binh_thuong", # Thanh khoản thấp kỷ lục (tiết cung)
        "status_tong_ket": "binh_thuong"     # Thị trường đi ngang tích lũy
    }
    return data

def get_status_icon(status):
    """Trả về icon theo đúng yêu cầu của bạn"""
    if status == "tot":
        return "🌵" # Cây xương rồng green cho tin tốt
    elif status == "xau":
        return "🔻" # Mũi tên đỏ chổng xuống cho tin xấu
    else:
        return "🗞️" # Tờ báo cuộn cho tin bình thường

def rsi_evaluation(rsi):
    if rsi < 30: return f"Quá bán (Cơ hội tích lũy)"
    elif rsi > 70: return f"Quá mua (Rủi ro điều chỉnh)"
    return f"{rsi} - Trung tính (Tích lũy đi ngang)"

def send_telegram_message():
    d = get_market_data()
    
    # Lấy ngày giờ hiện tại theo múi giờ Việt Nam (ICT)
    tz_vietnam = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_vietnam).strftime("%d/%m/%Y %H:%M:%S")
    
    # Xác định các icon động dựa trên trạng thái dữ liệu
    icon_xu_huong = get_status_icon(d['status_xu_huong'])
    icon_thanh_khoan = get_status_icon(d['status_thanh_khoan'])
    icon_tong_ket = get_status_icon(d['status_tong_ket'])
    
    # Soạn thảo văn bản gửi về Telegram dạng Markdown
    message = (
        f"⏱️ **BẢN TIN PHÁT HÀNH LÚC:** {current_time}\n"
        "📊 **CẬP NHẬT VN-INDEX & PHÂN TÍCH KỸ THUẬT** 📊\n"
        "------------------------------------\n"
        f"{icon_xu_huong} **Điểm số & Xu hướng:** {d['index_value']} ({d['change']} điểm) -> Vận động dưới các đường MA ngắn hạn.\n"
        f"{icon_thanh_khoan} **Thanh khoản:** {d['volume_hoan_thien']}.\n"
        f"🗞️ **Chỉ báo RSI:** {rsi_evaluation(d['rsi'])}\n\n"
        "🎯 **Các mốc kỹ thuật đáng chú ý (Fibonacci):**\n"
        f"📍 Hỗ trợ cứng (Fibo 50%): **{d['fibo_50']} điểm**\n"
        f"📍 Hỗ trợ ngắn hạn (Fibo 38.2%): **{d['fibo_382']} điểm**\n"
        f"📍 Kháng cự gần (MA20): **{d['ma20']} điểm**\n\n"
        f"{icon_tong_ket} **Tổng kết & Lời khuyên hành động:**\n"
        "Thị trường đang trong pha cạn vol (tiết cung), tránh hoảng loạn bán tháo nhưng cũng tuyệt đối không mua đuổi trong các phiên kéo xanh kỹ thuật. "
        "Nếu định giải ngân mua mới một mã nào đó, hãy chia tiền làm 3 phần: lấy vị thế trước 30% tại nền, phòng thủ 30% nếu thị trường quét về vùng hỗ trợ Fibo 50% (1745 điểm) và chỉ đánh gia tăng khi có dòng tiền lớn xác nhận đánh bùng nổ vượt MA20.\n"
        "\n" # Cách dòng 1
        "\n" # Cách dòng 2
        "\n" # Cách dòng 3
        "\n" # Cách dòng 4
        "\n" # Cách dòng 5 (Đủ 5 dòng trống để dễ nhìn theo yêu cầu)
        "--- HẾT BẢN TIN ---"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Gửi tin nhắn Telegram thành công!")
    else:
        print(f"Lỗi gửi tin nhắn: {response.text}")

if __name__ == "__main__":
    send_telegram_message()
