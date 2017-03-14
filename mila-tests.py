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

# conectar con odoo
odoo = odoorpc.ODOO(odoo_key['server'], port=odoo_key['port'])
odoo.login(odoo_key['database'], odoo_key['username'], odoo_key['password'])

prods_odoo_obj = odoo.env['product.product']
mila_np = MilaWorksheet('2017-03-07 NOTA DE PEDIDO.xlsx')

print 'Esta en odoo no esta en mila (productos discontinuados)'
# chequear lo que está en odoo y no está en mila
ids = prods_odoo_obj.search([('categ_id', 'in', [3, 25, 26, 53])])
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
