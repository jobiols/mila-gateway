# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------------
#
#    Copyright (C) 2017  jeo Software  (http://www.jeosoft.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ----------------------------------------------------------------------------------
import odoorpc
from lib import MilaWorksheet
from secret import odoo_key

"""
  Carga los productos y precios de la planilla discontinuos.xlsx
"""
# conectar con odoo
odoo = odoorpc.ODOO(odoo_key['server'], port=odoo_key['port'])
odoo.login(odoo_key['database'], odoo_key['username'], odoo_key['password'])

prods_odoo_obj = odoo.env['product.product']
mila_np = MilaWorksheet('discontinuos.xlsx')

MILA_CATEGS = [3, 25, 45, 26, 49, 53]


def process_obsolete_mila_prods():
    """ marca en odoo los producos obsoletos """
    # get all mila prods
    ids = prods_odoo_obj.search([('categ_id', 'in', MILA_CATEGS)])
    for odoo_prod in prods_odoo_obj.browse(ids):
        # check mila worksheets
        mila_prod = mila_np.prod(odoo_prod.default_code)
        if not mila_prod:
            # El producto está obsoloeto ponerlo obsoleto en Odoo
            odoo_prod.state = 'obsolete'
            print 'obsoleto', odoo_prod.name


def process_all_worksheet_prods():
    print 'actualizando productos en odoo'
    """ actualiza o agrega los productos en odoo """
    for mila_prod in mila_np.list():
        # busco en odoo
#        assert mila_prod.ctrl in ['MM', 'MP']
        ids = prods_odoo_obj.search([('default_code', '=', mila_prod.code)])
        if ids:
            # está en odoo
            odoo_prod = prods_odoo_obj.browse(ids)
            # asegurar que solo hay uno
            if len(ids) > 1:
                print '{} está {} veces'.format(mila_prod.code, len(ids))
            assert len(ids) == 1
            for prod in odoo_prod:
                prod.lst_price = mila_prod.price
                prod.name = mila_prod.desc
                prod.cost_method = 'real'
                prod.standard_price = mila_prod.price * 0.41095
                prod.sale_ok = not mila_prod.pack
#                prod.categ_id = 25 if mila_prod.ctrl == 'MM' else 26
                print 'update ', mila_prod.code, mila_prod.desc, prod.categ_id
        else:
            # no está en odoo, lo agregamos
            id_prod = prods_odoo_obj.create({
                'default_code': mila_prod.code,
                'lst_price': mila_prod.price,
                'name': mila_prod.desc,
                'cost_method': 'real',
                'categ_id': 25 if mila_prod.ctrl == 'MM' else 26,
                'standard_price': mila_prod.price * 0.41095,
                'sale_ok': not mila_prod.pack
            })
            print 'add id, code, desc', id_prod, mila_prod.code, mila_prod.desc


def check_new_worksheet():
    print 'Esta en odoo no esta en mila (productos discontinuados)'
    # chequear lo que está en odoo y no está en mila
    ids = prods_odoo_obj.search([('categ_id', 'in', MILA_CATEGS)])
    for odoo_prod in prods_odoo_obj.browse(ids):
        # busco en mila
        mila_prod = mila_np.prod(odoo_prod.default_code)
        if not mila_prod:
            print u'> {:10} {}'.format(odoo_prod.default_code, odoo_prod.name)

    print
    print 'esta en mila no esta en odoo (productos nuevos)'
    # chequear lo que está en mila y no está en odoo
    for mila_prod in mila_np.list():
        # busco en odoo
        ids = prods_odoo_obj.search([('default_code', '=', mila_prod.code)])
        if not ids:
            print '>', mila_prod.list()


def update_odoo_products():
    # bajar los productos discontinuados
    ids = prods_odoo_obj.search([('categ_id', 'in', MILA_CATEGS)])
    for odoo_prod in prods_odoo_obj.browse(ids):
        # busco en mila
        mila_prod = mila_np.prod(odoo_prod.default_code)
        if not mila_prod:
            print u'> {:10} {}'.format(odoo_prod.default_code, odoo_prod.name)


def list_categ():
    categ_obj = odoo.env['product.category']
    ids = MILA_CATEGS
    categs = categ_obj.browse(ids)
    for cat in categs:
        print cat.id, cat.name


def list_products():
    ids = prods_odoo_obj.search([('id', '=', '4150')])
    prods = prods_odoo_obj.browse(ids)
    for prod in prods:
        print prod.id, prod.default_code, prod.name, prod.active


# process_obsolete_mila_prods()
process_all_worksheet_prods()
# list_categ()
#check_new_worksheet()
# list_products()
