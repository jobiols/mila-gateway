# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------
import odoorpc
from secret import odoo_key
import csv

MILA_CATEGS = [3, 25, 45, 26, 49, 53]
MILA_PRECIOS = '2019-04-mila-precios-master.csv'


class Product(object):
    def __init__(self, data=False, object=False):
        self._data = data
        self._object = object

        if self._data:
            assert self._data['categ_id'] in ['MM', 'MP']

    def formatted(self):
        return "'" + self.get_code() + "'"
        return u'{:10}  {}  {}'.format(self.get_code(), self.get_list_price(),
                                       self.get_name())

    def get_code(self):
        return self._object.default_code if self._object else self._data[
            'default_code']

    def get_list_price(self):
        return self._object.lst_price if self._object else self._data[
            'lst_price']

    def get_standard_price(self):
        return self._data['lst_price'] * 0.41095

    def get_name(self):
        return self._object.name if self._object else self._data['name']

    def get_categ(self):
        if self._object:
            return self._object.categ_id
        else:
            return 25 if self._data['categ_id'] == 'MM' else 26

    def get_prod_pack(self):
        name = self.get_name()
        return name.find('PACK') > -1

    def obj(self):
        return self._object


class ProductData(object):
    def __init__(self):
        self._pro = []

    def all_odoo(self, odoo_key):
        """ Base class """
        pass

    def all_csv(self, filename):
        """ Base class """
        pass

    def all(self):
        return self._pro

    def find(self, prod):
        for pro in self._pro:
            if prod.get_code() == pro.get_code():
                return pro
        return False


class OdooDb(ProductData):
    def __init__(self, odoo_key):
        self._odoo_key = odoo_key
        self._odoo = odoorpc.ODOO(self._odoo_key['server'],
                                  port=self._odoo_key['port'])
        self._odoo.login(self._odoo_key['database'],
                         self._odoo_key['username'],
                         self._odoo_key['password'])
        self._prods_odoo_obj = self._odoo.env['product.product']

    def all_odoo(self):
        self._pro = []

        print 'getting ids'
        # get all mila prods categoria mila y estado no obsoleto
        # hay que traer explicitamente los productos no activos.
        ids = self._prods_odoo_obj.search([('categ_id', 'in', MILA_CATEGS)])
        ids += self._prods_odoo_obj.search([('categ_id', 'in', MILA_CATEGS),
                                            ('active', '=', False)])
        print 'browsing prods'
        for odoo_prod in self._prods_odoo_obj.browse(ids):
            self._pro.append(Product(object=odoo_prod))


class CsvFile(ProductData):
    # devuelve un writer para escribir un archivo csv sin quotas
    def write_csv(self):
        writer = csv.writer(open(self.filename, 'wb'),
                            delimiter=',',
                            quotechar='',
                            quoting=csv.QUOTE_NONE)
        return writer

    # devuelve un reader para leer un archivo csv
    def _read_csv(self, filename):
        return csv.reader(open(filename, 'rb'))

    def all_csv(self, filename):
        reader = self._read_csv(filename)
        first_line = True
        for line in reader:
            if first_line:
                header = line
                first_line = False
                continue

            self._pro.append(Product(data={
                'categ_id': line[header.index('categ_id')],
                'default_code': line[header.index('default_code')],
                'name': line[header.index('name')],
                'lst_price': float(line[header.index('lst_price')]),
            }))


class Odoo:
    def __init__(self, odoo_key):
        """
            Carga los productos que estan en odoo y los que estan en la plantilla
            mila para luego hacer las comparaciones.
        """
        prod = OdooDb(odoo_key)
        prod.all_odoo()
        self._odoo_prods = prod
        print 'odoo prods', len(prod._pro)

        prod = CsvFile()
        prod.all_csv(MILA_PRECIOS)
        self._mila_prods = prod
        print 'mila prods', len(prod._pro)

    def list_new_products(self):
        """ Lista los productos nuevos, que estan en la lista de precios pero no estan en odoo
        """
        count = mila = 0
        print 'Productos Nuevos'
        for prod in self._mila_prods.all():
            mila += 1
            if not self._odoo_prods.find(prod):
                count += 1
                print prod.formatted()
        print 'total productos ', count
        print 'mila prod', mila

    def list_obsolete_products(self):
        """ Lista los productos, que estan en odoo pero no estan en lista de precios
        """
        count = 0
        print 'Productos obsoletos'
        for prod in self._odoo_prods.all():
            if not self._mila_prods.find(prod):
                count += 1
                print prod.formatted()
        print 'total productos ', count

    def list_odoo_products(self):
        """ Lista los productos que estan en odoo
        """
        count = 0
        print 'Productos de Odooo'
        for prod in self._odoo_prods.all():
            print prod.formatted()
            count += 1
        print 'total productos ', count

    def list_mila_products(self):
        """ Lista los productos que estan en mila
        """
        count = 0
        print 'Productos de lista de precio mila'
        for prod in self._mila_prods.all():
            print prod.formatted()
            count += 1
        print 'total productos ', count

    def process_all(self):
        """ actualiza o agrega los productos en odoo
        """

        # Marcar los productos que son obsoletos
        # traer todos los productos no obsoletos de odoo
        for prod in self._odoo_prods.all():
            if not self._mila_prods.find(prod):
                prod.obj().state = 'obsolete'
                print 'obsoleto', prod.formatted()
            else:
                prod.obj().state = 'sellable'
                print 'sellable', prod.formatted()

        # Actualizar todos los productos o agregar si son nuevos
        print 'actualizar todos'
        for prod in self._mila_prods.all():
            pro = self._odoo_prods.find(prod)
            if pro:
                # esta en odoo, lo actualizo
                print '---update ', pro.formatted()
                pro.obj().name = prod.get_name()
                pro.obj().lst_price = prod.get_list_price()
                pro.obj().cost_method = 'real'
                pro.obj().standard_price = prod.get_standard_price()
                pro.obj().sale_ok = not prod.get_prod_pack()
                pro.obj().categ_id = prod.get_categ()
                pro.obj().state = 'sellable'
            else:
                # no está en odoo, lo agregamos
                print '---add ', prod.formatted()
                id_prod = self._odoo_prods._prods_odoo_obj.create({
                    'default_code': prod.get_code(),
                    'lst_price': prod.get_list_price(),
                    'name': prod.get_name(),
                    'cost_method': 'real',
                    'categ_id': prod.get_categ(),
                    'standard_price': prod.get_standard_price(),
                    'sale_ok': not prod.get_prod_pack(),
                    'state': 'sellable'
                })


odoo = Odoo(odoo_key)
#odoo.list_new_products()
# odoo.list_obsolete_products()
# odoo.list_odoo_products()
# odoo.list_mila_products()
odoo.process_all()
