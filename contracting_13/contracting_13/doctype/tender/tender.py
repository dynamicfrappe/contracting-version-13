# Copyright (c) 2021, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from contracting_13.contracting_13.doctype.sales_order.sales_order import set_delivery_date
from erpnext import get_default_company
from contracting_13.contracting_13.doctype.sales_order.sales_order import is_product_bundle
from frappe.model.mapper import get_mapped_doc
import json
from frappe import _

from frappe.utils.data import flt, get_link_to_form, nowdate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from six import string_types


class Tender(Document):

    @frappe.whitelist()
    def validate(self):
        #check insurance 
        self.validate_comparison()
        self.validate_incurance_details()
        # template states
        self.validate_states_template()


    def on_submit(self):
        self.validate_status()
        self.set_insurance_value_to_comparison()
        self.validate_terms_sheet()
        if self.terms_paid and self.terms_sheet_amount > 0 and self.current_status == "Approved":
            self.create_terms_journal_entries()
        #""" 
        # Add Insurance to comaprison 
        # """
        # if self.risk_insurance_amount > 0 and self.current_status == "Approved":
        #     self.create_risk_insurance_journal_entries()
        # if self.insurance_amount > 0 and self.current_status == "Approved":
        #     self.create_insurance_journal_entries()

    def set_insurance_value_to_comparison(self):
        comparison = frappe.get_doc("Comparison",self.comparison)
        comparison.insurances_on_deleviery = self.insurances_on_deleviery
        comparison.expenses_insurances = self.expenses_insurances
        comparison.payed_in_clearance_insurances = self.payed_in_clearance_insurances
        comparison.delevery_insurance_value_rate_= self.insurances_on_deleviery
        comparison.insurances_on_deleviery = self.delevery_insurance_amount
        #comparison.expenses_insurances = self.expenses_insurances
        comparison.flags.ignore_mandatory = 1
        comparison.save()
        
    def validate_incurance_details(self):
        self.total_insurance = 0
        if self.insurances :
            self.insurances_on_deleviery = 0
            self.delevery_insurance_amount = 0
            self.expenses_insurances =0 
            self.payed_in_clearance_insurances = 0 
            for line in self.insurances :
                #1 - validate type requirement two types  
                # For a Specified Period requrements is avalid validation days
                # for Expenses user shoud add payed_from_account
                self.validate_insurance_line_state(line)
                 #validate types Data 
                 #   """ 
                 #   if line type = Bank Guarantee
                 #   user shoud set Bank , Bank aaccount , Validation Dates
                 #   """
                self.set_insurance_missing_values(line)
               
                self.total_insurance = float(self.total_insurance or 0) + float(line.amount or 0)
                # frappe.throw(str(self.total_insurance))
                if line.type_of_insurance == "For a Specified Period" :
                    self.insurances_on_deleviery    = float(self.insurances_on_deleviery or 0) + float(line.precent or 0)
                    self.delevery_insurance_amount  = float(self.delevery_insurance_amount or 0) + float(line.amount or 0)
                if line.type_of_insurance == "Expenses" :
                     self.expenses_insurances  += float(line.amount or 0) 
                if line.type_of_insurance == "Payed in Clearance" :
                    self.payed_in_clearance_insurances +=  float(line.amount or 0)
    def validate_comparison(self) :
        if self.current_status == "Approved" and not self.comparison :
            frappe.throw(_(""" Can Not Approve Tender  Without Comparison  """))
        comparison = frappe.db.sql(""" SELECT docstatus as state FROM `tabComparison` WHERE name = '{}' 
                                  
                                        """.format(self.comparison) ,as_dict=1)   
        if self.current_status == "Approved"  and comparison[0].get("state") == 1 : 
            frappe.throw(_("""You Can Not Select Submited Comparison \n
                            Invalid Comparison """))

       
    def validate_insurance_line_state(self , obj ):
        if obj.type_of_insurance == "For a Specified Period" :
            if not obj.vaidation_days or obj.vaidation_days ==0 :
                frappe.throw(_(""" Please Set validation Days in Insurances Table For Value  {}
                        """.format(obj.incurance_detail)))
           
        if obj.type_of_insurance =="Expenses" : 
            if not obj.payed_from_account :
                frappe.throw(_("""
                                Please Set Expenses in Field Payed From Account
                                in Insurances Table For Value  {}
                                """.format(obj.incurance_detail)))
       
    # set insurance table missing Values 
    def set_insurance_missing_values(self ,line):
        if line.pay_method == "Bank Guarantee" :
       
              
            if line.bank and line.account :
                validate_bank_with_account(line.bank , line.account)
            else :
                  frappe.throw(_(""" Please Set Bank And Bank Account To insurance for Value {}""".format(line.incurance_detail)))
        #caculate Amount
        if line.pay_method == "Cash" :
            self.payment_account
        if self.project and line.precent and self.comparison :
            # validate Project 
            project = frappe.get_doc("Project" , self.project)
            # 1 - validate project status 
            if project.status != "Open" :
                message = "{} Is Not open Project".format(project.name)
                send_error_message(message)
            #Project required cost Center
            # if project has no cost center Erro Happend
            if not project.cost_center :
                message = "{} has No Cost Center ".format(project.name )
                send_error_message(message)

            #set Valide Amount and cost center
            if not line.cost_center :
                line.cost_center = project.cost_center
            #set amount 
            if  line.precent > 0:
                line.amount = (float(line.precent) /100) *float(self.total_amount)
                line.remaining_insurance = line.amount

 
    
    def validate_states_template(self):
        total_percent = sum([x.percent for x in self.states_template])
        if total_percent != 100:
            frappe.throw(_("Total States Percent Must be 100%"))



    def validate_terms_sheet(self):
        if self.terms_sheet_amount > 0 and self.terms_paid ==0:
            frappe.throw(_("You Must Pay Terms Sheet Amount"))

    # def calc_insurance_values(self):
    #     insurance_value_rate = 0
    #     delevery_insurance_value_rate = 0
    #     payed_in_clearance_insurances = 0
    #     for item in self.insurances:
    #         if item.type_of_insurance == "Payed in Clearance":
    #             payed_in_clearance_insurances += item.amount

    #         elif item.type_of_insurance == "For a Specified Period":
    #             pass
    #         elif item.type_of_insurance == "Expenses":
    #             pass

    @frappe.whitelist()
    def insert(self, ignore_permissions=None, ignore_links=None, ignore_if_duplicate=False, ignore_mandatory=None, set_name=None, set_child_names=True):
        self.terms_paid = 0
        self.insurance_paid = 0
        # return super().insert(ignore_permissions=ignore_permissions, ignore_links=ignore_links, ignore_if_duplicate=ignore_if_duplicate, ignore_mandatory=ignore_mandatory, set_name=set_name, set_child_names=set_child_names)
        return super().insert(ignore_permissions=ignore_permissions, ignore_links=ignore_links, ignore_if_duplicate=ignore_if_duplicate, ignore_mandatory=ignore_mandatory)

    @frappe.whitelist()
    def get_payment_account(self):
        self.payment_account = ""
        if self.mode_of_payment:
            self.payment_account = get_bank_cash_account(
                self.mode_of_payment, self.company).get("account")
    @frappe.whitelist()
    def create_risk_insurance_journal_entries(self):
        company = frappe.get_doc("Company", self.company)
        

        je = frappe.new_doc("Journal Entry")
        je.posting_date = nowdate()
        je.voucher_type = 'Journal Entry'
        je.company = company.name
        je.cheque_no = self.reference_no
        je.cheque_date = self.reference_date
        je.remark = f'Journal Entry against {self.doctype} : {self.name}'

        je.append("accounts", {
            "account":  self.payment_account,
            "credit_in_account_currency": flt(self.risk_insurance_amount),
            "reference_type": self.doctype,
            "reference_name": self.name,
            "cost_center": self.risk_insurance_cost_center,
            "project": self.project,
        })

        je.append("accounts", {
            "account":   self.risk_insurance_account,
            "debit_in_account_currency": flt(self.risk_insurance_amount),
            "reference_type": self.doctype,
            "reference_name": self.name
        })

        # for i in je.accounts :
        # 	frappe.msgprint(f"account : {i.account} | account_currency : {i.account_currency} | debit_in_account_currency : {i.debit_in_account_currency} | credit_in_account_currency : {i.credit_in_account_currency}")
        je.submit()

        lnk = get_link_to_form(je.doctype, je.name)
        # frappe.msgprint(_("Journal Entry {} was created").format(lnk))





    @frappe.whitelist()
    def create_terms_journal_entries(self):
        company = frappe.get_doc("Company", self.company)
        projects_account = company.terms_sheet_account
        if not projects_account:
            frappe.throw("Please set Terms Sheet Account in Company Settings")

        je = frappe.new_doc("Journal Entry")
        je.posting_date = nowdate()
        je.voucher_type = 'Journal Entry'
        je.company = company.name
        je.cheque_no = self.reference_no
        je.cheque_date = self.reference_date
        je.remark = f'Journal Entry against {self.doctype} : {self.name}'

        je.append("accounts", {
            "account": projects_account,
            "credit_in_account_currency": flt(self.terms_sheet_amount),
            "reference_type": self.doctype,
            "reference_name": self.name,
            "cost_center": self.terms_sheet_cost_center,
            "project": self.project,
        })

        je.append("accounts", {
            "account":   self.project_account,
            "debit_in_account_currency": flt(self.terms_sheet_amount),
            "reference_type": self.doctype,
            "reference_name": self.name
        })

        # for i in je.accounts :
        # 	frappe.msgprint(f"account : {i.account} | account_currency : {i.account_currency} | debit_in_account_currency : {i.debit_in_account_currency} | credit_in_account_currency : {i.credit_in_account_currency}")
        je.submit()

        lnk = get_link_to_form(je.doctype, je.name)
        # frappe.msgprint(_("Journal Entry {} was created").format(lnk))

    @frappe.whitelist()
    def create_terms_payment(self):
        company = frappe.get_doc("Company", self.company)
        projects_account = company.terms_sheet_account
        if not projects_account:
            frappe.throw("Please set Terms Sheet Account in Company Settings")

        payment_je = frappe.new_doc("Journal Entry")
        payment_je.posting_date = nowdate()
        payment_je.voucher_type = 'Journal Entry'
        payment_je.company = company.name
        payment_je.cheque_no = self.reference_no
        payment_je.cheque_date = self.reference_date
        payment_je.remark = f'Payment against {self.doctype} : {self.name}'

        payment_je.append("accounts", {
            "account": self.payment_account,
            "credit_in_account_currency": flt(self.terms_sheet_amount),
            "reference_type": self.doctype,
            "reference_name": self.name,
            "cost_center": self.terms_sheet_cost_center,
            "project": self.project,
        })

        payment_je.append("accounts", {
            "account": projects_account,
            "debit_in_account_currency": flt(self.terms_sheet_amount),
            "reference_type": self.doctype,
            "reference_name": self.name
        })

        payment_je.submit()
        payment_lnk = get_link_to_form(payment_je.doctype, payment_je.name)
        self.terms_paid = 1
        self.save()
        # frappe.msgprint(_("Journal Entry {} was created").format(payment_lnk))

    
    def validate_status(self):
        if self.current_status == "Pending":
            frappe.throw("Cannot Submit Please Approve Or Reject")
        elif self.current_status == "Approved" and self.comparison:
           
                doc = frappe.get_doc("Comparison", self.comparison)
                doc.tender= self.name
                total_insurances = 0
                doc.set("insurances",[])
                for insurance in self.insurances :
                    insure = doc.append("insurances" , {})
                    insure.incurance_detail    = insurance.incurance_detail
                    insure.type_of_insurance = insurance.type_of_insurance
                    insure.pay_method = insurance.pay_method
                    insure.precent = insurance.precent
                    insure.amount = insurance.amount
                    insure.vaidation_days = insurance.vaidation_days
                    insure.payed_from_account = insurance.payed_from_account
                    insure.cost_center =  insurance.cost_center
                    insure.bank_guarantee = insurance.bank_guarantee
                    insure.bank = insurance.bank
                    insure.account= insurance.account
                    insure.remaining_insurance = insurance.amount
                    total_insurances = total_insurances +float(insurance.amount or 0)
                doc.save()
               




                if not self.project:
                    frappe.throw("Please Set Project")
                else:
                    doc.project = self.project
                doc.docstatus = 1
                doc.delivery_insurance_value =self.insurances_on_deleviery
                doc.insurance_value = self.payed_in_clearance_insurances
                doc.total_insurance = float(doc.delivery_insurance_value or 0) + float(doc.total_insurance or 0)
                doc.tender = self.name
                doc.tender_status = self.current_status
                doc.save(ignore_permissions=True)
                doc.submit()
            

    @frappe.whitelist()
    def create_insurance_journal_entries(self):
        company = frappe.get_doc("Company", self.company)
        insurance_account = company.insurance_account_for_others_from_us
        if not insurance_account:
            frappe.throw(
                "Please set Insurance Account for others from us Account in Company Settings")

        je = frappe.new_doc("Journal Entry")
        je.posting_date = nowdate()
        je.voucher_type = 'Journal Entry'
        je.company = company.name
        # je.cheque_no = self.reference_no
        # je.cheque_date = self.reference_date
        je.remark = f'Journal Entry against Insurance for {self.doctype} : {self.name}'

        je.append("accounts", {
            "account": insurance_account,
            "credit_in_account_currency": flt(self.insurance_amount),
            "reference_type": self.doctype,
            "reference_name": self.name,
            "project": self.project,
        })

        je.append("accounts", {
            "account":   self.project_account,
            "debit_in_account_currency": flt(self.insurance_amount),
            "reference_type": self.doctype,
            "reference_name": self.name
        })

        # for i in je.accounts :
        # 	frappe.msgprint(f"account : {i.account} | account_currency : {i.account_currency} | debit_in_account_currency : {i.debit_in_account_currency} | credit_in_account_currency : {i.credit_in_account_currency}")
        je.submit()
        # self.insurance_paid = 1

        lnk = get_link_to_form(je.doctype, je.name)
        # frappe.msgprint(_("Journal Entry {} was created").format(lnk))

    @frappe.whitelist()
    def create_insurance_payment(self):
        company = frappe.get_doc("Company", self.company)
        insurance_account = company.insurance_account_for_others_from_us
        if not insurance_account:
            frappe.throw(
                "Please set Insurance Account for others from us Account in Company Settings")

        je = frappe.new_doc("Journal Entry")
        je.posting_date = nowdate()
        je.voucher_type = 'Journal Entry'
        je.company = company.name
        je.cheque_no = self.reference_no
        je.cheque_date = self.reference_date
        je.remark = f'Journal Entry against Insurance Payment for {self.doctype} : {self.name}'

        je.append("accounts", {
            "account": self.payment_account ,
            "credit_in_account_currency": flt(self.insurance_amount),
            "reference_type": self.doctype,
            "reference_name": self.name,
            "project": self.project,
        })

        je.append("accounts", {
            "account":   insurance_account,
            "debit_in_account_currency": flt(self.insurance_amount),
            "reference_type": self.doctype,
            "reference_name": self.name
        })

        # for i in je.accounts :
        # 	frappe.msgprint(f"account : {i.account} | account_currency : {i.account_currency} | debit_in_account_currency : {i.debit_in_account_currency} | credit_in_account_currency : {i.credit_in_account_currency}")
        je.submit()
        self.insurance_paid = 1
        self.save()

        lnk = get_link_to_form(je.doctype, je.name)
        # frappe.msgprint(_("Journal Entry {} was created").format(lnk))


@frappe.whitelist()
def validate_bank_with_account(bank , account):
    bank_account =    frappe.get_doc( "Bank Account" , account)
    if bank_account.bank != bank :
        frappe.throw(_(" Account {} not For {}".format(bank_account.bank , bank)))





@frappe.whitelist()
def send_error_message(message):
    frappe.throw(_("""{}""".format(message)))


@frappe.whitelist()
def create_payments_for_insurances(obj) :
    tender = frappe.get_doc("Tender" , obj )
    for insure in  tender.insurances :
        if  insure.type_of_insurance == "For a Specified Period" and insure.pay_method=="Cash":
            pass
        if  insure.type_of_insurance == "For a Specified Period" and insure.pay_method=="Bank Guarantee":
            pass
        

        

