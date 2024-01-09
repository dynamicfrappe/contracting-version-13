import frappe 
from frappe import _ 
from frappe.utils import today



"""
controllers
from contracting_13.contracting_13.controllers.create_clearance_gl_entry import create_journal_entry_from_clearance
a = frappe.get_doc("Clearance" ,  "CLR-24-12-23-0101")
create_journal_entry_from_clearance(a)
create_clearance_gl_entry
create journal entry from clearance 

customer  debit account 
insurance debit account (if insurance will pay back )
tax debit account if negative else credit account
insurance exp account if insurance will not pay back 
sales or income account credit account 

cost center 

process :
      every item in clearance should has its income account / if item without income account will use company default income account
      every item in clearance should has its cost center /or will use project cost center 

      

calculation  :

"""
def get_default_account(company , obj , obj_type ,comparison =None):
   default_account = None

   """
   params : company current company name as string 
            obj -- > object name ad Sting 
            obj_type -- > doctype name like (Customer , Item  Or Clearance Item )
            comparison str comparison name required if obj_type = Clearance Item
            return  default_account --> valid Account name as string 
   """
   if obj_type == "Customer" :
      #get default receivable account from company  and check if customer has its own account 
      default_account = frappe.db.get_value("Company" , company , "default_receivable_account")
      print(f"Company default_account {default_account}")
      customer = frappe.get_doc("Customer" , obj)
      for account in customer.accounts :
         if account.company == company :
            default_account = account.account
      if not default_account :
         frappe.throw(_(f"""Please Set default receivable account in company {company} \n
                           Or Set customer Account for customer {customer.customer_name }"""))
         
   if obj_type == "Clearance Item" :  
      default_account = frappe.db.get_value("Company" , company , "default_income_account")
      #item_default_account
      print(f"Company default_account {default_account}")
      comparison_default_account = frappe.get_value("Comparison" , comparison , "income_account")
      if comparison_default_account :
         default_account =comparison_default_account 
         print(f"comparison  default_account {default_account}")
      comparison_item_income_account = frappe.db.sql(f""" SELECT income_account FROM `tabComparison Item` WHERE 
      clearance_item='{obj}' and parent='{comparison}'  """,as_dict=1)
      if  comparison_item_income_account and len( comparison_item_income_account) > 0:
         print("Item data" , comparison_item_income_account)
         default_account =  comparison_item_income_account[0].get("income_account") if\
         comparison_item_income_account[0].get("income_account") else  default_account
         print(f"item  default_account {default_account}")
   if not default_account :
      frappe.throw(f"No Account Found for {obj} -- {obj_type}")
   return default_account


   

