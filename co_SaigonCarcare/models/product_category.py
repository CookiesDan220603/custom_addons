from odoo import models

class ProductCategory(models.Model):
    _inherit = 'product.category'

    def get_all_child_ids(self, category_id):
        result = []
        category = self.browse(category_id)
        if category:
            for child in category.child_id:
                result.append(child.id)
                result.extend(self.get_all_child_ids(child.id))
        return result

    def get_product_domain(self, category_id):
        """ Trả về domain cho product.template """
        all_ids = self.get_all_child_ids(category_id)
        all_ids.append(category_id)  # bao gồm cả chính nó
        return [
            ('categ_id', 'in', all_ids),
            ('sale_ok', '=', True)
        ]
