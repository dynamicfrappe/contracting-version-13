frappe.ui.form.on("Sales Order", {
  setup: function (frm) {
  },
  refresh: function (frm) {
    frm.events.get_cost_centrt(frm)
    frm.set_query("comparison", function () {
      return {
        filters: {
          tender_status: ["in", ["Approved"]],
        },
      };
    });
    if (frm.doc.docstatus == 1 && frm.doc.comparison) {
      frm.add_custom_button(
        __("Tasks"),
        function () {
          frappe.model.open_mapped_doc({
            method:
              "contracting.contracting.doctype.task.task.create_tasks_from_sales_order",
            frm: frm, //this.frm
          });
        },
        __("Create")
      );
    }
    frm.add_custom_button(
      __("Clearence"),
      function () {
        frappe.model.open_mapped_doc({
          method: "contracting.contracting.add_client_Sccript.make_clearence",
          frm: frm, //this.frm
        });
      },
      __("Create")
    );

    frm.add_custom_button(
      __("Grand Clearance"),
      function () {
        frappe.model.open_mapped_doc({
          method:
            "contracting.contracting.doctype.clearance.clearance.create_grand_clearance",
          frm: frm,
        });
        //frm.events.make_purchase_order(frm);
      },
      __("Create")
    );
  },
  onload: function (frm) {
    console.log("over Write ");
  },
  comparison: function (frm) {
    console.log("com");
    frappe.call({
      method: "contracting.contracting.global_data.get_comparison_data",
      args: { comparison: frm.doc.comparison },
      callback: function (r) {
        if (r.message) {
          console.log(r.message);
          var data = r.message;
          // Set customer from comparison
          frm.doc.customer = data.customer;
          frm.refresh_field("customer");

          // set insurance from comparison

          frm.doc.down_payment_insurance_rate = data.insurance;
          frm.doc.payment_of_insurance_copy = data.d_insurance;
          frm.refresh_field("down_payment_insurance_rate");
          frm.refresh_field("payment_of_insurance_copy");

          // set sales order items
          var i = 0;
          frm.clear_table("items");
          frm.refresh_field("items");
          for (i = 0; i < data.items.length; i++) {
            var row = frm.add_child("items");
            row.item_code = data.items[i].item_code;
            row.item_name = data.items[i].item_name;
            row.description = data.items[i].description;
            row.uom = data.items[i].uom;
            row.qty = data.items[i].current_qty;
            row.rate = data.items[i].price;
            row.amount = data.items[i].amount;
          }
          frm.refresh_field("items");
        } else {
          frappe.throw("Comparison Data Error !");
        }
      },
    });
  },
  is_contracting: function (frm) {
    if (frm.doc.is_contracting == 0) {
      frm.doc.comparison = "";
      frm.refresh_field("comparison");
      frm.doc.customer = " ";
      frm.refresh_field("customer");
      frm.clear_table("items");
      frm.refresh_field("items");
      frm.doc.down_payment_insurance_rate = 0;
      frm.doc.payment_of_insurance_copy = 0;
      frm.refresh_field("down_payment_insurance_rate");
      frm.refresh_field("payment_of_insurance_copy");
    }
  },
  set_contracting(frm) {
    frappe.call({
      method: "contracting.contracting.global_data.get_comparison_data",
      args: { comparison: frm.doc.comparison },
      callback: function (r) {
        if (r.message) {
          console.log(r.message);
          var data = r.message;
          // Set customer from comparison
          frm.doc.customer = data.customer;
          frm.refresh_field("customer");

          // set insurance from comparison

          frm.doc.down_payment_insurance_rate = data.insurance;
          frm.doc.payment_of_insurance_copy = data.d_insurance;
          frm.refresh_field("down_payment_insurance_rate");
          frm.refresh_field("payment_of_insurance_copy");

          // set sales order items
          var i = 0;
          frm.clear_table("items");
          frm.refresh_field("items");
          for (i = 0; i < data.items.length; i++) {
            var row = frm.add_child("items");
            row.item_code = data.items[i].item_code;
            row.item_name = data.items[i].item_name;
            row.description = data.items[i].description;
            row.uom = data.items[i].uom;
            row.qty = data.items[i].current_qty;
            row.rate = data.items[i].price;
            row.amount = data.items[i].amount;
          }
          frm.refresh_field("items");
        } else {
          frappe.throw("Comparison Data Error !");
        }
      },
    });
  },
  project:function(frm){
    if(frm.doc.project){
        frm.events.get_cost_centrt(frm)
    }
  },

  get_cost_centrt:function(frm){
    if(frm.doc.project){
      frm.call({
        'method':"frappe.client.get_value",
        'args': {
          'doctype': 'Project',
          'filters': {
            'name': frm.doc.project
          },
          'fieldname':'cost_center'
        },
        'callback': function(res){
            frm.set_value("cost_center", res.message.cost_center)
            frm.refresh_field("cost_center")
        },
      })
    }
  }
});