@frappe.whitelist()
def create_journal_entry_from_clearance(clearance , *args ,**kwargs) :
   """
   params : clearance  | clearance object 

   requirements receivable account 
               income account for each item
   
               
   Add debit accounts 
   Add credit accounts

   Set account dimensions 
      1- Project 
      2- Cost Center
      3- Comparison Item 
   """
   self  = clearance
   #get original comparison 
   comparison = frappe.get_doc("Comparison" ,self.comparison )
   customer = comparison.customer
   default_receivable_account = get_default_account(comparison.company , customer , "Customer" )
   #calculate Actual item income 
   default_income_account = comparison.income_account if comparison.income_account \
                      else  frappe.db.get_value("Company" , comparison.company , "default_income_account")
   journal_entry = frappe.new_doc("Journal Entry")
   journal_entry.posting_date = today()
   journal_entry.company = comparison.company
   #set customer debit amount 

   # make debit account Gl 
   #add items debit
   for item in self.items: 
      journal_entry.append("accounts" ,{
      "account" : default_receivable_account ,
      "debit_in_account_currency": item.total_price ,
      "party_type" :"Customer" ,
      "party" : customer ,
      "cost_center" :item.cost_center ,
      "project" : comparison.project ,
      "reference_type" :"Comparison" ,
      "reference_name" :self.comparison ,
      "reference_clearance" :self.name ,
      "reference_item" : item.clearance_item , 
      "user_remark" : f"""  Item details  {item.clearance_item } against {customer} \n
                           for clearance {self.name} and comparison {self.comparison} """
         
       })
  
   # add deductions  debit
   for deduction in self.deductions :
      journal_entry.append("accounts" ,{
                  "account" :deduction.account,
                  # "party_type" :"Customer" ,
                  # "party" : customer ,
                  "debit_in_account_currency":  deduction.amount ,
                  "cost_center" :frappe.db.get_value("Project" , comparison.project , "cost_center"),
                  "project" : comparison.project ,
                  "reference_type" :"Comparison" ,
                  "reference_name" :self.comparison,
                  "reference_clearance" :self.name ,
                  "user_remark" : f"""deduction {deduction.description}  - against {customer}  for clearance {self.name} and comparison {self.comparison} """
      })

    # Add Taxes debit
   for tax in self.item_tax :
      if float(tax.tax_amount or 0)> 0 :
        
         journal_entry.append("accounts" ,{
         "account" : default_receivable_account ,
         "debit_in_account_currency": tax.tax_amount ,
         "party_type" :"Customer" ,
         "party" : customer ,
         "cost_center" :tax.cost_center ,
         "project" : comparison.project ,
         "reference_type" :"Comparison" ,
         "reference_name" :self.comparison ,
         "reference_clearance" :self.name ,
         "user_remark" : f""" taxes - against {customer}  for clearance {self.name} and comparison {self.comparison} """
         
          })
      if float(tax.tax_amount or 0) < 0 :
         journal_entry.append("accounts" ,{
            "account" :tax.account_head,
            "debit_in_account_currency": (float(tax.tax_amount or 0)  * -1),
            "cost_center" :tax.cost_center,
            "project" : comparison.project ,
            "reference_type" :"Comparison" ,
            "reference_name" :self.comparison,
            "reference_clearance" :self.name ,
            "user_remark" : f"""Tax  - against {customer}  for clearance {self.name} and comparison {self.comparison} """
      })
   # Add insurance debit 
   for insurance in self.insurances : 
      journal_entry.append("accounts" ,{
               "account" :insurance.insurance_account,
               # "party_type" :"Customer" ,
               # "party" : customer ,
               "debit_in_account_currency":  insurance.amount ,
               "cost_center" :frappe.db.get_value("Project" , comparison.project , "cost_center"),
               "project" : comparison.project ,
               "reference_type" :"Comparison" ,
               "reference_name" :self.comparison,
               "reference_clearance" :self.name ,
               "user_remark" : f"""{insurance.incurance_detail}  - against {customer}  for clearance {self.name} and comparison {self.comparison} """
      })    
   # End Debit Account Adding 


   #make credit accounts Gl 
   #add items credit
   for item in self.items: 
         """
         remove 
         "account" : get_default_account(comparison.company , item.clearance_item ,
                                         "Clearance Item",self.comparison) ,
         
         """
         journal_entry.append("accounts" ,{
               "account" : default_income_account ,
               "credit_in_account_currency": item.total_price ,
               "cost_center" :item.cost_center,
               "project" : comparison.project ,
               "reference_type" :"Comparison" ,
               "reference_name" :self.comparison,
               "reference_clearance" :self.name ,
               "reference_item" : item.clearance_item , 
               "user_remark" : f"""   Item details  {item.clearance_item } against {customer} \n
                              for clearance {self.name} and comparison {self.comparison} """
         })
   # add deductions credit
   for deduction in self.deductions :
      journal_entry.append("accounts" ,{
                     "account" : default_receivable_account ,
                     "credit_in_account_currency": deduction.amount ,
                     "party_type" :"Customer" ,
                     "party" : customer ,
                     "cost_center" :frappe.db.get_value("Project" , comparison.project , "cost_center"),
                     "project" : comparison.project ,
                     "reference_type" :"Comparison" ,
                     "reference_name" :self.comparison ,
                     "reference_clearance" :self.name ,
                     "user_remark" : f"""{deduction.description}  - against {customer}  for clearance {self.name} and comparison {self.comparison} """
         
      })
   # Add Taxes credit
   for tax in self.item_tax :
      if float(tax.tax_amount or 0)> 0 :
         journal_entry.append("accounts" ,{
         "account" :tax.account_head,
         "credit_in_account_currency": tax.tax_amount ,
         "cost_center" :tax.cost_center,
         "project" : comparison.project ,
         "reference_type" :"Comparison" ,
         "reference_name" :self.comparison,
         "reference_clearance" :self.name ,
         "user_remark" : f"""Tax  - against {customer}  for clearance {self.name} and comparison {self.comparison} """
      })
      if float(tax.tax_amount or 0) < 0 :
         #total_debit_taxes+= float(tax.tax_amount)
         journal_entry.append("accounts" ,{
         "account" : default_receivable_account ,
         "credit_in_account_currency": (float(tax.tax_amount or 0)  * -1) ,
         "party_type" :"Customer" ,
         "party" : customer ,
         "cost_center" :tax.cost_center ,
         "project" : comparison.project ,
         "reference_type" :"Comparison" ,
         "reference_name" :self.comparison ,
         "reference_clearance" :self.name ,
         "user_remark" : f""" taxes  - against {customer}  for clearance {self.name} and comparison {self.comparison} """
         
          })
         
   # Add insurance credit 
   for insurance in self.insurances : 
      journal_entry.append("accounts" ,{
            "account" : default_receivable_account ,
            "credit_in_account_currency": insurance.amount ,
            "party_type" :"Customer" ,
            "party" : customer ,
            "cost_center" :frappe.db.get_value("Project" , comparison.project , "cost_center"),
            "project" : comparison.project ,
            "reference_type" :"Comparison" ,
            "reference_name" :self.comparison ,
            "reference_clearance" :self.name ,
            "user_remark" : f"""{insurance.incurance_detail}  - against {customer}  for clearance {self.name} and comparison {self.comparison} """
         
          })
   # end Maintenance 
   

  
   


   
   try :

      journal_entry.save()
      frappe.db.commit()
      journal_entry.docstatus =1 
      journal_entry.save(ignore_permissions =True)
      frappe.db.commit()
      return True
   except Exception as E :
      #create Error Log 
      error_log= frappe.new_doc("Error Log")
      error_log.method = "create_journal_entry_from_clearance"
      error_log.error = str(E) if len(str(E)) < 120 else str(E)[0:120]
      error_log.save()
      frappe.throw(_("An error accorded please see error logs !"))

      return False

#from create_clearence_gl_entry import create_journal_entry_from_clearance