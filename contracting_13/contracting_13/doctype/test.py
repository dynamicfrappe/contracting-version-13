



import itertools 
# importing "collections" for namedtuple()
import collections
 
# Declaring namedtuple()

data = [
    {'stock_entry_name': 'MAT-STE-2023-00004', 'comparison': 'COM-04-10-23-0005', 'main_item': 'Low Voltage earthing system-Trans 300KVA-2 ohm', 'child_item': '11095', 'child_name': 'رود 3/4 بطول 2 متر DAR', 'qty': 4.0, 'customer': 'mosafa'}, {'stock_entry_name': 'MAT-STE-2023-00003', 'comparison': 'COM-02-10-23-0003', 'main_item': 'Low Voltage earthing system-Trans 300KVA-2 ohm', 'child_item': '01005', 'child_name': 'جلبة ربط 3/4-فيرس', 'qty': 4.0, 'customer': 'mosafa'},]


# x= {'stock_entry_name': 'MAT-STE-2023-00003', 'comparison': 'COM-02-10-23-0003', 'main_item': 'Low Voltage earthing system-Trans 300KVA-2 ohm', 'child_item': '04001', 'child_name': 'رود3/4بطول1.50م-فيرس RB01', 'qty': 8.0, 'customer': 'mosafa'}, {'stock_entry_name': 'MAT-STE-2023-00004', 'comparison': 'COM-04-10-23-0005', 'main_item': 'Low Voltage earthing system-Trans 300KVA-2 ohm', 'child_item': '11003', 'child_name': 'كلامبة مسمار حرف جي3/4 DAR', 'qty': 4.0, 'customer': 'mosafa'}, {'stock_entry_name': 'MAT-STE-2023-00004', 'comparison': 'COM-04-10-23-0005', 'main_item': 'Low Voltage earthing system-Trans 300KVA-2 ohm', 'child_item': '04001', 'child_name': 'رود3/4بطول1.50م-فيرس RB01', 'qty': 8.0, 'customer': 'mosafa'}, {'stock_entry_name': 'MAT-STE-2023-00003', 'comparison': 'COM-02-10-23-0003', 'main_item': 'Low Voltage earthing system-Trans 300KVA-2 ohm', 'child_item': 'كابلات عاري  70 م2', 'child_name': 'كابلات عاري  70 م2', 'qty': 16.0, 'customer': 'mosafa'}, {'stock_entry_name': 'MAT-STE-2023-00003', 'comparison': 'COM-02-10-23-0003', 'main_item': 'Low Voltage earthing system-Trans 300KVA-2 ohm', 'child_item': '02007', 'child_name': 'كلامبة حرف يو قطعتين', 'qty': 4.0, 'customer': 'mosafa'}



key_func = lambda x: (x["customer"],x["stock_entry_name"]) 
result = []
# for key, group in itertools.groupby(data, key_func):
#     print(key + " :", list(group))
fields = ['main_item', 'comparison', 'customer','stock_entry_name','child_item','child_name' ]
Student = collections.namedtuple('Student', fields, defaults=(None,) * len(fields))
for key, group in itertools.groupby(data, key_func):
    head_row = {'main_item':key,'header':True}
    result.append(head_row)
    for child in list(group):
        print(f'\n\n child-->{child}\n\n')
        s1 = Student(**child)
        print(f'\n\n s1-->{s1}\n\n')
    #     result.append(child) 
    # print(result)

