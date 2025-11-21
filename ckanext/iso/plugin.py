import ckan.plugins as p
from ckanext.spatial.interfaces import ISpatialHarvester
from ckanext.spatial.validation.validation import BaseValidator
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
        
        # Define and create directories for saving harvested data in xml and json format
        # To Do: make path_volume configurable:
        path_volume = '/var/lib/ckan'
        path_csw = path_volume + '/csw'
        path_json = path_csw + '/json'
        path_xml = path_csw + '/xml'
        if os.path.exists(path_csw) == False:
            os.mkdir(path_csw)
        if os.path.exists(path_json) == False:
            os.mkdir(path_json)
        if os.path.exists(path_xml) == False:
            os.mkdir(path_xml)
        path_json = f'{path_json}/{guid}'
        path_xml = f'{path_xml}/{guid}'
        
        for key in package_dict:
            if type(package_dict[key]) == bytes:
                package_dict[key] = package_dict[key].decode('utf-8')
        data = json.dumps(package_dict, indent=4)
        f = open(f'{path_json}-package_dict_pre.json', 'w')
        f.write(data)
        f.close()


        # Check Harvest Source Configuration:
        '''
        e.g.: {"default_extras": {"target_dataset_type":"isodata"}}
        dataset type must be specified in active ckan schema
        '''
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
            '''
            Schema field name and extras field name cannot be the same,
            raises Validation Error: {'Extras': 'There is a schema field with the same name'}.
            Solution 2: Delete extras element after assigning as package-dict first level element,
            get values from package_dict extras:
            '''
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


        # Map Iso-Values and XML-Tree to LHM Geoportal-Schema (geoportal_dataset.yaml)
        if target_dataset_type == 'geoportal':

            # Define xml-paths for attributes not included in Iso Values
            tree = etree.ElementTree(xml_tree)
            root = tree.getroot()
            
            # Define namespaces
            gmd = "{http://www.isotc211.org/2005/gmd}"
            gco = "{http://www.isotc211.org/2005/gco}"
            srv = "{http://www.isotc211.org/2005/srv}"
            
            # Abbreviations
            service_ident = f'./{gmd}identificationInfo/{srv}SV_ServiceIdentification'
            data_ident = f'./{gmd}identificationInfo/{gmd}MD_DataIdentification'
            respons_party = f'{gmd}pointOfContact/{gmd}CI_ResponsibleParty'
            adress = f'{gmd}contactInfo/{gmd}CI_Contact/{gmd}address/{gmd}CI_Address'
            phone = f'{gmd}contactInfo/{gmd}CI_Contact/{gmd}phone/{gmd}CI_Telephone'
            online = f'{gmd}contactInfo/{gmd}CI_Contact/{gmd}onlineResource/{gmd}CI_OnlineResource'
            legal = f'{gmd}resourceConstraints/{gmd}MD_LegalConstraints'
            security = f'{gmd}resourceConstraints/{gmd}MD_SecurityConstraints'
            distributor = f'./{gmd}distributionInfo/{gmd}MD_Distribution/{gmd}distributor/{gmd}MD_Distributor'
            distrib_party = f'{gmd}distributorContact/{gmd}CI_ResponsibleParty'
            contact = f'./{gmd}contact/{gmd}CI_ResponsibleParty'
            data_quality = f'./{gmd}dataQualityInfo/{gmd}DQ_DataQuality'
            
            # Needed paths
            ident_deliverypoint = f'{service_ident}/{respons_party}/{adress}/{gmd}deliveryPoint/{gco}CharacterString'
            ident_city = f'{service_ident}/{respons_party}/{adress}/{gmd}city/{gco}CharacterString'
            ident_administrativearea = f'{service_ident}/{respons_party}/{adress}/{gmd}administrativeArea/{gco}CharacterString'
            ident_postalcode = f'{service_ident}/{respons_party}/{adress}/{gmd}postalCode/{gco}CharacterString'
            ident_country = f'{service_ident}/{respons_party}/{adress}/{gmd}country/{gco}CharacterString'
            ident_voice = f'{service_ident}/{respons_party}/{phone}/{gmd}voice/{gco}CharacterString'
            ident_facsimile = f'{service_ident}/{respons_party}/{phone}/{gmd}facsimile/{gco}CharacterString'
            ident_classification = f'{service_ident}/{security}/{gmd}classification/{gmd}MD_ClassificationCode'
            ident_uselimitation = f'{service_ident}/{legal}/{gmd}useLimitation/{gco}CharacterString'
            ident_useconstraints = f'{service_ident}/{legal}/{gmd}useConstraints/{gmd}MD_RestrictionCode'
            distrib_voice = f'{distributor}/{distrib_party}/{phone}/{gmd}voice/{gco}CharacterString'
            distrib_facsimile = f'{distributor}/{distrib_party}/{phone}/{gmd}facsimile/{gco}CharacterString'
            dataquality_scopedescription_dataset = f'{data_quality}/{gmd}scope/{gmd}DQ_Scope/{gmd}levelDescription/{gmd}MD_ScopeDescription/{gmd}dataset/{gco}CharacterString'
            dataquality_scopedescription_other = f'{data_quality}/{gmd}scope/{gmd}DQ_Scope/{gmd}levelDescription/{gmd}MD_ScopeDescription/{gmd}other/{gco}CharacterString'
            quantitativeresult = f'{data_quality}/{gmd}report/{gmd}DQ_QuantitativeAttributeAccuracy/{gmd}result/{gmd}DQ_QuantitativeResult/{gmd}value/{gco}Record/{gco}Integer'
            refsystem_code = f'./{gmd}referenceSystemInfo/{gmd}MD_ReferenceSystem/{gmd}referenceSystemIdentifier/{gmd}RS_Identifier/{gmd}code/{gco}CharacterString'
            refsystem_codespace =f'./{gmd}referenceSystemInfo/{gmd}MD_ReferenceSystem/{gmd}referenceSystemIdentifier/{gmd}RS_Identifier/{gmd}codeSpace/{gco}CharacterString'
            refsystem_version = f'./{gmd}referenceSystemInfo/{gmd}MD_ReferenceSystem/{gmd}referenceSystemIdentifier/{gmd}RS_Identifier/{gmd}version/{gco}CharacterString'
            contact_deliverypoint = f'{contact}/{adress}/{gmd}deliveryPoint/{gco}CharacterString'
            contact_city = f'{contact}/{adress}/{gmd}city/{gco}CharacterString'
            contact_administrativearea = f'{contact}/{adress}/{gmd}administrativeArea/{gco}CharacterString'
            contact_postalcode = f'{contact}/{adress}/{gmd}postalCode/{gco}CharacterString'
            contact_country = f'{contact}/{adress}/{gmd}country/{gco}CharacterString'
            contact_voice = f'{contact}/{phone}/{gmd}voice/{gco}CharacterString'
            contact_facsimile = f'{contact}/{phone}/{gmd}facsimile/{gco}CharacterString'
            dataquality_scopecode = f'./{gmd}dataQualityInfo/{gmd}DQ_DataQuality/{gmd}scope/{gmd}DQ_Scope/{gmd}level/{gmd}MD_ScopeCode'
            ident_identifier = f'{service_ident}/{gmd}citation/{gmd}CI_Citation/{gmd}identifier/{gmd}MD_Identifier/{gmd}code/{gco}CharacterString'

            # Get iso_type
            if len(root.findall(f".//{gmd}MD_DataIdentification")) == 1:
                package_dict['iso_type'] = 'MD_DataIdentification'
                print('---------------- WORKING dataset ---------------')
            else:
                if len(root.findall(f".//{srv}SV_ServiceIdentification")) == 1:
                    package_dict['iso_type'] = 'SV_ServiceIdentification'
                    print('---------------- WORKING Service ---------------')

            # Replace if iso_type is data
            if service_ident in xml_path:
                if package_dict['iso_type'] == 'MD_DataIdentification':
                    xml_path = xml_path.replace(service_ident, data_ident)

            # Define List for attributes that need to be xtracted from xml-tree
            xml_paths = []
            xml_names = []
            

            # Define LHM Geoportal-Schema fields

            package_dict['ident_inividual'] = iso_values["metadata-point-of-contact"][0]["individual-name"] 
            #title                      Done
            #notes                      Done
            #tags / tag_string          Done
            package_dict['ident_topic'] = iso_values["topic-category"][0] #Multi needed?
            package_dict['ident_datetype'] = iso_values["dataset-reference-date"][0]["type"] #Multi needed? If yes Repeating subfields with ident_date
            package_dict['ident_date'] = iso_values["dataset-reference-date"][0]["value"] #Multi needed? If yes Repeating subfields with ident_datetype
            #package_dict['ident_date'] conversion datetime zu date oder Textefeld? -> Einfacher: Textfeld
            package_dict['ident_maintenancefrequency'] = iso_values["frequency-of-update"]
            package_dict['ident_organisation'] = iso_values["metadata-point-of-contact"][0]["organisation-name"] #Multi needed?
            # All following commented out need xml-tree to be extracted from
            # All following with [0]: Check if Multi is needed!
            #package_dict['ident_deliverypoint']
            xml_paths.append(ident_deliverypoint)
            xml_names.append('ident_deliverypoint')
            #package_dict['ident_city']
            xml_paths.append(ident_city)
            xml_names.append('ident_city')
            #package_dict['ident_administrativearea']
            xml_paths.append(ident_administrativearea)
            xml_names.append('ident_administrativearea')
            #package_dict['ident_postalcode']
            xml_paths.append(ident_postalcode)
            xml_names.append('ident_postalcode')
            #package_dict['ident_country']
            xml_paths.append(ident_country)
            xml_names.append('ident_country')
            #package_dict['ident_voice']
            xml_paths.append(ident_voice)
            xml_names.append('ident_voice')
            #package_dict['ident_facsimile']
            xml_paths.append(ident_facsimile)
            xml_names.append('ident_facsimile')
            package_dict['ident_email'] = iso_values["metadata-point-of-contact"][0]["contact-info"]["email"]
            package_dict['ident_online'] = iso_values["metadata-point-of-contact"][0]["contact-info"]["online-resource"]["url"]
            package_dict['ident_role'] = iso_values["metadata-point-of-contact"][0]["role"] 
            #package_dict['ident_classification']
            xml_paths.append(ident_classification)
            xml_names.append('ident_classification')
            package_dict['ident_accessconstraints'] = iso_values["access-constraints"]
            #package_dict['ident_uselimitation']
            xml_paths.append(ident_uselimitation)
            xml_names.append('ident_uselimitation')
            package_dict['ident_otherconstraints'] = iso_values["limitations-on-public-access"]
            #package_dict['ident_otherconstraints']
            xml_paths.append(ident_useconstraints)
            xml_names.append('ident_useconstraints')
            package_dict['distrib_organisation'] = iso_values["distributor"][0]["organisation-name"]
            package_dict['distrib_individual'] = iso_values["distributor"][0]["individual-name"]
            package_dict['distrib_position'] = iso_values["distributor"][0]["position-name"]
            #package_dict['distrib_voice']
            xml_paths.append(distrib_voice)
            xml_names.append('distrib_voice')
            #package_dict['distrib_facsimile']
            xml_paths.append(distrib_facsimile)
            xml_names.append('distrib_facsimile')
            package_dict['distrib_email'] = iso_values["distributor"][0]["contact-info"]["email"]
            package_dict['distrib_online'] = iso_values["distributor"][0]["contact-info"]["online-resource"]["url"]
            package_dict['distrib_role'] = iso_values["distributor"][0]["role"]
            #package_dict['dataquality_scopedescription_dataset']
            xml_paths.append(dataquality_scopedescription_dataset)
            xml_names.append('dataquality_scopedescription_dataset')
            #package_dict['dataquality_scopedescription_other']
            xml_paths.append(dataquality_scopedescription_other)
            xml_names.append('dataquality_scopedescription_other')
            package_dict['ident_alternatetitle'] = iso_values["alternate-title"]
            #package_dict['quantitativeresult']
            xml_paths.append(quantitativeresult)
            xml_names.append('quantitativeresult')
            #package_dict['refsystem_code']
            #package_dict['refsystem_codespace']
            #package_dict['refsystem_version']
            xml_paths.append(refsystem_code)
            xml_names.append('refsystem_code')
            xml_paths.append(refsystem_codespace)
            xml_names.append('refsystem_codespace')
            xml_paths.append(refsystem_version)
            xml_names.append('refsystem_version')
            package_dict['contact_organisation'] = iso_values["responsible-organisation"][0]["organisation-name"]
            package_dict['contact_individual'] = iso_values["responsible-organisation"][0]["individual-name"]
            #package_dict['contact_deliverypoint']
            xml_paths.append(contact_deliverypoint)
            xml_names.append('contact_deliverypoint')
            #package_dict['contact_city']
            xml_paths.append(contact_city)
            xml_names.append('contact_city')
            #package_dict['contact_administrativearea']
            xml_paths.append(contact_administrativearea)
            xml_names.append('contact_administrativearea')
            #package_dict['contact_postalcode']
            xml_paths.append(contact_postalcode)
            xml_names.append('contact_postalcode')
            #package_dict['contact_country']
            xml_paths.append(contact_country)
            xml_names.append('contact_country')
            #package_dict['contact_voice']
            xml_paths.append(contact_voice)
            xml_names.append('contact_voice')
            #package_dict['contact_facsimile']
            xml_paths.append(contact_facsimile)
            xml_names.append('contact_facsimile')
            package_dict['contact_email'] = iso_values["responsible-organisation"][0]["contact-info"]["email"]
            package_dict['contact_online'] = iso_values["responsible-organisation"][0]["contact-info"]["online-resource"]["url"]
            package_dict['contact_role'] = iso_values["responsible-organisation"][0]["role"]
            #package_dict['dataquality_scopecode']
            xml_paths.append(dataquality_scopecode)
            xml_names.append('dataquality_scopecode')
            #package_dict['distrib_format_name']
            #package_dict['distrib_format_version']
            # The both above are already a list of dicts in iso values -> fits for Repeating Subfields of the following
            package_dict['distrib_format'] = iso_values["data-format"]
            #package_dict['ident_identifier']
            xml_paths.append(ident_identifier)
            xml_names.append('ident_identifier')
            #package_dict['owner_org'] Mapping 'ident_inividual' to MDK 'owner_org':
            with open('mapping_orgas.json', 'r') as mapping:
                data = mapping.read()
            orgas = json.loads(data)
            for orga in orgas:
                if package_dict['ident_inividual'] in orgas[orga]:
                    package_dict['owner_org'] = orga
                else:
                    package_dict['owner_org'] = 'sonstige'
            # iso_type, siehe oben
            package_dict['iso_standard'] = iso_values["metadata-standard-name"]
            package_dict['iso_version'] = iso_values["metadata-standard-version"]
            #package_dict['name'] Already right in package_dict

            # Get Values from xml-tree
            i = 0
            for path in xml_paths:
                check = root.find(path)
                # Get name
                name = xml_names[i]
                i = i + 1
                if isinstance(check, type(None)):
                    # Path does not exist in XML
                    value = ''
                else:
                    if not type(check.text) == str:
                        try:
                            value = check.attrib['codeListValue']
                        except:
                            # XML-Pfad existing, content empty (e.g. <gmd:URL />), so no to is-string (value:None) even if it would be if filled
                            # --> fill with '' instead of None to be writable in csv
                            value = ''
                    else:
                        value = check.text

                # Check if multi, if yes, create list of values
                check_multi = root.findall(path)
                if len(check_multi) > 1:
                    vals = []
                    for val in check_multi:  
                        if not type(check.text) == str:
                            try:
                                value = check.attrib['codeListValue']
                                vals.append(value)
                            except:
                                value = ''
                        else:
                            print(val.text)
                            vals.append(val.text)
                    value = str(vals)

                package_dict[name] = value

            # Handle list of dicts for Repeating subfields
            refsystem_list = []
            k = 0
            if 'refsystem_code' in package_dict.keys():
                for ref_code in package_dict['refsystem_code']:
                    ref_codespace = package_dict['refsystem_codespace'][k]
                    ref_version = package_dict['refsystem_version'][k]
                    k = k + 1
                    refsystem_list.append({"refsystem_code": ref_code, "refsystem_codespace": ref_codespace, "refsystem_version": ref_version })
            package_dict["refsystem"] = refsystem_list
            
                     
                    
        
                
            
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
            '''
            Schema field name and extras field name cannot be the same,
            raises Validation Error: {'Extras': 'There is a schema field with the same name'}.
            Solution 2: Delete extras element after assigning as package-dict first level element,
            get values from iso_values:
            '''
            package_dict['spatial-reference-system'] = iso_values['spatial-reference-system']
            package_dict['guid'] = iso_values['guid']
            for item in package_dict['extras']:
                if item['key'] == 'spatial-reference-system':
                    del package_dict['extras'][package_dict['extras'].index(item)]
                elif item['key'] == 'guid':
                    del package_dict['extras'][package_dict['extras'].index(item)]
            

        # Mapping organisations
        '''
        # Example implementation for defining mapping_orgas path in ckan .ini file:
        filepath_config = toolkit.config.get("ckanext.iso.mapping_orgas")
        print('filepath_config')
        print(filepath_config)
        # Example implementation with hardcoded path value:
        filepath = '/usr/local/lib/python3.8/dist-packages/ckanext/iso/mapping_orgas.json'
        '''
        filepath_config = toolkit.config.get("ckanext.iso.mapping_orgas")
        f = open(filepath_config)
        data = json.load(f)
        for orga, iso_orgas in data.items():
            if iso_values['responsible-organisation'][0]['individual-name'] in iso_orgas:
                package_dict['owner_org'] = orga


        # Write files for Schema Mapping II
        tree = etree.ElementTree(xml_tree)
        tree.write(f'{path_xml}-iso_tree.xml')

        for key in iso_values:
            if type(iso_values[key]) == bytes:
                iso_values[key] = iso_values[key].decode('utf-8')
        data = json.dumps(iso_values, indent=4)
        f = open(f'{path_json}-iso_values.json', 'w')
        f.write(data)
        f.close()

        for key in package_dict:
            if type(package_dict[key]) == bytes:
                package_dict[key] = package_dict[key].decode('utf-8')
        data = json.dumps(package_dict, indent=4)
        f = open(f'{path_json}-package_dict_post.json', 'w')
        f.write(data)
        f.close()

        '''
        Set force_import in base.py import_stage if specified in harvest source config like
        {"default_extras": {"target_dataset_type":"isodata", "force_import":"true"}}
        and if status is 'change' (update)
        For development only! Updates will be made any time even if metadata_modified_date
        on csw-server is not more recent then metadata_modified_date of previous object.
        Caution: Previous harvesting objects and others will not be set to current = false,
        so 'ckan harvester source clear-history <source id> -k true' will not work.
        To make it work, do before in pgAdmin:
        UPDATE public.harvest_object SET current = 'false' WHERE harvest_job_id = '<job id>';
        '''
        status = _get_object_extra(harvest_object, 'status')
        for item in package_dict['extras']:
            if item['key'] == 'force_import':
                if item['value'] == 'true':
                    if status == 'change':
                        base.SpatialHarvester.force_import = True
                    else:
                        base.SpatialHarvester.force_import = False

        return package_dict


    # Register custom validator

    def get_validators(self):
        '''
        Allows to register custom Validators that can be applied to harvested
        metadata documents.

        Validators are classes that implement the ``is_valid`` method. Check
        the `Writing custom validators`_ section in the docs to know more
        about writing custom validators.

        :returns: A list of Validator classes
        :rtype: list
        '''
        return [TestValidator]
    

