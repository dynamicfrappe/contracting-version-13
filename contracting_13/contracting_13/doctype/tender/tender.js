// Copyright (c) 2021, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tender", {
    setup(frm) {
        frm.set_query("project_account", function(doc) {
            // alert(doc.company)
            console.log("doc", doc);
            return {
                filters: {
                    is_group: 0,
                    company: doc.company,
                },
            };
        });
        frm.set_query("risk_insurance_account", function(doc) {
            // alert(doc.company)
            console.log("doc", doc);
            return {
                filters: {
                    is_group: 0,
                    company: doc.company,
                    root_type: "Expense"
                        // account_type:"Expense Account"
                },
            };
        });
        frm.set_query("terms_sheet_cost_center", function(doc) {
            return {
                filters: {
                    is_group: 0,
                    company: doc.company,
                },
            };
        });
        frm.set_query("risk_insurance_cost_center", function(doc) {
            return {
                filters: {
                    is_group: 0,
                    company: doc.company,
                },
            };
        });

    },
    company(frm) {},
    refresh: function(frm) {

        frm.events.set_mandatory_fields(frm)
        // frm.add_custom_button(
        //     __("Insurance Payments"),
        //     function() {
        //         console.log("Fan")
        //     },

        //     __("Create"))

        frm.set_query("comparison", function(doc) {
            return {
                filters: {
                    docstatus: 0,
                },
            };
        });

        //     var details = []
        //     var i =0 
        //     for (i =0 ; i < frm.doc.insurances.length ; i ++){

        //       if (frm.doc.insurances[i].invocied== 0){
        //         details.push(
        //           {

        //           "incurance_detail" :frm.doc.insurances[i].incurance_detail  ,
        //           "type_of_insurance" : frm.doc.insurances[i].type_of_insurance ,
        //           "amount" : frm.doc.insurances[i].amount }

        //         )

        //      }}
        //     var insurance_dialoge = new frappe.ui.Dialog({
        //       title: __("Select incurance"),
        //        'fields': [
        //         {
        //           fieldtype: "Check",
        //           label: __("Against Default Supplier"),
        //           fieldname: "against_default_supplier",
        //           default:0,
        //           hidden: 1,
        //         },

        //         {
        //           fieldname: "items_for_po",
        //           fieldtype: "Table",
        //           label: "Select Items",
        //           cannot_add_rows: true,
        //           in_place_edit: true,
        //           reqd: 1,
        //           data :details,
        //           fields: [
        //             {
        //               fieldtype: "Data",
        //               fieldname: "incurance_detail",
        //               label: __("Incurance Detail"),
        //               read_only: 1,
        //               in_list_view: 1,
        //             },
        //             {
        //               fieldtype: "Data",
        //               fieldname: "type_of_insurance",
        //               label: __("Incurancetype"),
        //               read_only: 1,
        //               in_list_view: 1,
        //             },
        //             {
        //               fieldtype: "Data",
        //               fieldname: "amount",
        //               label: __("Amount"),
        //               read_only: 1,
        //               in_list_view: 1,
        //             },] ,

        //           }



        //       ]  ,
        //       primary_action_label: "Create Payments",
        //       primary_action: function(){
        //         insurance_dialoge.get_field("items_for_po").refresh();
        //         var data = insurance_dialoge.fields_dict.items_for_po.grid.get_selected_children()



        //         data.forEach(function(item) {
        //           console.log(item)
        //         })
        //         insurance_dialoge.hide();
        //         show_alert("Created");
        //     }




        //     })
        //     insurance_dialoge.fields_dict["items_for_po"].df.data = [{"item_code" : "defaulte valus"}]
        //     insurance_dialoge.show();
        //   },
        //   __("Create")
        // );
        if (
            frm.doc.docstatus == 0 &&
            !frm.__islocal &&
            frm.doc.terms_paid == 0 &&
            frm.doc.terms_sheet_amount > 0
        ) {
            //   if (
            //     frm.doc.terms_sheet_amount > 0 &&
            //     frm.doc.current_status == "Approved"
            //   ) {
            frm.add_custom_button(
                __("Terms Sheet Payment"),
                function() {
                    frappe.call({
                        method: "create_terms_payment",
                        doc: frm.doc,
                        callback: function(r) {
                            frm.refresh();
                        },
                    });
                },
                __("Create")
            );
            //   }
        }

        if (
            frm.doc.docstatus == 1 &&
            frm.doc.insurance_paid == 0 &&
            frm.doc.insurance_amount > 0 &&
            frm.doc.current_status == "Approved"
        ) {
            frm.add_custom_button(
                __("Insurance Payment"),
                function() {
                    frappe.call({
                        method: "create_insurance_payment",
                        doc: frm.doc,
                        callback: function(r) {
                            frm.refresh();
                        },
                    });
                },
                __("Create")
            );
            //   }
        }
    },
    mode_of_payment(frm) {
        frm.events.set_mandatory_fields(frm)
        frappe.call({
            method: "get_payment_account",
            doc: frm.doc,
            callback: function(r) {
                frm.refresh_field("payment_account");
            },
        });
    },
    comparison: (frm) => {
        let comparison_name = frm.doc.comparison;
        if (comparison_name != null) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Comparison",
                    name: comparison_name,
                },
                callback: function(r) {
                    if (r.message) {
                        let obj = r.message;
                        frm.set_value("insurance_rate", obj.insurance_value_rate);
                        frm.set_value("insurance_amount", obj.insurance_value);
                        frm.refresh_field("insurance_rate");
                    }
                },
            });
        }
    },
    insurance_rate: (frm) => {
        let ins_rate = parseFloat(frm.doc.insurance_rate);
        let total_amount = parseFloat(frm.doc.total_amount);
        console.log("ins rate", ins_rate);
        console.log("total amount", total_amount);
        let amount = (ins_rate / 100) * total_amount;
        frm.set_value("insurance_amount", amount);
        frm.refresh_field("insurance_amount");
    },

    insurance_amount: function(frm) {
        frm.events.set_mandatory_fields(frm)
    },
    risk_insurance_amount: function(frm) {
        frm.events.set_mandatory_fields(frm)
    },

    terms_paid: function(frm) {
        frm.events.set_mandatory_fields(frm)
    },
    terms_sheet_amount: function(frm) {
        frm.events.set_mandatory_fields(frm)
    },


    set_mandatory_fields(frm) {

        frm.set_df_property("terms_sheet_amount", "read_only", frm.doc.terms_paid == 1)


        frm.set_df_property("project_account", "reqd", frm.doc.terms_sheet_amount > 0 || frm.doc.insurance_amount > 0)
        frm.set_df_property("mode_of_payment", "reqd", frm.doc.terms_sheet_amount > 0 || frm.doc.insurance_amount > 0)

        frm.set_df_property("terms_sheet_cost_center", "reqd", frm.doc.terms_sheet_amount > 0)
        frm.set_df_property("terms_sheet_cost_center", "read_only", frm.doc.terms_paid == 1)


        frm.set_df_property("reference_no", "reqd", frm.doc.mode_of_payment != "Cash" && frm.doc.mode_of_payment)
        frm.set_df_property("reference_date", "reqd", frm.doc.mode_of_payment != "Cash" && frm.doc.mode_of_payment)

        frm.set_df_property("risk_insurance_account", "reqd", frm.doc.risk_insurance_amount > 0)
        frm.set_df_property("risk_insurance_cost_center", "reqd", frm.doc.risk_insurance_amount > 0)


    },


    current_status: function(frm) {
        if (!frm.doc.project && frm.doc.current_status == "Approved") {
            frappe.throw("please Set Project for Approved Tender")
        }
    }
});