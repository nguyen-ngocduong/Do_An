"""Hướng dẫn do nhóm biên soạn từ tài liệu tham khảo; không thực thi hành động."""

from copy import deepcopy


PLAYBOOK_VERSION = "2026-10-28.v1"
NIST_SOURCE = {
    "title": "NIST SP 800-61 Rev. 3 — Incident Response",
    "url": "https://csrc.nist.gov/pubs/sp/800/61/r3/final",
}
SCOPE_NOTE = (
    "Đây là hướng dẫn tham khảo theo lớp model, cần đối chiếu bối cảnh và quyền vận hành. "
    "Chưa xác nhận cuộc tấn công, kỹ thuật MITRE cụ thể, IP hoặc thiết bị liên quan. "
    "Xác suất model không phải mức độ nghiêm trọng. Đánh giá thủ công được lưu riêng, không tự xác nhận nhãn thật."
)

PLAYBOOKS = {
    "Normal": {
        "title": "Theo dõi mẫu được dự đoán Normal",
        "checks": [
            "Nếu có nhật ký cùng bối cảnh, đối chiếu hoạt động dự kiến của dịch vụ và thiết bị.",
            "Nếu có dấu hiệu vận hành bất thường, lưu bằng chứng để kiểm tra thêm dù model trả Normal.",
        ],
        "response_steps": [
            "Lưu kết quả và tiếp tục theo dõi; nhãn Normal chưa bảo đảm hệ thống an toàn.",
            "Nếu xuất hiện bằng chứng bổ sung, chuyển người phụ trách kiểm tra theo quy trình của đơn vị.",
        ],
        "sources": [],
    },
    "BruteForce": {
        "title": "Kiểm tra nghi vấn dò thông tin đăng nhập",
        "checks": [
            "Nếu có log xác thực, đối chiếu các lần đăng nhập thất bại và thành công của dịch vụ liên quan.",
            "Kiểm tra hoạt động đã được cho phép trước khi kết luận các lần thử là hành vi trái phép.",
        ],
        "response_steps": [
            "Nếu xác minh có thử đăng nhập trái phép, người quản trị xem xét MFA và giới hạn số lần thử theo chính sách.",
            "Nếu xác minh tài khoản bị ảnh hưởng, thực hiện quy trình khôi phục thông tin xác thực của đơn vị.",
        ],
        "sources": [{"title": "MITRE ATT&CK — Brute Force", "url": "https://attack.mitre.org/techniques/T1110/"}],
    },
    "DDoS": {
        "title": "Kiểm tra nghi vấn làm gián đoạn mạng từ nhiều nguồn",
        "checks": [
            "Nếu có số liệu mạng, đối chiếu mức sử dụng đường truyền và khả năng đáp ứng của dịch vụ với nền hoạt động.",
            "Nếu có log lưu lượng, kiểm tra phân bố nguồn; CSV đặc trưng hiện tại chưa xác định các địa chỉ đó.",
        ],
        "response_steps": [
            "Nếu xác minh dịch vụ bị ảnh hưởng, chuyển đơn vị mạng hoặc nhà cung cấp để đánh giá phương án giảm thiểu DDoS.",
            "Chỉ áp dụng lọc lưu lượng theo quy trình đã phê duyệt và theo dõi khả năng phục hồi dịch vụ.",
        ],
        "sources": [{"title": "MITRE ATT&CK — Network Denial of Service", "url": "https://attack.mitre.org/techniques/T1498/"}],
    },
    "DoS": {
        "title": "Kiểm tra nghi vấn làm gián đoạn dịch vụ",
        "checks": [
            "Nếu có log dịch vụ và số liệu tài nguyên, kiểm tra lỗi, tải và tình trạng đáp ứng trong bối cảnh liên quan.",
            "Đối chiếu sự cố cấu hình hoặc tải hợp lệ; nhãn DoS chưa xác định cơ chế gây gián đoạn.",
        ],
        "response_steps": [
            "Nếu xác minh sự cố, người phụ trách đánh giá biện pháp bảo vệ tài nguyên hoặc lọc lưu lượng phù hợp.",
            "Khôi phục dịch vụ theo quy trình của đơn vị và tiếp tục theo dõi sau xử lý.",
        ],
        "sources": [
            {"title": "MITRE ATT&CK — Network Denial of Service", "url": "https://attack.mitre.org/techniques/T1498/"},
            {"title": "MITRE ATT&CK — Endpoint Denial of Service", "url": "https://attack.mitre.org/techniques/T1499/"},
        ],
    },
    "Mirai": {
        "title": "Kiểm tra thiết bị IoT có dấu hiệu cần điều tra",
        "checks": [
            "Nếu xác định được thiết bị từ nguồn khác, kiểm tra phiên bản phần mềm và cấu hình truy cập quản trị.",
            "Nếu có log kết nối, đối chiếu hoạt động ngoài dự kiến; nhãn Mirai chưa chứng minh thiết bị nhiễm botnet.",
        ],
        "response_steps": [
            "Người phụ trách kiểm tra thông tin xác thực mặc định và cập nhật được nhà sản xuất hỗ trợ.",
            "Nếu xác minh thiết bị bị ảnh hưởng, xử lý và khôi phục theo hướng dẫn nhà sản xuất và quy trình của đơn vị.",
        ],
        "sources": [{
            "title": "UK Government — Code of Practice for Consumer IoT Security",
            "url": "https://www.gov.uk/government/publications/code-of-practice-for-consumer-iot-security/code-of-practice-for-consumer-iot-security",
        }],
    },
    "Recon": {
        "title": "Kiểm tra nghi vấn dò tìm dịch vụ",
        "checks": [
            "Nếu có log firewall hoặc lưu lượng, đối chiếu các lần truy cập dịch vụ trong cùng bối cảnh.",
            "Kiểm tra lịch quét được cho phép và danh sách công cụ quản trị trước khi kết luận dò quét trái phép.",
        ],
        "response_steps": [
            "Nếu xác minh hoạt động ngoài phạm vi cho phép, người quản trị rà soát dịch vụ đang công khai và quyền truy cập.",
            "Ghi nhận phạm vi quan sát và chuyển người phụ trách để đánh giá bước kiểm tra tiếp theo.",
        ],
        "sources": [{"title": "MITRE ATT&CK — Network Service Discovery", "url": "https://attack.mitre.org/techniques/T1046/"}],
    },
    "Spoofing": {
        "title": "Kiểm tra nghi vấn giả mạo thông tin mạng",
        "checks": [
            "Nếu có log ARP, DHCP hoặc DNS, đối chiếu các thay đổi ánh xạ với cấu hình và danh mục thiết bị.",
            "Kiểm tra thay đổi hợp lệ; nhãn Spoofing chưa xác định giao thức hoặc địa chỉ bị giả mạo.",
        ],
        "response_steps": [
            "Nếu xác minh ánh xạ trái phép, người quản trị mạng xem xét cơ chế bảo vệ tương ứng với hạ tầng thực tế.",
            "Lưu bằng chứng và xác minh cấu hình sau xử lý theo quy trình của đơn vị.",
        ],
        "sources": [{"title": "MITRE ATT&CK — Adversary-in-the-Middle", "url": "https://attack.mitre.org/techniques/T1557/"}],
    },
    "Web-Based": {
        "title": "Kiểm tra nghi vấn liên quan ứng dụng web",
        "checks": [
            "Nếu có access log, log ứng dụng hoặc WAF, đối chiếu yêu cầu và phản hồi trong bối cảnh liên quan.",
            "Kiểm tra hoạt động kiểm thử đã được cho phép; nhãn Web-Based chưa xác định SQL injection, XSS hay lỗ hổng cụ thể.",
        ],
        "response_steps": [
            "Nếu xác minh yêu cầu độc hại, nhóm ứng dụng đánh giá cấu hình bảo vệ và bản vá phù hợp với phần mềm thực tế.",
            "Nếu có bằng chứng xâm nhập, chuyển quy trình ứng phó sự cố; không gán CVE từ tên lớp model.",
        ],
        "sources": [{"title": "MITRE ATT&CK — Exploit Public-Facing Application", "url": "https://attack.mitre.org/techniques/T1190/"}],
    },
}


def get_playbook(class_name):
    if class_name not in PLAYBOOKS:
        raise ValueError("Tên lớp không thuộc tám lớp đã chốt.")
    result = deepcopy(PLAYBOOKS[class_name])
    result.update(class_name=class_name, version=PLAYBOOK_VERSION, scope_note=SCOPE_NOTE, automatic_actions=False)
    result["sources"].append(dict(NIST_SOURCE))
    return result
