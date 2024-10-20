from __future__ import unicode_literals
from frappe import _


data = {
    'custom_fields':
    {
        'Journal Entry':[
            {
                "label":_("Notebook No"),
                "fieldname":"notebook_no",
                "fieldtype":"Data",
                "insert_after":"multi_currency", 
            },
        ],
        "Material Request":[
            {
                "fieldname": "comparison",
                "fieldtype": "Link",
                "insert_after": "status",
                "options": "Comparison",
                # "depends_on": "eval:doc.against_comparison == 1",
                # "mandatory_depends_on": "eval:doc.against_comparison == 1",
                "label": "Comparison",

            },
            {
                "fieldname": "project_name",
                "fieldtype": "Data",
                "insert_after": "project",
                # "depends_on": "eval:doc.against_comparison == 1",
                # "mandatory_depends_on": "eval:doc.against_comparison == 1",
                "label": "Project Name",
                "fetch_from":"project.project_name"
            },
            {
                "fieldname": "comparison_item",
                "fieldtype": "Link",
                "insert_after": "comparison",
                "options": "Item",
                "label": "Comparison Item",

            },
            {
                "label": _("All Comparsion"),
                "fieldname": "all_comparsion",
                "fieldtype": "Check",
                "insert_after": "comparison_item",

            }
        ],
        "Material Request Item":[
            {
                "fieldname": "attach_image",
                "fieldtype": "Image",
                "insert_after": "description",
                "label": "Attach Image",
            },
        ],
        'Quotation':[
            {
                "label":_("Project"),
                "fieldname":"project",
                "fieldtype":"Link",
                "options":"Project",
                "insert_after":"items_section", 
                "no_copy":1, 
            },
         
            {
                "label":_("Comparison"),
                "fieldname":"comparison",
                "fieldtype":"Link",
                "options":"Comparison",
                "insert_after":"project", 
                "no_copy":1, 
            },
      
            {
                "label":_("Quotation For"),
                "fieldname":"quotation_for",
                "fieldtype":"Text Editor",
                "insert_after":"comparison",  
            },
            {
                "label":_("Card Items"),
                "fieldname":"card_items",
                "fieldtype":"Table",
                "options":"Comparison Item Card Stock Item",
                "insert_after":"card_items_sect", 
                "no_copy":1, 
            },
            {
                "label":_("Card Services"),
                "fieldname":"card_services",
                "fieldtype":"Table",
                "options":"Comparison Item Card Service Item",
                "insert_after":"card_items", 
                "no_copy":1, 
            },
            
        ],
        'Quotation Item':[
            {
                "label": "Build",
                "fieldname": "build",
                "fieldtype": "Data",
                "insert_after": "ordered_qty",
            }, 
              {
                "label": "Rate Demo",
                "fieldname": "rate_demo",
                "fieldtype": "Float",
                "insert_after": "rate",
                "in_list_view": "1",
                "bold": "1",
            }, 

        ],
        'Comparison Item':[
            {
                "label": "Build",
                "fieldname": "build",
                "fieldtype": "Data",
                "insert_after": "remaining_purchased_qty",
            }
        ],
        'Company': [
            {
                "fieldname": "contracting",
                "fieldtype": "Section Break",
                "insert_after": "date_of_establishment",
                "label": "Contracting Settings",

            },
            {
                "fieldname": "account_advance_copy_receivable",
                "fieldtype": "Link",
                "insert_after": "contracting",
                "label": "Account Advance Copy Receivable",
                "options": "Account"

            },
            {
                "fieldname": "advance_version_account_payable",
                "fieldtype": "Link",
                "insert_after": "account_advance_copy_receivable",
                "label": "Advance Version Account Payable",
                "options": "Account"

            },
            {
                "fieldname": "advance_version_account_payable_break",
                "fieldtype": "Column Break",
                "insert_after": "advance_version_account_payable",

            },
            {
                "fieldname": "third_party_insurance_account",
                "fieldtype": "Link",
                "insert_after": "advance_version_account_payable_break",
                "label": "Third party insurance account",
                "options": "Account"

            },
            {
                "fieldname": "insurance_account_for_others_from_us",
                "fieldtype": "Link",
                "insert_after": "third_party_insurance_account",
                "label": "Insurance Account for others from us",
                "options": "Account"

            },

            {
                "fieldname": "terms_sheet_account",
                "fieldtype": "Link",
                "insert_after": "insurance_account_for_others_from_us",
                "label": "Terms Sheet Account",
                "options": "Account"

            },


        ],
        'Purchase Order': [
            {
                "fieldname": "is_contracting",
                "fieldtype": "Check",
                "insert_after": "schedule_date",
                "label": "Has Clearence",

            },

            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "contracting",
                "fieldtype": "Section Break",
                "insert_after": "ignore_pricing_rule",
                "label": "Clearance",

            },
            {
                "fieldname": "down_payment_insurance_rate",
                "fieldtype": "Percent",
                "insert_after": "contracting",
                "label": "Down payment insurance rate (%)",

            },
            {
                "fieldname": "advance_version_account_payable_break",
                "fieldtype": "Column Break",
                "insert_after": "down_payment_insurance_rate",

            },
            {
                "fieldname": "payment_of_insurance_copy",
                "fieldtype": "Percent",
                "insert_after": "advance_version_account_payable_break",
                "label": "Payment of insurance copy of operation and initial delivery(%)",

            },
            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "comparison",
                "fieldtype": "Link",
                "insert_after": "payment_of_insurance_copy",
                "label": "Comparison",
                "options": "Comparison",


            },

        ],


        'Purchase Order Item': [

            {
                "fieldname": "comparison_details",
                "fieldtype": "Section Break",
                "insert_after": "cost_center",
                "label": "Comparison Details",
                "collapsible": 1,

            },
            {
                "fieldname": "comparison",
                "fieldtype": "Link",
                "insert_after": "comparison_details",
                "label": "Comparison",
                "options": "Comparison",
                "read_only": 1

            },
            {
                "fieldname": "comparison_column",
                "fieldtype": "Column Break",
                "insert_after": "comparison",

            },
            {
                "fieldname": "comparison_item",
                "fieldtype": "Link",
                "insert_after": "comparison_column",
                "label": "Comparison Item",
                "options": "Comparison Item",
                "read_only": 1

            },
            # Completed Qty
            {
                "fieldname": "completed",
                "fieldtype": "Section Break",
                "insert_after": "comparison_item",
                "label": "Completed",
                "collapsible": 1,

            },
            {
                "fieldname": "completed_qty",
                "fieldtype": "Float",
                "insert_after": "completed",
                "label": "Completed Qty",
                "read_only": 1,
                "default": 0,
                "allow_on_submit": 1

            },
            {
                "fieldname": "completed_percent",
                "fieldtype": "Percent",
                "insert_after": "completed_qty",
                "label": "Completed Percent",
                "read_only": 1,
                "default": 0,
                "allow_on_submit": 1

            },
            {
                "fieldname": "completed_column",
                "fieldtype": "Column Break",
                "insert_after": "completed_percent",

            },
            {
                "fieldname": "completed_amount",
                "fieldtype": "Currency",
                "insert_after": "completed_column",
                "label": "Completed Amount",
                "read_only": 1,
                "default": 0,
                "allow_on_submit": 1

            },


            # Completed Qty
            {
                "fieldname": "remaining_section",
                "fieldtype": "Section Break",
                "insert_after": "completed_amount",
                "label": "Remaining",
                "collapsible": 1,

            },
            {
                "fieldname": "remaining_qty",
                "fieldtype": "Float",
                "insert_after": "remaining_section",
                "label": "Remaining Qty",
                "read_only": 1,
                "default": 0,
                "allow_on_submit": 1

            },
            {
                "fieldname": "remaining_percent",
                "fieldtype": "Percent",
                "insert_after": "remaining_qty",
                "label": "Remaining Percent",
                "read_only": 1,
                "default": 0,
                "allow_on_submit": 1

            },
            {
                "fieldname": "remaining_column",
                "fieldtype": "Column Break",
                "insert_after": "remaining_percent",

            },
            {
                "fieldname": "remaining_amount",
                "fieldtype": "Currency",
                "insert_after": "remaining_column",
                "label": "Remaining Amount",
                "read_only": 1,
                "default": 0,
                "allow_on_submit": 1

            },

        ],

        'Purchase Invoice': [


            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "contracting",
                "fieldtype": "Section Break",
                "insert_after": "ignore_pricing_rule",
                "label": "Clearance",

            },

            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "comparison",
                "fieldtype": "Link",
                "insert_after": "contracting",
                "label": "Comparison",
                "options": "Comparison",
                "read_only": 1


            },
            {
                "fieldname": "is_contracting",
                "fieldtype": "Check",
                "insert_after": "comparison",
                "label": "Has Clearence",
                "read_only": 1

            },
            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "comparison_column_break",
                "fieldtype": "Column Break",
                "insert_after": "comparison",
            },

            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "clearance",
                "fieldtype": "Link",
                "insert_after": "comparison_column_break",
                "label": "Clearance",
                "options": "Clearance",
                "read_only": 1
            },

        ],

        'Sales Invoice': [


            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "contracting",
                "fieldtype": "Section Break",
                "insert_after": "ignore_pricing_rule",
                "label": "Clearance",

            },

            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "comparison",
                "fieldtype": "Link",
                "insert_after": "contracting",
                "label": "Comparison",
                "options": "Comparison",
                "read_only": 1


            },
            {
                "fieldname": "is_contracting",
                "fieldtype": "Check",
                "insert_after": "comparison",
                "label": "Has Clearence",
                "read_only": 1

            },
            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "comparison_column_break",
                "fieldtype": "Column Break",
                "insert_after": "comparison",
            },

            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "clearance",
                "fieldtype": "Link",
                "insert_after": "comparison_column_break",
                "label": "Clearance",
                "options": "Clearance",
                "read_only": 1
            },

        ],



        'Sales Order': [
            {
                "fieldname": "is_contracting",
                "fieldtype": "Check",
                "insert_after": "delivery_date",
                "label": "Has Clearence",

            },
            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "comparison",
                "fieldtype": "Link",
                "insert_after": "is_contracting",
                "label": "Comparison",
                "options": "Comparison"

            },

            {
                "depends_on": "eval:doc.is_contracting==\"1\"",
                "fieldname": "contracting",
                "fieldtype": "Section Break",
                "insert_after": "ignore_pricing_rule",
                "label": "Clearance",

            },
            {
                "fieldname": "down_payment_insurance_rate",
                "fieldtype": "Percent",
                "insert_after": "contracting",
                "label": "Down payment insurance rate (%)",

            },
            {
                "fieldname": "advance_version_account_payable_break",
                "fieldtype": "Column Break",
                "insert_after": "down_payment_insurance_rate",

            },
            {
                "fieldname": "payment_of_insurance_copy",
                "fieldtype": "Percent",
                "insert_after": "advance_version_account_payable_break",
                "label": "Payment of insurance copy of operation and initial delivery(%)",

            },
            {
                "fieldname": "estimated_cost",
                "fieldtype": "Float",
                "insert_after": "payment_of_insurance_copy",
                "label": "Estimated Cost"
            }


        ],

        "Task":[

            {
                "fieldname": "comparison_section",
                "fieldtype": "Section Break",
                "insert_after": "company",
                "label": "Comparison"

            },
            {
                "fieldname": "sales_order",
                "fieldtype": "Link",
                "insert_after": "comparison_section",
                "label": "Sales Order",
                "options": "Sales Order"
            },
            {
                "fieldname": "comparison",
                "fieldtype": "Link",
                "insert_after": "sales_order",
                "label": "Comparison",
                "options": "Comparison",
                "fetch_if_empty":1,
                "fetch_from":"sales_order.comparison"
            },
            {
                "fieldname": "tender",
                "fieldtype": "Link",
                "insert_after": "comparison",
                "label": "Tender",
                "options": "Tender",
                "read_only":1,
                "fetch_from":"comparison.tender"
            },
            # {
            #     "fieldname": "clearance",
            #     "fieldtype": "Link",
            #     "insert_after": "tender",
            #     "label": "Clearance",
            #     "options": "Clearance",
            #     "read_only":1,
            # },
            {
                "fieldname": "items",
                "fieldtype": "Table",
                "insert_after": "clearance",
                "label": "Items",
                "options": "Task Items"
            },
        ],

        'Stock Entry':
        [
            {
                "fieldname": "against_comparison",
                "fieldtype": "Check",
                "insert_after": "stock_entry_type",
                # "depends_on": "eval:doc.stock_entry_type == 'Material Transfer' || doc.stock_entry_type == 'Material Issue' ",
                "label": "Against Comparison",

            },
            {
                "fieldname": "comparison",
                "fieldtype": "Link",
                "insert_after": "against_comparison",
                "options": "Comparison",
                "depends_on": "eval:doc.against_comparison == 1",
                "mandatory_depends_on": "eval:doc.against_comparison == 1",
                "label": "Comparison",

            },
            {
                "fieldname": "comparison_item",
                "fieldtype": "Link",
                "insert_after": "comparison",
                "options": "Item",
                "depends_on": "eval:doc.against_comparison == 1",
                "mandatory_depends_on": "eval:doc.against_comparison == 1",
                "label": "Comparison Item",

            }
        ],



        'Stock Entry Detail':
        [

            {
                "fieldname": "comparison_item",
                "fieldtype": "Link",
                "insert_after": "item_name",
                "options": "Item",
                "label": "Against Item",
            },
            {
                "fieldname": "comparison_item_name",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "comparison_item",
                "fetch_from": "comparison_item.item_name",
                "label": "Against Item Name",
            }
        ],
        # 'Bank Guarantee':
        # [
        #     {
        #         "fieldname": "comparison",
        #         "fieldtype": "Link",
        #         "insert_after": "amended_from",
        #         "label": "Comparison",
        #         "options": "Comparison"
        #     }
        # ],
        'Bank Account':
        [   
            {
                "fieldname": "grantee_section",
                "fieldtype": "Section Break",
                "insert_after": "mask",
                "label": "Bank grantee section ",

            },
            {
                "fieldname": "income_bank_grantee_rate",
                "fieldtype": "Percent",
                "insert_after": "grantee_section",
                "label": "Income Bank Grantee Rate",
            },
            {
                "fieldname": "outcome_bank_grantee_rate",
                "fieldtype": "Percent",
                "insert_after": "income_bank_grantee_rate",
                "label": "Outcome Bank Grantee Rate",
            },
            {
                "fieldname": "col_22",
                "fieldtype": "Column Break",
                "insert_after": "outcome_bank_grantee_rate",
                "label": "",
            },
            {
                "fieldname": "income_bank_grantee_cost_account",
                "fieldtype": "Link",
                "options" : "Account",
                "insert_after": "col_22",
                "label": "Income Bank grantee Cost  Account",
            },
            {
                "fieldname": "outcome_bank_grantee_cost_account",
                "fieldtype": "Link",
                "options" : "Account",
                "insert_after": "income_bank_grantee_cost_account",
                "label": "Outcome bank grantee Cost Account",
            },
        ],
           'Project':
        [
            {
                "fieldname": "project_warehouse",
                "fieldtype": "Link",
                "options" : "Warehouse",
                "insert_after": "customer",
                "label": "Warehouse",
                "reqd" :1 

            }
         ]
       







    },

    "properties": [
        {
        "doctype": "Journal Entry Account",
        "doctype_or_field": "DocField",
        "fieldname": "reference_type",
        "property": "options",
        "property_type": "Text",
        "value": "\nSales Invoice\nPurchase Invoice\nJournal Entry\nSales Order\nPurchase Order\nExpense Claim\nAsset\nLoan\nPayroll Entry\nEmployee Advance\nExchange Rate Revaluation\nInvoice Discounting\nFees\nPay and Receipt Document\nComparison\nClearance\nTender\nPayroll Month"
    },
    {
        "doctype": "Sales Order",
        "doctype_or_field": "DocField",
        "fieldname": "cost_center",
        "property": "fetch_from",
        "property_type": "Small Text",
        "value": "project.cost_center"
    },
    ],

    'on_setup': 'contracting_13.contracting_13.add_client_Sccript.add_sales_order_script'
}
