from odoo import models, fields, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

class CustomerDebtBrandXlsxReport(models.AbstractModel):
    _name = 'report.customer_debt_monthly_report.brand_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        date_from = fields.Date.from_string(data.get('date_from'))
        report_by = data.get('report_by', 'employee')
        employee_ids = data.get('employee_ids')
        brand_ids = data.get('brand_ids')
        num_months = data.get('number_of_months', 10)

        months = []
        for i in range(num_months):
            m = date_from + relativedelta(months=i)
            months.append(m.strftime('%b-%y'))

        sheet = workbook.add_worksheet('متحصلات عملاء')
        
        # Formats
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#D3D3D3', 'border': 1, 'font_size': 11
        })
        month_header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#FF0000', 'font_color': '#FFFFFF', 'border': 1, 'font_size': 11
        })
        cell_format = workbook.add_format({'border': 1, 'align': 'center'})
        primary_format = workbook.add_format({
            'bold': True, 'border': 1, 'align': 'left', 'bg_color': '#D9E1F2', 'font_size': 12
        })
        subgroup_format = workbook.add_format({
            'bold': True, 'border': 1, 'align': 'left', 'bg_color': '#E2EFDA', 'font_size': 11
        })
        total_format = workbook.add_format({
            'bold': True, 'bg_color': '#B4C6E7', 'border': 1, 'align': 'center'
        })
        brand_total_format = workbook.add_format({
            'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'center'
        })
        title_format = workbook.add_format({
            'bold': True, 'align': 'center', 'font_size': 14, 'valign': 'vcenter'
        })

        sheet.merge_range(1, 1, 1, 6 + num_months, 'متحصلات العملاء بدلالة (المندوب/البراند)', title_format)

        headers = ['Partner', 'Sales Employee', 'NO.Invoice', 'Payment Term', 'Brand', 'Value', 'Amount paied']

        col = 1
        for h in headers:
            sheet.write(3, col, h, header_format)
            col += 1
        
        for m in months:
            sheet.write(3, col, m, month_header_format)
            col += 1

        domain = [
            ('move_id.move_type', '=', 'out_invoice'),
            ('move_id.state', '=', 'posted'),
            ('account_type', '=', 'asset_receivable'),
            ('reconciled', '=', False),
            ('amount_residual', '!=', 0),
        ]
        if employee_ids:
            domain.append(('move_id.sales_employee_id', 'in', employee_ids))
        
        aml_lines = self.env['account.move.line'].search(domain)

        augmented_lines = []
        for line in aml_lines:
            brand = False
            first_line = line.move_id.invoice_line_ids.filtered(lambda l: l.display_type == 'product')
            if first_line:
                brand = first_line[0].product_id.product_brand_id
            
            b_id = brand.id if brand else 0
            b_name = brand.name if brand else _('No Brand')

            if brand_ids and b_id not in brand_ids:
                continue

            e_id = line.move_id.sales_employee_id.id or 0
            e_name = line.move_id.sales_employee_id.name or _('No Sales Employee')
            
            p_id = line.partner_id.id or 0
            p_name = line.partner_id.name or _('No Partner')

            augmented_lines.append({
                'line': line,
                'b_id': b_id,
                'b_name': b_name,
                'e_id': e_id,
                'e_name': e_name,
                'p_id': p_id,
                'p_name': p_name
            })

        if report_by == 'brand':
            augmented_lines.sort(key=lambda x: (x['b_id'], x['p_id'], x['line'].move_id.id, x['line'].date_maturity or fields.Date.today()))
        else:
            augmented_lines.sort(key=lambda x: (x['e_id'], x['p_id'], x['line'].move_id.id, x['line'].date_maturity or fields.Date.today()))

        grouped_data = {}
        for item in augmented_lines:
            line = item['line']
            b_id = item['b_id']
            b_name = item['b_name']
            e_id = item['e_id']
            e_name = item['e_name']
            p_id = item['p_id']
            p_name = item['p_name']

            if report_by == 'brand':
                primary_id, primary_name = b_id, b_name
                secondary_id, secondary_name = p_id, p_name
            else:
                primary_id, primary_name = e_id, e_name
                secondary_id, secondary_name = p_id, p_name

            if primary_id not in grouped_data:
                grouped_data[primary_id] = {'name': primary_name, 'subgroups': {}, 'brand_totals': {}}
            
            if secondary_id not in grouped_data[primary_id]['subgroups']:
                grouped_data[primary_id]['subgroups'][secondary_id] = {'name': secondary_name, 'invoices': {}}
            
            if b_name not in grouped_data[primary_id]['brand_totals']:
                grouped_data[primary_id]['brand_totals'][b_name] = {
                    'value': 0.0,
                    'amount_due': 0.0,
                    'monthly_dues': {m: 0.0 for m in months}
                }
            
            m_id = line.move_id.id
            
            if m_id not in grouped_data[primary_id]['subgroups'][secondary_id]['invoices']:
                inv_name = line.move_id.name
                if line.move_id.invoice_date:
                    inv_name += f" ({line.move_id.invoice_date})"
                
                grouped_data[primary_id]['subgroups'][secondary_id]['invoices'][m_id] = {
                    'name': inv_name,
                    'partner_name': p_name,
                    'brand_name': b_name,
                    'sales_employee': e_name,
                    'payment_term': line.move_id.invoice_payment_term_id.name or '',
                    'value': line.move_id.amount_total,
                    'amount_due': line.move_id.amount_residual,
                    'monthly_dues': {m: 0.0 for m in months}
                }
                
                # Add to brand totals for this primary group
                grouped_data[primary_id]['brand_totals'][b_name]['value'] += line.move_id.amount_total
                grouped_data[primary_id]['brand_totals'][b_name]['amount_due'] += line.move_id.amount_residual
            
            if line.date_maturity:
                m_str = line.date_maturity.strftime('%b-%y')
                if m_str in grouped_data[primary_id]['subgroups'][secondary_id]['invoices'][m_id]['monthly_dues']:
                    grouped_data[primary_id]['subgroups'][secondary_id]['invoices'][m_id]['monthly_dues'][m_str] += line.amount_residual
                    grouped_data[primary_id]['brand_totals'][b_name]['monthly_dues'][m_str] += line.amount_residual

        row = 4
        overall_totals = {m: 0.0 for m in months}
        overall_value = 0.0
        overall_due = 0.0

        for p_id, p_info in grouped_data.items():
            sheet.merge_range(row, 1, row, 7 + num_months, p_info['name'], primary_format)
            row += 1
            
            primary_value = 0.0
            primary_due = 0.0
            primary_monthly = {m: 0.0 for m in months}

            for s_id, s_info in p_info['subgroups'].items():
                sheet.merge_range(row, 1, row, 7 + num_months, '    ' + s_info['name'], subgroup_format)
                row += 1

                for m_id, inv in s_info['invoices'].items():
                    sheet.write(row, 1, inv['partner_name'], cell_format)
                    sheet.write(row, 2, inv['sales_employee'], cell_format)
                    sheet.write(row, 3, inv['name'], cell_format)
                    sheet.write(row, 4, inv['payment_term'], cell_format)
                    sheet.write(row, 5, inv['brand_name'], cell_format)
                    sheet.write(row, 6, inv['value'], cell_format)
                    sheet.write(row, 7, inv['amount_due'], cell_format)
                    
                    primary_value += inv['value']
                    primary_due += inv['amount_due']
                    overall_value += inv['value']
                    overall_due += inv['amount_due']
                    
                    col = 8
                    for m in months:
                        val = inv['monthly_dues'][m]
                        sheet.write(row, col, val if val != 0 else '-', cell_format)
                        primary_monthly[m] += val
                        overall_totals[m] += val
                        col += 1
                    
                    row += 1
                    
            # Print Primary Totals
            label = f"Total Collected {'Employee' if report_by == 'employee' else 'Brand'} {p_info['name']}"
            sheet.merge_range(row, 1, row, 5, label, total_format)
            sheet.write(row, 6, primary_value, total_format)
            sheet.write(row, 7, primary_due, total_format)
            col = 8
            for m in months:
                sheet.write(row, col, primary_monthly[m], total_format)
                col += 1
            row += 1
            
            # Print Brand Totals for this Primary Group
            for b_name, b_totals in p_info['brand_totals'].items():
                b_label = f"Total Collected EMP - {b_name} - {p_info['name']}" if report_by == 'employee' else f"Total Collected - {p_info['name']} - {b_name}"
                sheet.merge_range(row, 1, row, 5, b_label, brand_total_format)
                sheet.write(row, 6, b_totals['value'], brand_total_format)
                sheet.write(row, 7, b_totals['amount_due'], brand_total_format)
                col = 8
                for m in months:
                    sheet.write(row, col, b_totals['monthly_dues'][m], brand_total_format)
                    col += 1
                row += 1
            
        row += 1
        sheet.merge_range(row, 1, row, 5, _('Grand Total'), total_format)
        sheet.write(row, 6, overall_value, total_format)
        sheet.write(row, 7, overall_due, total_format)
        col = 8
        for m in months:
            sheet.write(row, col, overall_totals[m], total_format)
            col += 1

        sheet.set_column(1, 1, 30) # Partner
        sheet.set_column(2, 2, 20) # Sales Employee
        sheet.set_column(3, 3, 35) # Invoice + Date
        sheet.set_column(4, 4, 20) # Payment Term
        sheet.set_column(5, 5, 20) # Brand
        sheet.set_column(6, 7, 15) # Value/Due
        sheet.set_column(8, 8 + num_months, 12) # Months
