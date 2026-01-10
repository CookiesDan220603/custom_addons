{
    'name': 'Payment addons function',
    'version': '1.0',
    'summary': 'Tạo smart button xem hóa đơn trong res.partner'
               'Chọn nhiều hóa đơn tiến thành ghi nhận thanh toán',
    'description': """
        Tính năng:
        - Ẩn fields không cần thiết trong res.partner
        - Filter hóa đơn theo khách - vụ - năm - chưa thanh toán - đã thanh toán
        - In phiếu thanh toán đầy đủ
    """,
    'depends': ['sale', 'account','contacts'],
    'category': 'Cookies Modules',
    'data': [
        'views/res_partner_views.xml',
        'views/co_account_move_views.xml',
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': True,
}
