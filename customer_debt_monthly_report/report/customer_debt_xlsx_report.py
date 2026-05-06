from odoo import models, fields, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

class CustomerDebtXlsxReport(models.AbstractModel):
    _name = 'report.customer_debt_monthly_report.customer_debt_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        # Initial data from wizard
        date_from = fields.Date.from_string(data.get('date_from'))
        partner_ids = data.get('partner_ids')
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
        total_format = workbook.add_format({
            'bold': True, 'bg_color': '#F2F2F2', 'border': 1, 'align': 'center'
        })
        title_format = workbook.add_format({
            'bold': True, 'align': 'center', 'font_size': 14, 'valign': 'vcenter'
        })

        # Main Title
        sheet.merge_range(1, 1, 1, 5 + num_months, 'مديونية العملاء', title_format)

        # Headers
        headers = ['Partner', 'Sales Employee', 'NO.Invoice', 'Value', 'Amount due']
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
        
        aml_lines = self.env['account.move.line'].search(domain, order='partner_id, move_id, date_maturity')

        # Group data
        partners_data = {}
        for line in aml_lines:
            p_id = line.partner_id.id
            m_id = line.move_id.id
            
            if p_id not in partners_data:
                partners_data[p_id] = {'name': line.partner_id.name, 'invoices': {}}
            
            if m_id not in partners_data[p_id]['invoices']:
                partners_data[p_id]['invoices'][m_id] = {
                    'name': line.move_id.name,
                    'sales_employee': line.move_id.sales_employee_id.name or '',
                    'value': line.move_id.amount_total,
                    'amount_due': line.move_id.amount_residual,
                    'monthly_dues': {m: 0.0 for m in months}
                }
            
            # Find which month column this line falls into
            if line.date_maturity:
                m_str = line.date_maturity.strftime('%b-%y')
                if m_str in partners_data[p_id]['invoices'][m_id]['monthly_dues']:
                    partners_data[p_id]['invoices'][m_id]['monthly_dues'][m_str] += line.amount_residual
                else:
                    # If date is outside range or before start month, maybe add to first month or a 'prior' column?
                    # For now, let's just focus on the months requested.
                    pass

        # Write data
        row = 4
        overall_totals = {m: 0.0 for m in months}
        overall_value = 0.0
        overall_due = 0.0

        for p_id, p_info in partners_data.items():
            # Write Partner Header Row
            sheet.merge_range(row, 1, row, 5 + num_months, p_info['name'], partner_format)
            row += 1

            for m_id, inv in p_info['invoices'].items():
                sheet.write(row, 1, '', cell_format) # Empty partner cell in invoice rows
                sheet.write(row, 2, inv['sales_employee'], cell_format)
                sheet.write(row, 3, inv['name'], cell_format)
                sheet.write(row, 4, inv['value'], cell_format)
                sheet.write(row, 5, inv['amount_due'], cell_format)
                
                col = 6
                for m in months:
                    val = inv['monthly_dues'][m]
                    sheet.write(row, col, val if val != 0 else '-', cell_format)
                    overall_totals[m] += val
                    col += 1
                
                overall_value += inv['value']
                overall_due += inv['amount_due']
                row += 1
            
        # Grand Total Row (Total Partner)
        row += 1
        sheet.write(row, 1, 'Total Partner', total_format)
        sheet.write(row, 2, '', total_format)
        sheet.write(row, 3, '', total_format)
        sheet.write(row, 4, overall_value, total_format)
        sheet.write(row, 5, overall_due, total_format)
        col = 6
        for m in months:
            sheet.write(row, col, overall_totals[m], total_format)
            col += 1

        # Set column widths
        sheet.set_column(1, 1, 30) # Partner
        sheet.set_column(2, 2, 20) # Sales Employee
        sheet.set_column(3, 3, 20) # Invoice
        sheet.set_column(4, 5, 15) # Value/Due
        sheet.set_column(6, 6 + num_months, 12) # Months
