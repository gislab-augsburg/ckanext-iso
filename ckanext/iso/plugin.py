import ckan.plugins as p
from ckanext.spatial.interfaces import ISpatialHarvester

class LHM_GP_Harvester(p.SingletonPlugin):

    p.implements(ISpatialHarvester, inherit=True)

    def get_package_dict(self, context, data_dict):

        package_dict = data_dict['package_dict']
        iso_values = data_dict['iso_values']
        xml_tree = data_dict['xml_tree']
        harvest_object = data_dict['harvest_object']        

        print('MB_edit_03__individual-name:')
        print(iso_values['responsible-organisation'][0]['individual-name'])
        print('MB_edit_03__update_frequ:')
        print(iso_values['frequency-of-update'])
        print('MB_edit_03__check_package_dict_before:')
        print(package_dict)
        print('-----------------------------------------')
        print(package_dict['extras'])

        package_dict['author'] = iso_values['responsible-organisation'][0]['individual-name']
        package_dict['author_email'] = iso_values['responsible-organisation'][0]['contact-info']['email']
        package_dict['schema'] = 'baug'
        package_dict['ext_org'] = iso_values['responsible-organisation'][0]['organisation-name']
        package_dict['timeliness'] = 'auf_anforderung'
        package_dict['geometry_type'] = 'point'
        package_dict['archive'] = {"archivability": "archivwuerdig", "justification": ""}
        #package_dict['intranet'] = {"fachverfahren": "alle_mit_geoinfoweb", "geoinfoweb": "alle_nutzer"}
        package_dict['internet_publish'] = 'backend'
        package_dict['datenabgabe_extern_mit_auftrag'] = 'yes'
        package_dict['datenabgabe_extern'] = 'no'
        package_dict['open_data'] = 'no'

        print('MB_edit_04__check_package_dict_after:')
        print(package_dict)
        print('-----------------------------------------')
        print(package_dict['extras'])


        return package_dict


