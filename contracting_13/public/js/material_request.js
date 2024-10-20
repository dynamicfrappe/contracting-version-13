frappe.ui.form.on("Material Request",{
  comparison : function (frm) {
          frappe.call({
            "method" : "contracting_13.contracting_13.doctype.stock_functions.stock_entry_setup" ,
            args:{
              "comparison" : frm.doc.comparison,
            },
            callback :function(r){
              if (r.message){

                frm.set_query("comparison_item",function () {
                  return {
                    filters: [
                      ["item_code", "in", r.message],
                    ],
                  };
                });
                frm.refresh_field("comparison_item")
                frm.set_query("comparison_item","items",function () {
                  return {
                    filters: [
                      ["item_code", "in", r.message],
                    ],
                  };
                });
                frm.refresh_field("items")
              }
            } 
         
          })
      
    },

    comparison_item:function(frm){
      if(frm.doc.comparison_item){
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
