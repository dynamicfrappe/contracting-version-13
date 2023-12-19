cur_frm.cscript['Make SalOrderes '] = function() {
   frappe.model.open_mapped_doc({
      method: "contracting_13.contracting_13.add_client_Sccript.make_task_clearence",
      frm: frm, //this.frm
    });
}