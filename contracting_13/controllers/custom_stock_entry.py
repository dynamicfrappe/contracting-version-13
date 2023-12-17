

import frappe
import erpnext


from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from erpnext.stock.utils import get_incoming_rate





class customStockEntry(StockEntry):
    @frappe.whitelist()
    def get_item_stock_details(self,args_item_detail,args_get_incoming_rate):
        out1 = get_incoming_rate(args_get_incoming_rate)
        out2 = self.get_item_details(args_item_detail)
        print(f'\n\n\n===>out1===>{out1}\n\n')
        print(f'\n\n\n===>out2===>{out2}\n\n')
        print('test2')
        return {'uom':out2.get('uom'),'rate':out1 or 0}