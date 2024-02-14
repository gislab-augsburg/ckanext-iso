import ckan.plugins as p
from ckanext.spatial.interfaces import ISpatialHarvester
import ckanext.spatial.harvesters.base as base
import ckan.plugins.toolkit as toolkit
import os
from lxml import etree
import json


class LHM_GP_Harvester(p.SingletonPlugin):

    p.implements(ISpatialHarvester, inherit=True)

    def get_package_dict(self, context, data_dict):

        package_dict = data_dict['package_dict']
        iso_values = data_dict['iso_values']
        xml_tree = data_dict['xml_tree']
        harvest_object = data_dict['harvest_object']


        # Write files for Schema Mapping I
        guid = iso_values['guid']
        path = f'/srv/app/data/{guid}'
        #os.mkdir(path)
        for key in package_dict:
            if type(package_dict[key]) == bytes:
                package_dict[key] = package_dict[key].decode('utf-8')
        data = json.dumps(package_dict, indent=4)
        f = open(f'{path}-package_dict_pre.json', 'w')
        f.write(data)
        f.close()


        # Check Harvest Source Configuration:
        # e.g.: {"default_extras": {"target_dataset_type":"isodata"}}
        # dataset type must be specified in active ckan schema
        for item in package_dict['extras']:
            if item['key'] == 'target_dataset_type':
                target_dataset_type = item['value']
                # Define target schema type:
                package_dict['type'] = target_dataset_type
                del package_dict['extras'][package_dict['extras'].index(item)]
            else:
                target_dataset_type = 'not_defined'


        # Map Iso Values to LHM-Iso-Schema
        if target_dataset_type == 'isodata':
            # Example hard-coded value:
            package_dict['harvest_source'] = 'Geoportal Muenchen'
            # Example iso_values nested:
            package_dict['author'] = iso_values['responsible-organisation'][0]['individual-name']
            package_dict['author_email'] = iso_values['responsible-organisation'][0]['contact-info']['email']
            # Example iso_values:
            package_dict['timeliness'] = iso_values['frequency-of-update']
            package_dict['metadata-standard-name'] = iso_values['metadata-standard-name']
            package_dict['metadata-standard-version'] = iso_values['metadata-standard-version']
            # Example package_dict extras:
            # Schema field name and extras field name cannot be the same,
            # raises Validation Error: {'Extras': 'There is a schema field with the same name'}.
            # Solution 2: Delete extras element after assigning as package-dict first level element,
            # get values from package_dict extras:
            for item in package_dict['extras']:
                if item['key'] == 'spatial-reference-system':
                    package_dict['spatial-reference-system'] = item['value']
                    i = package_dict['extras'].index(item)
                    del package_dict['extras'][i]
                elif item['key'] == 'spatial':
                    package_dict['spatial'] = item['value']
                    i = package_dict['extras'].index(item)
                    del package_dict['extras'][i]
                elif item['key'] == 'guid':
                    package_dict['guid'] = item['value']
                    i = package_dict['extras'].index(item)
                    del package_dict['extras'][i]

            
        # Map Iso Values to LHM-Schema
        # If not defined, target schema/ target_dataset type is "dataset"
        else:
            package_dict['author'] = iso_values['responsible-organisation'][0]['individual-name']
            package_dict['author_email'] = iso_values['responsible-organisation'][0]['contact-info']['email']
            package_dict['schema'] = 'baug'
            package_dict['ext_org'] = iso_values['responsible-organisation'][0]['organisation-name']
            package_dict['timeliness'] = 'auf_anforderung'
            package_dict['geometry_type'] = 'point'
            package_dict['archive'] = '{"archivability": "archivwuerdig", "justification": ""}'
            package_dict['intranet'] = '{"fachverfahren":"zugriffsuser", "geoinfoweb":"organisationseinheiten"}'
            package_dict['internet_publish'] = 'backend'
            package_dict['datenabgabe_extern_mit_auftrag'] = 'yes'
            package_dict['datenabgabe_extern'] = 'no'
            package_dict['open_data'] = 'all_open'
            # Example package_dict extras:
            # Schema field name and extras field name cannot be the same,
            # raises Validation Error: {'Extras': 'There is a schema field with the same name'}.
            # Solution 2: Delete extras element after assigning as package-dict first level element,
            # get values from iso_values:
            package_dict['spatial-reference-system'] = iso_values['spatial-reference-system']
            package_dict['guid'] = iso_values['guid']
            for item in package_dict['extras']:
                if item['key'] == 'spatial-reference-system':
                    del package_dict['extras'][package_dict['extras'].index(item)]
                elif item['key'] == 'guid':
                    del package_dict['extras'][package_dict['extras'].index(item)]
            

        # Mapping organisations
        filepath_config = toolkit.config.get("ckanext.iso.mapping_orgas")
        print('filepath_config')
        print(filepath_config)
        # (above an example implementation from ckanext-lhm, do similar for ckanext-iso)
        filepath = '/srv/app/src/ckanext-iso/ckanext/iso/mapping_orgas.json'
        f = open(filepath)
        data = json.load(f)
        for orga, iso_orgas in data.items():
            if iso_values['responsible-organisation'][0]['individual-name'] in iso_orgas:
                package_dict['owner_org'] = orga


        # Write files for Schema Mapping II
        tree = etree.ElementTree(xml_tree)
        tree.write(f'{path}-iso_tree.xml')

        for key in iso_values:
            if type(iso_values[key]) == bytes:
                iso_values[key] = iso_values[key].decode('utf-8')
        data = json.dumps(iso_values, indent=4)
        f = open(f'{path}-iso_values.json', 'w')
        f.write(data)
        f.close()

        for key in package_dict:
            if type(package_dict[key]) == bytes:
                package_dict[key] = package_dict[key].decode('utf-8')
        data = json.dumps(package_dict, indent=4)
        f = open(f'{path}-package_dict_post.json', 'w')
        f.write(data)
        f.close()

        # Set force_import in base.py import_stage if specified in harvest source config like
        # {"default_extras": {"target_dataset_type":"isodata", "force_import":"true"}}
        # and if status is 'change' (update)
        status = _get_object_extra(harvest_object, 'status')
        for item in package_dict['extras']:
            if item['key'] == 'force_import':
                if item['value'] == 'true':
                    if status == 'change':
                        base.SpatialHarvester.force_import = True
                    else:
                        base.SpatialHarvester.force_import = False

        return package_dict


# Helper Functions

def _get_object_extra(harvest_object, key):
    '''
    Helper function for retrieving the value from a harvest object extra,
    given the key
    '''
    for extra in harvest_object.extras:
        if extra.key == key:
            return extra.value
    return None
        

