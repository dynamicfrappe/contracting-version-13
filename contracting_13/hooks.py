from . import __version__ as app_version

app_name = "contracting_13"
app_title = "Contracting 13"
app_publisher = "dynamic"
app_description = "dynamic"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "beshoy.atef@dynamiceg.com"
app_license = "MIT"


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"contracting_13.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []


override_doctype_class = {
	"Stock Entry": "contracting_13.controllers.custom_stock_entry.customStockEntry" ,
    "Delivery Note": "contracting_13.controllers.custom_delivery_note.CustomDeliveryNote",
	"Sales Invoice": "contracting_13.controllers.custom_sales_invoice.CustomSalesInvoice",
   "Task" : "contracting_13.controllers.custom_task.customTask",
   "Sales Order" : "contracting_13.contracting_13.doctype.sales_order.sales_order.SalesOrder" , 
   "Martrial Request": "contracting_13.contracting_13.overrides.material_request.CustomMaterialRequest"
}




doctype_js = {
	"Purchase Order" : "public/js/purchase_order.js" ,
	"Sales Order" : "public/js/sales_order.js" ,
	"Sales Invoice" : "public/js/sales_invoice.js" ,
	"Payment Entry" : "public/js/payment_entry.js" ,
	"Purchase Invoice" : "public/js/purchase_invoice.js" ,
	"Task" : "contracting_13/doctype/task/task.js" ,
	"Stock Entry" : "public/js/stock_entry.js",
	"Quotation" : "public/js/quotation.js",
	"Material Request" :"public/js/material_request.js",

}

domains = {
	'Contracting':'contracting_13.domains.contracting'
}

override_doctype_dashboards = {
	"Project": "contracting_13.public.dashboard.project_get_dashboard_data.get_data"
}

jenv = {
    "methods": [
        "get_comparison_item_cards:contracting_13.contract_api.get_comparison_item_cards",
    ],
    "filters": []
}

scheduler_events = {

	"daily": [
		"contracting_13.contracting_13.doctype.comparison.comparison.get_returnable_insurance"
	],

}

doc_events = {
		"Stock Entry" : {
			"validate" :"contracting_13.contracting_13.doctype.stock_entry.stock_entry.validate" ,
			"on_submit": "contracting_13.contracting_13.doctype.stock_entry.stock_entry.on_submit"
		} ,
		"Sales Order" : {
			"validate": "contracting_13.contracting_13.doctype.stock_entry.stock_entry.update_project_cost"
		} ,
         "Quotation" : {
			"validate": "contracting_13.controllers.quotation.validate_quotation"
		} ,
		"Purchase Order": {
		"on_submit": "contracting_13.contracting_13.doctype.purchase_order.purchase_order.update_comparison",
		"on_cancel": "contracting_13.contracting_13.doctype.purchase_order.purchase_order.update_comparison",}  ,
}



before_migrate = 'contracting_13.contracting_13.add_client_Sccript.create_item_account_dimension'