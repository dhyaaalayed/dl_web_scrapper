import json
 
# Opening JSON file
from city import City
from my_functions import log
from navigator import Navigator

with open('city_config.json') as json_file:
    city_dict = json.load(json_file)
 

for city_key in city_dict.keys():
    city_obj = city_dict[city_key]
    if city_obj["loading_json_activated"] == False:
        continue
    print("after continue city: {}".format(city_key))
    paths = city_obj["paths"]
    for path in paths:
        city = City(city_key, path, None)
        city.load_nvt_dict_from_stored_json()
        for nvt in city.nvt_list:
            if city_obj["generating_ansprechpartner"] == True:
                log("Operation on NVT {}:".format(nvt.nvt_number))
                log("Generating ansprechpartner liste")
                nvt.export_anshprechpartner_to_excel() # no need to archive the prev one

            if city_obj["updating_montage_activated"] == True:
                log("Archiving current montage")
                nvt.archive_montage_excel()
                
                log("Update montage excel")
                nvt.initialize_montage_excel_parser()
                nvt.montage_excel_parser.update_addresses_from_web()
               
                #### To be called later:
                nvt.montage_excel_parser.update_addresses_from_telekom_excel()
                
                # Now using the new template:
                log("Using the new Montage Excel template")
                nvt.copy_montage_template_to_montage_excel_path()
                nvt.montage_excel_parser.export_current_data_to_excel(nvt.nvt_number)
        log("Exporting Masterliste for {}".format(city.name))
        city.copy_master_liste_template()
        city.export_all_montage_to_one_excel()
