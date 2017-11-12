# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------------
import odoorpc
from lib import MilaWorksheet
from secret import odoo_key


"""
    Para funcionar esto requiere los modulos
        product_variant_default_code            Genera la mascara de producto
        product_variants_no_automatic_creation  Evita la creacion automatica de productos
"""


class Makeover():
    def __init__(self, odoo_key):
        self._odoo = odoorpc.ODOO(odoo_key['server'], port=odoo_key['port'])
        self._odoo.login(odoo_key['database'], odoo_key['username'], odoo_key['password'])

    def list_products(self):
        product_template = self._odoo.env['product.template']
        ids = product_template.search([])
        for pro in product_template.browse(ids):
            print pro.id, pro.default_code, pro.name

    def list_variants(self):
        product_product = self._odoo.env['product.product']

        ids = product_product.search([])
        for pro in product_product.browse(ids):
            print pro.id, pro.default_code, pro.name, pro.name_template

    def list_attribute_line(self):
        product_al = self._odoo.env['product.attribute.line']

        ids = product_al.search([])
        for pro in product_al.browse(ids):
            print pro.attribute_id.name

    def add_product(self, name, default_code, cost, seller_id, category, pack):
        '''
            Create a product
            product.template
                attribute_id : product.attribute

        '''

        # chequear el product attribute color
        attribute_ids = self._odoo.env['product.attribute'].search([('name', '=', 'color')])
        if not attribute_ids:
            attribute_id = self._odoo.env['product.attribute'].create({'name': 'color'})
        else:
            attribute_id = attribute_ids[0]

        # buscar la categoria por Marzi o Pro
        categ = self._odoo.env['product.category']
        categ_id = categ.search([('name', 'like', category)])[0]

        # crear el product template
        variant_id = self._odoo.env['product.template'].create({
            'name': name,
            'type': 'product',
            'categ_id': categ_id,
            'standard_price': cost,
            'sale_ok': not pack,
            'state': 'sellable',
            'seller_id': seller_id,
            'cost_method': 'real',
            #'product_variant_ids': -> 'product.product', 'product_tmpl_id',
        })

        prod = self._odoo.env['product.template'].browse(variant_id)
        attribute_lines = {
            'product_tmpl_id': variant_id,
            'attribute_id': attribute_id
        }
        prod.attribute_line_ids = [(0, 0, attribute_lines)]
        prod.reference_mask = '{}-[color]'.format(default_code)

        # crear el producto (esta es la variante)
        product_id = self._odoo.env['product.product'].create({
            ''
        })





mk = Makeover(odoo_key)
mk.add_product('producto creado programatico', '1010', 200.0, False, 'Marzi', False)
