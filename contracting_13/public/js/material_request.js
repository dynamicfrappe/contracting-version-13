frappe.ui.form.on("Material Request",{

  // onload:function(frm) {

  // },
  setup:function(frm){
    frm.events.setup_comparsion_query(frm)
  },

  refresh:function(frm){
    frm.events.setup_comparsion_query(frm)
  },

  comparison : function (frm) {
    frm.events.setup_comparsion_query(frm)
    },

    setup_comparsion_query:function(frm){
      if(frm.doc.comparison){
        frappe.call({
          "method" : "contracting_13.contracting_13.doctype.stock_functions.stock_entry_setup" ,
          args:{
            "comparison" : frm.doc.comparison,
          },
          freeze: true,
          async: true,
          callback :function(r){
            if (r.message){
              // console.log(r.message)
              // console.log(r.message.items)
              frm.set_value("project",r.message.project)
              frm.set_value("cost_center",r.message.cost_center)
              frm.set_query("comparison_item",function () {
                return {
                  filters: [
                    ["item_code", "in", r.message.items],
                  ],
                };
              });
              frm.refresh_field("comparison_item")
              frm.set_query("comparison_item","items",function () {
                return {
                  filters: [
                    ["item_code", "in", r.message.items],
                  ],
                };
              });
              frm.refresh_fields("items","cost_center","project")
            }
          } 
       
        })
      }
      
    },
    comparison_item:function(frm){
      if(frm.doc.comparison_item && frm.doc.comparison){
        frappe.call({
          "method" : "contracting_13.contracting_13.doctype.stock_functions.get_comparision_items" ,
          args:{
            "comparison" : frm.doc.comparison,
            "item_code" : frm.doc.comparison_item,
          },
          callback :function(r){
            if (r.message){
              frm.clear_table("items")
              $.each(r.message || [], function(i, element) {
                let row = frm.add_child('items', {
                  item_code: element.item_code,
                  item_name: element.item_name,
                  qty: element.total_qty,
                  uom: element.uom,
                  stock_uom: element.uom,
                  transfer_qty: element.total_qty * element.conversion_factor,
                  conversion_factor: element.conversion_factor,
                  basic_rate: element.unit_price,
                  cost_center: frm.doc.cost_center,
                  project: frm.doc.project,
                  item: frm.doc.comparison_item || "", 
                  
              });
              })
              frm.refresh_field("items")
            }
          } 
       
        })
      }
      
  
    },
    //[{'item_code': 'معدن مشكل', 'item_name': 'معدن مشكل', 'uom': None, 'qty': 100.0, 'unit_price': 1500.0, 'conversion_factor': 1}, {'item_code': 'اسمنت',
    // 'item_name': 'اسمنت', 'uom': None, 'qty': 20.0, 'unit_price': 250.0, 'conversion_factor': 1}]
    all_comparsion:function(frm){
      if(frm.doc.all_comparsion && frm.doc.comparison){
        frappe.call({
          "method" : "contracting_13.contracting_13.doctype.stock_functions.get_all_comparsion_item" ,
          args:{
            "comparsion" : frm.doc.comparison,
          },
          callback :function(r){
            if (r.message){
              frm.clear_table("items")
              $.each(r.message || [], function(i, element) {
                let row = frm.add_child('items', {
                  item_code: element.item_code,
                  item_name: element.item_name,
                  qty: element.total_qty,
                  uom: element.uom,
                  stock_uom: element.uom,
                  transfer_qty: element.total_qty * element.conversion_factor,
                  conversion_factor: element.conversion_factor,
                  basic_rate: element.unit_price,
                  
              });
              })
              frm.refresh_field("items")
            }
          } 
       
        })
      }
      
  
    },
    
    
})
