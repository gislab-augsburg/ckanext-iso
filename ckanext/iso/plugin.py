import ckan.plugins as p
from ckanext.spatial.interfaces import ISpatialHarvester

class LHM_GP_Harvester(p.SingletonPlugin):

    p.implements(ISpatialHarvester, inherit=True)

    def get_package_dict(self, context, data_dict):

        package_dict = data_dict['package_dict']

        print('MB_edit_03__individual-name:')
        print(iso_values['responsible-organisation'][0]['individual-name'])
        print('MB_edit_03__update_frequ:')
        print(iso_values['frequency-of-update'])

        package_dict['extras'].append(
            {'key': 'schema', 'value': 'baug'},
            {'key': 'ext_org', 'value': 'TBA'},
            {'key': 'timeliness', 'value': 'auf_anforderung'},
            {'key': 'geometry_type', 'value': 'point'},
            {'key': 'archive', 'value': {"archivability": "archivwuerdig", "justification": ""}},
            {'key': 'intranet', 'value': {"fachverfahren": "alle_mit_geoinfoweb", "geoinfoweb": "alle_nutzer"}},
            {'key': 'internet_publish', 'value': 'backend'},
            {'key': 'datenabgabe_extern_mit_auftrag', 'value': 'yes'},
            {'key': 'open_data', 'value': 'no'}
        )

        package_dict['author'] = iso_values['responsible-organisation'][0]['individual-name']
        package_dict['author_email'] = iso_values['responsible-organisation'][0]['contact-info']['email']

        return package_dict


