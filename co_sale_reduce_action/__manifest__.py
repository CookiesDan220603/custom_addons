{
    'name': 'Reduce Action Sale',
    'version': '1.0',
    'summary': 'Ẩn/hiển thị các field trong Sale Order',
    'description': """
        Tính năng:
        - Ẩn fields không cần thiết trong Sale Order
        - Filter sản phẩm theo phân loại
        - Stock validation với hiển thị "Hết hàng"
        - In hóa đơn chi tiết PDF với thông tin đầy đủ
        Module cho phép in hóa đơn với:
        - Nút in trong form view account_move
        - Xem trước hóa đơn trực tiếp trên chrome
    """,
    'depends': ['sale', 'sale_management'],
    'category': 'Cookies Modules',
    'data': [
        'reports/invoice_report.xml',
        'reports/invoice_template.xml',
        'reports/custom_layout.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/account_move_views.xml',
    ],
    'assets': {
                'web.assets_backend': [
                    'co_sale_reduce_action/static/src/css/my_report_styles.css',
                ],
            },
    'installable': True,
    'application': True,
}
