# Customer Debt Monthly Report

## Overview
This module provides a monthly breakdown of customer debt and installments in Excel (XLSX). It enables financial and sales stakeholders to view and analyze open customer balances and receivables across active companies.

## Features
- **Monthly Debt Breakdown**: Displays open customer invoices grouped by partner or sales employee with monthly due amounts.
- **Brand Analysis**: Extended reporting by product brand.
- **Role-Based Access Control**:
  - **Accounting / Invoicing**: `account.group_account_invoice`
  - **Sales / User (Own Documents Only)**: `sales_team.group_sale_salesman`
  - **Sales / User (All Documents)**: `sales_team.group_sale_salesman_all_leads`
- **Menu Availability**:
  - `Accounting > Reporting > Customer Debt (Monthly)`
  - `Sales > Reporting > Customer Debt (Monthly)`

## Technical Details
- **Odoo Version**: 18.0
- **Model**: `customer.debt.report.wizard`, `customer.debt.brand.report.wizard`
- **Report Action**: `customer_debt_monthly_report.customer_debt_report_xlsx_action`
- **Author**: ENG/Mohamed Ahmed
