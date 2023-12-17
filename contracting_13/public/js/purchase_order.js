frappe.ui.form.on("Purchase Order", {
  refresh(frm) {
    frm.events.get_cost_centrt(frm)
    frm.set_query("comparison", function () {
      return {
        filters: {
          tender_status: ["in", ["Approved"]],
        },
      };
    });
    if (frm.doc.docstatus == 1 && frm.doc.is_contracting) {
      frm.add_custom_button(
        __("Clearence"),
        function () {
          frappe.model.open_mapped_doc({
            method:
              "contracting.contracting.doctype.purchase_order.purchase_order.make_clearence_doc",
            frm: frm, //this.frm
          });
        },
        __("Create")
      );
    }
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
