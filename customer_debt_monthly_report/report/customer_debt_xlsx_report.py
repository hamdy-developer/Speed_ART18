from odoo import models, fields, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

class CustomerDebtXlsxReport(models.AbstractModel):
    _name = 'report.customer_debt_monthly_report.customer_debt_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        # Initial data from wizard
        date_from = fields.Date.from_string(data.get('date_from'))
        report_by = data.get('report_by', 'partner')
        partner_ids = data.get('partner_ids')
        employee_ids = data.get('employee_ids')
        num_months = data.get('number_of_months', 10)

        # Calculate months
        months = []
        for i in range(num_months):
            m = date_from + relativedelta(months=i)
            months.append(m.strftime('%b-%y'))

        sheet = workbook.add_worksheet('مديونية العملاء')
        
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
        partner_format = workbook.add_format({
            'bold': True, 'border': 1, 'align': 'left', 'bg_color': '#D9E1F2', 'font_size': 12
        })
        subgroup_format = workbook.add_format({
            'bold': True, 'border': 1, 'align': 'left', 'bg_color': '#F2F2F2', 'font_size': 11
        })
        total_format = workbook.add_format({
            'bold': True, 'bg_color': '#F2F2F2', 'border': 1, 'align': 'center'
        })
        title_format = workbook.add_format({
            'bold': True, 'align': 'center', 'font_size': 14, 'valign': 'vcenter'
        })

        # Main Title
        sheet.merge_range(1, 1, 1, 6 + num_months, 'مديونية العملاء', title_format)

        # Headers
        headers = ['Partner', 'Sales Employee', 'NO.Invoice', 'Payment Term', 'Value', 'Amount due']
        col = 1
        for h in headers:
            sheet.write(3, col, h, header_format)
            col += 1
        
        for m in months:
            sheet.write(3, col, m, month_header_format)
            col += 1

        # Data fetching
        domain = [
            ('move_id.move_type', '=', 'out_invoice'),
            ('move_id.state', '=', 'posted'),
            ('account_type', '=', 'asset_receivable'),
            ('reconciled', '=', False),
            ('amount_residual', '!=', 0),
        ]
        if partner_ids:
            domain.append(('partner_id', 'in', partner_ids))
        if employee_ids:
            domain.append(('move_id.sales_employee_id', 'in', employee_ids))
        
        aml_lines = self.env['account.move.line'].search(domain)
        # Sort lines based on report_by to handle nested grouping
        if report_by == 'partner':
            aml_lines = aml_lines.sorted(key=lambda l: (l.partner_id.id, l.move_id.sales_employee_id.id or 0, l.move_id.id, l.date_maturity or fields.Date.today()))
        else:
            aml_lines = aml_lines.sorted(key=lambda l: (l.move_id.sales_employee_id.id or 0, l.partner_id.id, l.move_id.id, l.date_maturity or fields.Date.today()))

        # Group data
        grouped_data = {}
        for line in aml_lines:
            p_id = line.partner_id.id
            p_name = line.partner_id.name
            e_id = line.move_id.sales_employee_id.id or 0
            e_name = line.move_id.sales_employee_id.name or _('No Sales Employee')

            if report_by == 'partner':
                primary_id, primary_name = p_id, p_name
                secondary_id, secondary_name = e_id, e_name
            else:
                primary_id, primary_name = e_id, e_name
                secondary_id, secondary_name = p_id, p_name

            if primary_id not in grouped_data:
                grouped_data[primary_id] = {'name': primary_name, 'subgroups': {}}
            
            if secondary_id not in grouped_data[primary_id]['subgroups']:
                grouped_data[primary_id]['subgroups'][secondary_id] = {'name': secondary_name, 'invoices': {}}
            
            m_id = line.move_id.id
            
            if m_id not in grouped_data[primary_id]['subgroups'][secondary_id]['invoices']:
                inv_name = line.move_id.name
                if line.move_id.invoice_date:
                    inv_name += f" ({line.move_id.invoice_date})"
                
                grouped_data[primary_id]['subgroups'][secondary_id]['invoices'][m_id] = {
                    'name': inv_name,
                    'partner_name': line.partner_id.name,
                    'sales_employee': line.move_id.sales_employee_id.name or '',
                    'payment_term': line.move_id.invoice_payment_term_id.name or '',
                    'value': line.move_id.amount_total,
                    'amount_due': line.move_id.amount_residual,
                    'monthly_dues': {m: 0.0 for m in months}
                }
            
            # Find which month column this line falls into
            if line.date_maturity:
                m_str = line.date_maturity.strftime('%b-%y')
                if m_str in grouped_data[primary_id]['subgroups'][secondary_id]['invoices'][m_id]['monthly_dues']:
                    grouped_data[primary_id]['subgroups'][secondary_id]['invoices'][m_id]['monthly_dues'][m_str] += line.amount_residual

        # Write data
        row = 4
        overall_totals = {m: 0.0 for m in months}
        overall_value = 0.0
        overall_due = 0.0

        for p_id, p_info in grouped_data.items():
            # Write Primary Header Row
            sheet.merge_range(row, 1, row, 6 + num_months, p_info['name'], partner_format)
            row += 1

            for s_id, s_info in p_info['subgroups'].items():
                # Write Secondary Header Row (Sub-group)
                sheet.merge_range(row, 1, row, 6 + num_months, '    ' + s_info['name'], subgroup_format)
                row += 1

                for m_id, inv in s_info['invoices'].items():
                    sheet.write(row, 1, inv['partner_name'], cell_format)
                    sheet.write(row, 2, inv['sales_employee'], cell_format)
                    sheet.write(row, 3, inv['name'], cell_format)
                    sheet.write(row, 4, inv['payment_term'], cell_format)
                    sheet.write(row, 5, inv['value'], cell_format)
                    sheet.write(row, 6, inv['amount_due'], cell_format)
                    
                    col = 7
                    for m in months:
                        val = inv['monthly_dues'][m]
                        sheet.write(row, col, val if val != 0 else '-', cell_format)
                        overall_totals[m] += val
                        col += 1
                    
                    overall_value += inv['value']
                    overall_due += inv['amount_due']
                    row += 1
            
        # Grand Total Row
        row += 1
        label = _('Total Partner') if report_by == 'partner' else _('Total Sales Employee')
        sheet.write(row, 1, label, total_format)
        sheet.write(row, 2, '', total_format)
        sheet.write(row, 3, '', total_format)
        sheet.write(row, 4, '', total_format)
        sheet.write(row, 5, overall_value, total_format)
        sheet.write(row, 6, overall_due, total_format)
        col = 7
        for m in months:
            sheet.write(row, col, overall_totals[m], total_format)
            col += 1

        # Set column widths
        sheet.set_column(1, 1, 30) # Partner
        sheet.set_column(2, 2, 20) # Sales Employee
        sheet.set_column(3, 3, 35) # Invoice + Date
        sheet.set_column(4, 4, 20) # Payment Term
        sheet.set_column(5, 6, 15) # Value/Due
        sheet.set_column(7, 7 + num_months, 12) # Months
