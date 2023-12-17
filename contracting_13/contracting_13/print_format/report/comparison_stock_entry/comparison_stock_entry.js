// Copyright (c) 2023, Dynamic Technology and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Comparison Stock Entry"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.get_today(),1),
			// reqd: 1
		},
		{
			fieldname: "comparison",
			label: __("Comparison"),
			fieldtype: "Link",
			options: "Comparison",
			// reqd: 1
		},
		{
			fieldname: "from_warehouse",
			label: __("From Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
		},
		{
			fieldname: "to_warehouse",
			label: __("To Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
		},
		// {
		// 	fieldname: "customer",
		// 	label: __("Customer"),
		// 	fieldtype: "Link",
		// 	options: "Customer",
		// },
		{
			fieldname: "stock_entry_type",
			label: __("Stock Entry Type"),
			fieldtype: "Link",
			options: "Stock Entry Type",
		},

	]
};
