{
    'name': 'Saigon carcare',
    'version': '1.0',
    'summary': 'tuỳ chỉnh cho saigon carcare',
    'description': """
        Tính năng:
        - Ẩn fields không cần thiết trong Sale Order
        - Filter sản phẩm theo phân loại
        - Stock validation với hiển thị "Hết hàng"
        - In hóa đơn chi tiết PDF với thông tin đầy đủ
        Module cho phép in hóa đơn với:
        - Nút in trong form view account_move
        - Xem trước hóa đơn trực tiếp trên chrome
        - Ẩn fields không cần thiết trong res.partner
        - Filter hóa đơn theo khách - vụ - năm - chưa thanh toán - đã thanh toán
        - In phiếu thanh toán đầy đủ
    """,
    'depends': ['sale', 'sale_management','account','stock'],
    'category': 'Cookies Modules',
    'data': [
        'reports/invoice_report.xml',
        'reports/invoice_template.xml',
        'reports/quote_report.xml',
        'reports/quote_template.xml',
        'reports/custom_layout.xml',
        'reports/construction_order_report.xml',
        'reports/construction_order_template.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/account_move_views.xml',
        'views/co_account_move_views.xml',
        'views/co_account_payment_views.xml',
    ],
    'installable': True,
    'application': True,
}
