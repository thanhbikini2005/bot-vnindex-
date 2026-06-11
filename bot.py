import requests


def send_telegram_message(message):
    # Thay thế Token và Chat ID của bạn vào đây
    TOKEN = "THAY_THE_BOT_TOKEN_CUA_BAN_VAO_DAY"
    CHAT_ID = "THAY_THE_CHAT_ID_CUA_BAN_VAO_DAY"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",  # Hỗ trợ định dạng chữ đậm, nghiêng
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Gửi tin nhắn thành công!")
        else:
            print(f"Lỗi từ Telegram: {response.text}")
    except Exception as e:
        print(f"Không thể kết nối đến Telegram API: {e}")


# --- BẤT CỨ KHI NÀO MUỐN GỬI, CHỈ CẦN GỌI HÀM NÀY ---
if __name__ == "__main__":
    noi_dung = (
        "🔔 *Thông báo từ Hệ thống VN-Index*\n\n"
        "Thị trường đang ở vùng hỗ trợ 1.790 - 1.800 điểm.\n"
        "Khối lượng giao dịch thấp, có thể cân nhắc giải ngân 30% vị thế."
    )

    send_telegram_message(noi_dung)
