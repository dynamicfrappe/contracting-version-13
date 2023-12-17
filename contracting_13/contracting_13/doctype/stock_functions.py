
from __future__ import unicode_literals
from frappe import _
import frappe 




#stock entry over write 

# 1- find if contatracting in installed domains 
DOMAINS = frappe.get_active_domains()
@frappe.whitelist()
def fetch_contracting_data(*args , **kwargs ):
    if 'Contracting' in DOMAINS : 
        return True
    else :
         return False


# @frappe.whitelist()
# def test(comparison , *args ,**kwargs):
#     frappe.throw('test')


@frappe.whitelist()
def stock_entry_setup(comparison , *args ,**kwargs):
    print(f'\n\n\n------------------\n\n')
    data = frappe.db.sql(""" SELECT `tabItem`.item_code  FROM  `tabItem`
    inner Join
    `tabComparison Item` on `tabItem`.name = `tabComparison Item`.clearance_item
    WHERE 
    `tabComparison Item`.parent = '%s' """%comparison )
    item_list = []
    for i in data :
        item_list.append(i[0])
    print(f'\n\n\n{item_list}\n\n')
    return (item_list)


#{"parent": item_code, "uom": uom}
@frappe.whitelist()
def get_comparision_items(comparison,item_code):
    sql = f"""SELECT `tabComparison Item Card Stock Item`.item as item_code
    ,`tabComparison Item Card Stock Item`.item_name
    ,`tabComparison Item Card Stock Item`.uom
    ,`tabComparison Item Card Stock Item`.qty
    ,`tabComparison Item Card Stock Item`.unit_price
    ,(if(`tabUOM Conversion Detail`.conversion_factor,null,1)or 1) as conversion_factor
    ,`tabComparison Item`.qty as parent_qty
    ,(`tabComparison Item Card Stock Item`.qty *`tabComparison Item`.qty) as total_qty
    FROM  `tabComparison Item Card`
    INNER JOIN `tabComparison Item Card Stock Item`
    ON `tabComparison Item Card Stock Item`.parent=`tabComparison Item Card`.name
    INNER JOIN `tabComparison Item`
    ON `tabComparison Item`.parent=`tabComparison Item Card`.comparison
    AND `tabComparison Item`.clearance_item='{item_code}'
    LEFT JOIN `tabUOM Conversion Detail`
    ON `tabUOM Conversion Detail`.parent=`tabComparison Item Card Stock Item`.item 
    AND `tabUOM Conversion Detail`.uom=`tabComparison Item Card Stock Item`.uom
    WHERE `tabComparison Item Card`.item_code='{item_code}' AND `tabComparison Item Card`.comparison='{comparison}'
    AND `tabComparison Item Card`.docstatus=1 
                         """
    # frappe.errprint(sql)
    data = frappe.db.sql(
    f"""SELECT `tabComparison Item Card Stock Item`.item as item_code
    ,`tabComparison Item Card Stock Item`.item_name
    ,`tabComparison Item Card Stock Item`.uom
    ,`tabComparison Item Card Stock Item`.qty
    ,`tabComparison Item Card Stock Item`.unit_price
    ,(if(`tabUOM Conversion Detail`.conversion_factor,null,1)or 1) as conversion_factor
    ,`tabComparison Item`.qty as parent_qty
    ,(`tabComparison Item Card Stock Item`.qty *`tabComparison Item`.qty) as total_qty
    FROM  `tabComparison Item Card`
    INNER JOIN `tabComparison Item Card Stock Item`
    ON `tabComparison Item Card Stock Item`.parent=`tabComparison Item Card`.name
    INNER JOIN `tabComparison Item`
    ON `tabComparison Item`.parent=`tabComparison Item Card`.comparison
    AND `tabComparison Item`.clearance_item='{item_code}'
    LEFT JOIN `tabUOM Conversion Detail`
    ON `tabUOM Conversion Detail`.parent=`tabComparison Item Card Stock Item`.item 
    AND `tabUOM Conversion Detail`.uom=`tabComparison Item Card Stock Item`.uom
    WHERE `tabComparison Item Card`.item_code='{item_code}' AND `tabComparison Item Card`.comparison='{comparison}'
    AND `tabComparison Item Card`.docstatus=1 
                         """,as_dict=1)
    return data or []



