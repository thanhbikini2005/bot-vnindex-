import os
import requests
import pandas as pd

# 1. Cấu hình thông tin bảo mật từ GitHub Secrets
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def get_market_data():
    """
    Hàm giả lập gọi dữ liệu VN-Index. 
    Trong thực tế, bạn có thể cấu hình API endpoint từ các nguồn dữ liệu cung cấp 
    hoặc cào dữ liệu real-time từ các trang tài chính uy tín.
    """
    # Các thông số phân tích kỹ thuật (Cập nhật tự động/Scrape)
    data = {
        "index_value": 1798.61,
        "change": -5.1,
        "volume_hoan_thien": "10,100 tỷ VNĐ (Thấp kỷ lục)",
        "fibo_382": 1790,
        "fibo_50": 1745,
        "ma20": 1825,
        "rsi": 42
    }
    return data

def rsi_evaluation(rsi):
    if rsi < 30: return "Quá bán (Cơ hội tích lũy)"
    elif rsi > 70: return "Quá mua (Rủi ro điều chỉnh)"
    return f"{rsi} - Trung tính (Thị trường đang tích lũy đi ngang)"

def send_telegram_message():
    d = get_market_data()
    
    # Soạn thảo văn bản gửi về Telegram dạng Markdown
    message = (
        "📊 **CẬP NHẬT VN-INDEX & PHÂN TÍCH KỸ THUẬT** 📊\n"
        "------------------------------------\n"
        f"🔹 **Điểm số:** {d['index_value']} ({d['change']} điểm)\n"
        f"🔹 **Thanh khoản:** {d['volume_hoan_thien']}\n"
        f"🔹 **Chỉ báo RSI:** {rsi_evaluation(d['rsi'])}\n\n"
        "🎯 **Các mốc kỹ thuật đáng chú ý (Fibonacci):**\n"
        f"📍 Hỗ trợ cứng (Fibo 50%): **{d['fibo_50']} điểm**\n"
        f"📍 Hỗ trợ ngắn hạn (Fibo 38.2%): **{d['fibo_382']} điểm**\n"
        f"📍 Kháng cự gần (MA20): **{d['ma20']} điểm**\n\n"
        "💡 **Lời khuyên hành động:** Thị trường cạn voL (tiết cung), tránh mua đuổi trong các phiên kéo xanh kỹ thuật. Chia tiền làm 3 phần giải ngân từng bước khi có tín hiệu dòng tiền lan tỏa."
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
