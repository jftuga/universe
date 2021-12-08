from collections import defaultdict

immuniz = defaultdict(dict)
immuniz["Client Record Identifier"]["dataType"] = 24
immuniz["Client Record Identifier"]["position"] = 1
immuniz["Vaccine Group"]["dataType"] = 16
immuniz["Vaccine Group"]["position"] = 25
immuniz["CPT Code"]["dataType"] = 5
immuniz["CPT Code"]["position"] = 41
immuniz["Trade Name"]["dataType"] = 24
immuniz["Trade Name"]["position"] = 46
immuniz["Vaccination Date"]["dataType"] = 8
immuniz["Vaccination Date"]["position"] = 70
immuniz["Administration Route Code"]["dataType"] = 2
immuniz["Administration Route Code"]["position"] = 78
immuniz["Body Site Code"]["dataType"] = 4
immuniz["Body Site Code"]["position"] = 80
immuniz["Reaction Code"]["dataType"] = 8
immuniz["Reaction Code"]["position"] = 84
immuniz["Manufacturer Code"]["dataType"] = 4
immuniz["Manufacturer Code"]["position"] = 92
immuniz["Immunization Information Source"]["dataType"] = 2
immuniz["Immunization Information Source"]["position"] = 96
immuniz["Lot Number"]["dataType"] = 30
immuniz["Lot Number"]["position"] = 98
immuniz["Provider Name"]["dataType"] = 50
immuniz["Provider Name"]["position"] = 128
immuniz["Administered By Name"]["dataType"] = 50
immuniz["Administered By Name"]["position"] = 178
immuniz["Site Name"]["dataType"] = 30
immuniz["Site Name"]["position"] = 228
immuniz["Sending Organization"]["dataType"] = 5
immuniz["Sending Organization"]["position"] = 258
immuniz["Eligibility Code"]["dataType"] = 3
immuniz["Eligibility Code"]["position"] = 263

def load_sort_order() -> dict:
    imm_order = {}
    i = 0
    for name in immuniz:
        imm_order[name] = immuniz[name]["position"]

    return imm_order


def main():
    imm_order = load_sort_order()
    for k in sorted(imm_order, key=imm_order.get):
        #print(f"immuniz['{k}']['dataType'] = ", immuniz[k]['dataType'])
        print(f"immuniz['{k}']['position'] = ", immuniz[k]['position'])


if "__main__" == __name__:
    main()
