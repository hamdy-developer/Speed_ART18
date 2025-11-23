# -*- coding: utf-8 -*-

import base64
import io
from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    import xlwt
except ImportError:
    xlwt = None


class ProductPackagingReportWizard(models.TransientModel):
    _name = 'product.packaging.report.wizard'
    _description = 'Product Packaging Report Wizard'

    product_ids = fields.Many2many(
        'product.product',
        string='Products',
        help="Select specific products. If empty, the report will run for all storable products."
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    def _get_report_data(self):
        """
        New logic: Iterate through products first.
        For each product, show its on-hand quantity.
        If it has packagings, create a new line for each one.
        If it has no packaging, create a single line with empty packaging info.
        """
        domain = [
            # ('type', '=', 'product'),  # تم إعادة الفلتر لضمان جلب المنتجات القابلة للتخزين فقط
            ('company_id', 'in', [self.company_id.id, False]),
        ]
        if self.product_ids:
            products = self.product_ids
        else:
            products = self.env['product.product'].sudo().search(domain)

        report_lines = []
        for product in products:
            if product.packaging_ids:
                for packaging in product.packaging_ids:
                    contained_qty = packaging.qty or 1.0
                    num_packages = product.qty_available / contained_qty if contained_qty else 0
                    report_lines.append({
                        'product_name': product.display_name,
                        'on_hand_qty': product.qty_available,
                        'package_name': packaging.name,
                        'package_type_name': packaging.package_type_id.name or '',
                        'contained_qty': packaging.qty,
                        'num_packages': num_packages,
                    })
            else:
                report_lines.append({
                    'product_name': product.display_name,
                    'on_hand_qty': product.qty_available,
                    'package_name': '',
                    'package_type_name': '',
                    'contained_qty': 0,
                    'num_packages': 0,
                })
        return report_lines

    def action_print_xlsx_report(self):
        """
        Generates and returns a formatted XLSX report.
        """
        if not xlwt:
            raise UserError(_("The 'xlwt' library is required to generate XLSX reports. Please install it."))

        report_lines = self._get_report_data()
        workbook = xlwt.Workbook(encoding='utf-8')
        sheet = workbook.add_sheet('Packaging Report')

        # --- تعريف التنسيقات ---

        # تنسيق الهيدر (خلفية رمادية، خط أبيض عريض، حدود، محاذاة بالمنتصف)
        header_style = xlwt.easyxf(
            'font: bold on, color white; '
            'align: horiz center, vert center; '
            'pattern: pattern solid, fore_colour gray25; '
            'borders: left thin, right thin, top thin, bottom thin;'
        )

        # تنسيق خلايا النصوص (محاذاة لليسار، حدود)
        text_style = xlwt.easyxf(
            'align: horiz left, vert center; '
            'borders: left thin, right thin, top thin, bottom thin;'
        )

        # تنسيق خلايا الأرقام (محاذاة لليمين، حدود)
        number_style = xlwt.easyxf(
            'align: horiz right, vert center; '
            'borders: left thin, right thin, top thin, bottom thin;'
        )

        # --- بناء التقرير ---

        # تحديد عرض الأعمدة
        sheet.col(0).width = 256 * 45
        sheet.col(1).width = 256 * 20
        sheet.col(2).width = 256 * 25
        sheet.col(3).width = 256 * 20
        sheet.col(4).width = 256 * 20
        sheet.col(5).width = 256 * 25

        # كتابة الهيدر بالتنسيق الجديد
        headers = [
            'Product', 'Quantity On Hand', 'Package Name', 'Package Type',
            'Contained Qty', 'Number of Full Packages'
        ]
        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header, header_style)

        # تجميد صف الهيدر
        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(1)

        # كتابة البيانات بالتنسيقات المخصصة
        row_num = 1
        for line in report_lines:
            sheet.write(row_num, 0, line['product_name'], text_style)
            sheet.write(row_num, 1, line['on_hand_qty'], number_style)
            sheet.write(row_num, 2, line['package_name'], text_style)
            sheet.write(row_num, 3, line['package_type_name'], text_style)
            sheet.write(row_num, 4, line['contained_qty'], number_style)
            sheet.write(row_num, 5, line['num_packages'], number_style)
            row_num += 1

        # --- حفظ وإرجاع الملف ---
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_data = base64.b64encode(fp.read())
        fp.close()

        file_name = f'Packaging_Report_{fields.Date.today()}.xls'
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': file_data,
            'type': 'binary',
            'mimetype': 'application/vnd.ms-excel'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }