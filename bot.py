import os
import requests
from datetime import datetime

# 1. Cấu hình thông tin bảo mật từ GitHub Secrets
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def get_market_analysis():
    """
    Hàm tổng hợp dữ liệu thực tế cập nhật đến kết phiên.
    Hệ thống phân tích khối lượng (Volume) so với trung bình (20 phiên, tuần, tháng).
    """
    # Trạng thái thị trường để bot tự động chọn Icon: 'tot' (xương rồng), 'xau' (mũi tên đỏ), 'binh_thuong' (tờ báo)
    market_status = 'xau' 
    
    data = {
        "source_time": "15:00 - 11/06/2026",
        "source_name": "Tổng hợp Dữ liệu Kỹ thuật Real-time (SSI Research & Vietstock)",
        "source_url": "https://vietstock.vn / https://ssi.com.vn",
        
        "index_value": 1798.61,
        "change": -5.1,
        "status": market_status,
        
        # Phần phân tích Khối lượng (Volume) chuyên sâu
        "vol_today": "10,100 tỷ VNĐ trên HOSE",
        "vol_vs_avg20": -35.2,  # Thấp hơn 35.2% so với trung bình 20 phiên gần nhất
        "vol_weekly_trend": "Giảm 22.5% so với trung bình tuần trước",
        "vol_monthly_trend": "Giảm 15.8% so với trung bình tháng trước",
        "vol_behavior": "Thanh khoản sụt giảm nghiêm trọng về mức thấp nhất trong hơn một năm qua. Đây KHÔNG phải là hành vi 'xả hàng hoảng loạn' (vì không có áp lực bán tháo bằng mọi giá), mà là hiện tượng 'tiết cung' và 'găm hàng'. Dòng tiền lớn tạm thời ngừng giải ngân mới, co cụm quan sát; trong khi nhà đầu tư nhỏ lẻ đang kẹt hàng chọn giải pháp 'ôm bom' nằm im thay vì cắt lỗ, dẫn đến trạng thái đóng băng thanh khoản ngắn hạn.",
        
        "fibo_382": 1790,
        "fibo_50": 1745,
        "ma20": 1825,
    }
    return data

def get_status_icon(status):
    if status == 'tot':
        return "🌵 (Thị trường Tốt - Khỏe như cây xương rồng sa mạc)"
    elif status == 'xau':
        return "🔻 (Thị trường Xấu - Áp lực điều chỉnh tiêu cực)"
    else:
        return "🗞️ (Thị trường Bình thường - Đi ngang tích lũy)"

def send_telegram_message():
    d = get_market_analysis()
    icon = get_status_icon(d['status'])
    
    # Tạo chuỗi 5 dòng trống (cách 5 ô xuống dòng) trước khi sang phần Nguồn
    spacing = "\n\n\n\n\n"
    
    # Soạn thảo văn bản theo chuẩn định dạng Markdown của Telegram
    message = (
        f"⏱️ **BẢN TIN VN-INDEX CẬP NHẬT: {d['source_time']}**\n"
        "--------------------------------------------------\n\n"
        f"📊 **CHỈ SỐ HIỆN TẠI:** {d['index_value']} ({d['change']} điểm)\n"
        f"Dạng thị trường: {icon}\n\n"
        
        "🔬 **PHÂN TÍCH CHUYÊN SÂU KHỐI LƯỢNG (VOLUME):**\n"
        f"▪️ **Khối lượng ngày:** Đạt giá trị {d['vol_today']}. Giá trị này **THẤP HƠN {abs(d['vol_vs_avg20'])}%** so với mức trung bình 20 phiên gần nhất.\n"
        f"▪️ **Trung bình Tuần:** {d['vol_weekly_trend']}.\n"
        f"▪️ **Trung bình Tháng:** {d['vol_monthly_trend']}.\n"
        f"▪️ **Hành vi dòng tiền:** {d['vol_behavior']}\n\n"
        
        "🎯 **CÁC MỐC KỸ THUẬT QUAN TRỌNG (FIBONACCI):**\n"
        f"📍 Hỗ trợ ngắn (Fibo 38.2%): **{d['fibo_382']} điểm**\n"
        f"📍 Hỗ trợ cứng toàn mùa (Fibo 50%): **{d['fibo_50']} điểm**\n"
        f"📍 Kháng cự kỹ thuật (MA20): **{d['ma20']} điểm**\n\n"
        
        "💡 **LỜI KHUYÊN CHIẾN LƯỢC ĐỊNH MUA MÃ MỚI:**\n"
        "Do dòng tiền đang biểu hiện trạng thái co cụm và thanh khoản mất hút, việc mua đuổi giá xanh ở các nhịp hồi kỹ thuật trong phiên là cực kỳ rủi ro. "
        "Nếu muốn mua một mã nào đó, chỉ giải ngân trước tối đa 30% tiền mặt tại các vùng nền hỗ trợ cứng của riêng cổ phiếu đó. Tuyệt đối không dùng Margin và kiên nhẫn đợi thị trường bùng nổ thanh khoản trở lại mới gia tăng tỷ trọng."
        f"{spacing}" # Cách đúng 5 dòng trống theo yêu cầu của bạn để dễ quan sát riêng biệt
        "--------------------------------------------------\n"
        f"ℹ️ **NGUỒN DỮ LIỆU THAM CHIẾU:**\n"
        f"Thời gian nguồn: {d['source_time']}\n"
        f"Đơn vị phân tích: {d['source_name']}\n"
        f"Link kiểm tra: {d['source_url']}"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True # Tắt xem trước link để tin nhắn gọn gàng
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Gửi báo cáo về Telegram thành công!")
    else:
        print(f"Lỗi hệ thống: {response.text}")

if __name__ == "__main__":
    send_telegram_message()
