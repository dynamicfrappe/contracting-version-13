import frappe 
from frappe import _ 
from erpnext.projects.doctype.task.task import Task



class customTask(Task) :
   """
   validate task state percent and qty against comparison remaining qty and percent 
   """
   def get_previous_state_completed_amount(self , item , state ):
      """
      param : item -- item code as string 
              state current task comparison state
            return sum of completed qty in current state  
      
      """
      # tabComparison Item Log
      completed_qty = 0
      sql_sum_completed_qty_for_current_state = frappe.db.sql(f"""
      SELECT SUM(qty) as current_qty FROM `tabComparison Item Log` WHERE 
      comparison ='{self.comparison}' and item_code = '{item}' and state = '{state}'
      """,as_dict =1)
      if sql_sum_completed_qty_for_current_state and len(sql_sum_completed_qty_for_current_state) > 0 :
         completed_qty = float(sql_sum_completed_qty_for_current_state[0].get("current_qty") or 0)
      return completed_qty 
   def get_comparison_item_remaining_qty(self , item ,state ) :
      """
      param : item -- item code as string 
              state current task comparison state 
      return current remaining qty for this item 
      
      """
      comparison = frappe.get_doc("Comparison" , self.comparison)
      for item_code in comparison.item :
         if item_code.clearance_item == item :
            return ( float(item_code.qty) - self.get_previous_state_completed_amount(item ,state ))

      
   def __init__(self, *args , **kwargs) :
      return super(customTask , self).__init__(*args , **kwargs)
   def validate(self) :
      if self.comparison :
         for item in self.items :
            remaining_qty = self.get_comparison_item_remaining_qty(item.item_code ,item.state)
            if float(remaining_qty or 0) < float(item.qty) :
              frappe.throw(str(f"remaining qty in current state {item.state} is  {remaining_qty} not allowed to add {item.qty}"))
         pass
        