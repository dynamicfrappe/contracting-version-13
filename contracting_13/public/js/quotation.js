


frappe.ui.form.on("Quotation", {
    refresh: function (frm) {
      if (frm.doc.docstatus == 1) {
        frm.events.add_custom_btn_event(frm)
      }
    },
    add_custom_btn_event:function(frm){
      frm.add_custom_button(
        __("Make Comparision"),
        function () {
          frappe.model.open_mapped_doc({
            method: "contracting.contract_api.create_comparision",
            frm: frm, 
          });
        },
        __("Create")
      );
    }
})