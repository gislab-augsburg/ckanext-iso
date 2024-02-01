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
            {'key': 'positional_accuracy', 'value': 'tachymeter'}
        )

        package_dict['schema'] = 'baug'
        package_dict['author'] = iso_values['responsible-organisation'][0]['individual-name']
        package_dict['author_email'] = iso_values['responsible-organisation'][0]['contact-info']['email']
        package_dict['ext_org'] = 'TBA'
        package_dict['timeliness'] = 'auf_anforderung'
        package_dict['geometry_type'] = 'point'
        package_dict['archive'] = 'noch_offen'
        package_dict['fachverfahren'] = 'alle_mit_geoinfoweb'
        package_dict['geoinfoweb'] = 'alle_nutzer'
        package_dict['internet_publish'] = 'backend'
        package_dict['datenabgabe_extern_mit_auftrag'] = 'yes'
        package_dict['open_data'] = 'no'

        return package_dict


