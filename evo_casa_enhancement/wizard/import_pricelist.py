from odoo import fields, models, _
from odoo.exceptions import Warning
from datetime import datetime
import os
import base64
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat

try:
    import xlrd

    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

FILE_TYPE_DICT = {
    'application/vnd.ms-excel': ('xls', xlrd, 'xlrd'),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ('xlsx', xlsx, 'xlrd >= 0.8'),
}

EXTENSIONS = {
    '.' + ext: handler
    for mime, (ext, handler, req) in FILE_TYPE_DICT.items()
}


class UpdateProductPriceList(models.TransientModel):
    _name = 'update.product.pricelist'
    _description = 'Update Product Pricelist'

    pricelist_id = fields.Many2one('product.pricelist', string='Price List')
    import_file_data = fields.Binary("File to Import")
    file_name = fields.Char("Filename")

    def update_product_pricelist(self):
        if not self.import_file_data:
            raise Warning("Please select file.")
        p, ext = os.path.splitext(self.file_name)
        if ext[1:] not in ['xls', 'xlsx']:
            raise Warning(_("Unsupported file format \"{}\", import only supports XLS, XLSX").format(self.file_name))

        options = {u'datetime_format': u'', u'date_format': u'', u'keep_matches': False, u'encoding': u'utf-8',
                   u'fields': [], u'quoting': u'"', u'headers': True, u'separator': u',',
                   u'float_thousand_separator': u',', u'float_decimal_separator': u'.', u'advanced': False}
        import_file = base64.b64decode(self.import_file_data)
        mimetype = guess_mimetype(import_file)
        (file_extension, handler, req) = FILE_TYPE_DICT.get(mimetype, (None, None, None))

        result = []
        if handler:
            result = getattr(self, '_read_' + file_extension)(options, import_file)

        if not result and self.file_name:
            p, ext = os.path.splitext(self.file_name)
            if ext in EXTENSIONS:
                result = getattr(self, '_read_' + ext[1:])(options, import_file)
        if not result and req:
            raise Warning(_("Unable to load \"{extension}\" file: requires Python module \"{modname}\"").format(
                extension=file_extension, modname=req))

        ''' We have count first row as header row.First column will be internal reference and other will be price.'''
        pricelist_update_log = self.env['pricelist.process.log']
        pricelist_update_log_details = self.env['pricelist.process.detail.log']
        pricelist_item = self.env['product.pricelist.item']
        total_successfully_processed_row = 0
        total_unprocessed_row = 0
        count = 0
        pricelist_id = self.pricelist_id
        if result:
            process_log_id = pricelist_update_log.sudo().create({'pricelist_id': pricelist_id.id})
            for row in result:
                if count == 0:
                    count += 1
                    continue
                try:
                    default_code = row[0]
                    price = float(row[1] or 0.0)
                    product_tmpl_id = self.env['product.template'].search([('default_code', '=', default_code)],
                                                                          limit=1)
                    if not product_tmpl_id:
                        pricelist_update_log_details.sudo().create({
                            'process_log_id': process_log_id.id,
                            'file_row_number': count,
                            'file_product_default_code': row[0],
                            'file_process_error': _('No product found with SLC Code : %s' % (default_code))
                        })
                        total_unprocessed_row += 1
                        continue
                    # Searching for pricelist item.
                    pricelist_item_id = pricelist_item.search(
                        [('pricelist_id', '=', pricelist_id.id), ('product_tmpl_id', '=', product_tmpl_id.id)], limit=1)
                    if pricelist_item_id:
                        pricelist_item_id.write({'fixed_price': price})
                    else:
                        pricelist_item.create({'product_tmpl_id': product_tmpl_id.id,
                                               'pricelist_id': self.pricelist_id.id,
                                               'fixed_price': price,
                                               'applied_on': '1_product',
                                               'compute_price': 'fixed',
                                               'min_quantity': 1,
                                               })
                    total_successfully_processed_row += 1
                except Exception as e:
                    pricelist_update_log_details.sudo().create({
                        'process_log_id': process_log_id.id,
                        'file_row_number': count,
                        'file_product_default_code': default_code,
                        'file_process_error': _(str(e))
                    })
                    total_unprocessed_row += 1
                finally:
                    count += 1
            if process_log_id:
                process_log_id.write({
                    'total_processed_record': total_successfully_processed_row,
                    'total_unprocessed_record': total_unprocessed_row,
                    'total_records': count - 1,  # First row is header row.
                })
        return

    def _read_xls(self, options, import_file):
        """ Read file content, using xlrd lib """
        book = xlrd.open_workbook(file_contents=import_file or b'')
        return self._read_xls_book(book)

    def _read_xls_book(self, book):
        sheet = book.sheet_by_index(0)
        # emulate Sheet.get_rows for pre-0.9.4
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            values = []
            for colx, cell in enumerate(row, 1):
                if cell.ctype is xlrd.XL_CELL_NUMBER:
                    is_float = cell.value % 1 != 0.0
                    values.append(
                        str(cell.value)
                        if is_float
                        else str(int(cell.value))
                    )
                elif cell.ctype is xlrd.XL_CELL_DATE:
                    is_datetime = cell.value % 1 != 0.0
                    # emulate xldate_as_datetime for pre-0.9.3
                    dt = datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                    values.append(
                        dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        if is_datetime
                        else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    )
                elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                    values.append(u'True' if cell.value else u'False')
                elif cell.ctype is xlrd.XL_CELL_ERROR:
                    raise ValueError(
                        _("Invalid cell value at row %(row)s, column %(col)s: %(cell_value)s") % {
                            'row': rowx,
                            'col': colx,
                            'cell_value': xlrd.error_text_from_code.get(cell.value,
                                                                        _("unknown error code %s") % cell.value)
                        }
                    )
                else:
                    values.append(cell.value)
            if any(x for x in values if x.strip()):
                yield values

    # use the same method for xlsx and xls files
    _read_xlsx = _read_xls