# Cutom validator 

class TestValidator(BaseValidator):
    name = 'testval'
    title = 'Minimal Test Validation'
    _elements = [
        ('File Identifier', '/gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString'),
        ('Hierarchy Level', '/gmd:MD_Metadata/gmd:hierarchyLevel'),
        ('Organisation Name', '/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString')
        ]
    _check_name = [
        ('Organisation Name', '/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString')
        ]
    @classmethod
    def is_valid(cls, xml):
        errors = []
        for title, xpath in cls._elements:
            element = xml.xpath(xpath, namespaces={'gmd': 'http://www.isotc211.org/2005/gmd', 'gco': 'http://www.isotc211.org/2005/gco'})
            if len(element) == 0 or not element[0].text:
                errors.append(('Element not found: {0}'.format(title), None))
            else:
                print(f'Dataset passed validation for {title}, value is {element[0].text}')
        for title, xpath in cls._check_name:
            element = xml.xpath(xpath, namespaces={'gmd': 'http://www.isotc211.org/2005/gmd', 'gco': 'http://www.isotc211.org/2005/gco'})
            print('----------------------')
            print('MB_DEBUG_01')
            try:
                print(element)
            except:
                print('element not printable')
            try:
                print(element[0].text)
            except:
                print('element[0].text not printable')
            try:
                print(len(element))
            except:
                print('len(element) not printable')
            try:
                print(type(element))
            except:
                print('type(element) not printable')
            print('----------------------')
            if len(element) != 0:
                if element[0].text != 'KR-GSM':
                    errors.append(('Orga name (gmd:contact/gmd:CI_ResponsibleParty/gmd:individualName) is not KR-GSM, it is {0}'.format(element[0].text), None))
                else:
                    errors.append(('No organisation name in path /gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString', None))
        if len(errors):
            return False, errors
        return True, []


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
        

