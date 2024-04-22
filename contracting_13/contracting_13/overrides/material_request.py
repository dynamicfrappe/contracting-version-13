from erpnext.stock.doctype.material_request.material_request import MaterialRequest
import frappe


class CustomMaterialRequest(MaterialRequest):
    def validate(self):
        items = self.get("items")
        for item in items:
            sales_order = item.sales_order
            if sales_order:
                doc = frappe.get_doc("Sales Order" , sales_order)
                item.cost_center = doc.cost_center
                item.project = doc.project