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

        package_dict['extras'].append({'key': 'schema', 'value': 'baug'})
        package_dict['extras'].append({'key': 'ext_org', 'value': iso_values['responsible-organisation'][0]['organisation-name']})
        package_dict['extras'].append({'key': 'timeliness', 'value': 'auf_anforderung'})
        package_dict['extras'].append({'key': 'geometry_type', 'value': 'point'})
        package_dict['extras'].append({'key': 'archive', 'value': {"archivability": "archivwuerdig", "justification": ""}})
        package_dict['extras'].append({'key': 'intranet', 'value': {"fachverfahren": "alle_mit_geoinfoweb", "geoinfoweb": "alle_nutzer"}})
        package_dict['extras'].append({'key': 'internet_publish', 'value': 'backend'})
        package_dict['extras'].append({'key': 'datenabgabe_extern_mit_auftrag', 'value': 'yes'})
        package_dict['extras'].append({'key': 'open_data', 'value': 'no'})

        package_dict['author'] = iso_values['responsible-organisation'][0]['individual-name']
        package_dict['author_email'] = iso_values['responsible-organisation'][0]['contact-info']['email']

        return package_dict


