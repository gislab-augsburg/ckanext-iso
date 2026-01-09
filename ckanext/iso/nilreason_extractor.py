# iso19139_nilreason_extractor.py
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple


# Embedded mapping pairs (as before)
MAPPING_PAIRS: List[Tuple[str, str, str]] = [
    ('ident_individual', 'Abteilung / Unterabteilung', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString'),
    ('ident_title', 'Titel', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString'),
    ('ident_abstract', 'Beschreibung', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:abstract/gco:CharacterString'),
    ('ident_keywords', 'Schlagworte', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString'),
    ('ident_topic', 'Thematik', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:topicCategory/gmd:MD_TopicCategoryCode'),
    ('ident_datetype', 'Datumsart', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode'),
    ('ident_date_', 'Datum', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date'),
    ('ident_maintenancefrequency', 'Aktualisierungsintervall', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd:maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode'),
    ('ident_organisation', 'Vertrieb Organisation', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString'),
    ('ident_deliverypoint', 'Vertrieb Straße', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:deliveryPoint/gco:CharacterString'),
    ('ident_city', 'Vertrieb Stadt', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:city/gco:CharacterString'),
    ('ident_administrativearea', 'Vertrieb Bundesland', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:administrativeArea/gco:CharacterString'),
    ('ident_postalcode', 'Vertrieb Postleitzahl', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:postalCode/gco:CharacterString'),
    ('ident_country', 'Vertrieb Land', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:country/gco:CharacterString'),
    ('ident_voice', 'Vertrieb Telefon', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString'),
    ('ident_facsimile', 'Vertrieb Fax', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile/gco:CharacterString'),
    ('ident_email', 'Vertrieb E-Mail', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString'),
    ('ident_online', 'Vertrieb Homepage', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource/gmd:linkage/gmd:URL'),
    ('ident_role', 'Vertrieb Funktion', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode'),
    ('ident_classification', 'Anwendungsbeschränkungen', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_SecurityConstraints/gmd:classification/gmd:MD_ClassificationCode'),
    ('ident_accessconstraints', 'Zugriffsbeschränkungen', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_RestrictionCode'),
    ('ident_uselimitation', 'Nutzungsbeschränkungen', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco:CharacterString'),
    ('ident_otherconstraints', 'Sonstige Beschränkungen', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString'),
    ('ident_useconstraints', 'Sonstige Nutzungsbeschränkungen', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useConstraints/gmd:MD_RestrictionCode'),
    ('distrib_organisation', 'Metadaten Organisation', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString'),
    ('distrib_individual', 'Metadaten Ansprechpartner', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString'),
    ('distrib_position', 'Metadaten Position', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:positionName/gco:CharacterString'),
    ('distrib_voice', 'Metadaten Telefon', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString'),
    ('distrib_facsimile', 'Metadaten Fax', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile/gco:CharacterString'),
    ('distrib_email', 'Metadaten E-Mail', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString'),
    ('distrib_online', 'Metadaten Homepage', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource/gmd:linkage/gmd:URL'),
    ('distrib_role', 'Metadaten Funktion', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode'),
    ('dataquality_scopedescription_dataset', 'Datenqualität Datensatz', 'gmd:MD_Metadata/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:levelDescription/gmd:MD_ScopeDescription/gmd:dataset/gco:CharacterString'),
    ('dataquality_scopedescription_other', 'Datenqualität andere', 'gmd:MD_Metadata/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:levelDescription/gmd:MD_ScopeDescription/gmd:other/gco:CharacterString'),
    ('ident_alternatetitle', 'Datenbeschreibung', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:alternateTitle/gco:CharacterString'),
    ('quantitativeresult', 'Datenergebnis (quantitativ)', 'gmd:MD_Metadata/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_QuantitativeAttributeAccuracy/gmd:result/gmd:DQ_QuantitativeResult/gmd:value/gco:Record/gco:Integer'),
    ('refsystem_code', 'Koordinatensystem-Identifikator', 'gmd:MD_Metadata/gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gco:CharacterString'),
    ('refsystem_codespace', 'Koordinatensystem-Codespace', 'gmd:MD_Metadata/gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:codeSpace/gco:CharacterString'),
    ('refsystem_version', 'Koordinatensystem-Version', 'gmd:MD_Metadata/gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:version/gco:CharacterString'),
    ('contact_organisation', 'Daten Organisation', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString'),
    ('contact_individual', 'Daten Ansprechpartner', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString'),
    ('contact_deliverypoint', 'Daten Straße', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:deliveryPoint/gco:CharacterString'),
    ('contact_city', 'Daten Stadt', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:city/gco:CharacterString'),
    ('contact_administrativearea', 'Daten Bundesland', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:administrativeArea/gco:CharacterString'),
    ('contact_postalcode', 'Daten Postleitzahl', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:postalCode/gco:CharacterString'),
    ('contact_country', 'Daten Land', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:country/gco:CharacterString'),
    ('contact_voice', 'Daten Telefon', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString'),
    ('contact_facsimile', 'Daten Fax', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile/gco:CharacterString'),
    ('contact_email', 'Daten E-Mail', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString'),
    ('contact_online', 'Daten Homepage', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource/gmd:linkage/gmd:URL'),
    ('contact_role', 'Daten Funktion', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode'),
    ('dataquality_scopecode', 'Datentyp', 'gmd:MD_Metadata/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode'),
    ('distrib_format_name', 'Diensteart', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString'),
    ('distrib_format_version', 'Version', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:version/gco:CharacterString'),
    ('ident_identifier', 'Metadaten-Identifikator', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString'),
    ('iso_standard', 'ISO-Standard', 'gmd:MD_Metadata/gmd:metadataStandardName/gco:CharacterString'),
    ('iso_version', 'ISO-Version', 'gmd:MD_Metadata/gmd:metadataStandardVersion/gco:CharacterString'),
    ('service_type', 'Service-Typ', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/srv:serviceType/gco:LocalName'),
    ('file_identifier', 'Datei-Identifikator', 'gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString'),
    ('hierarchylevel_scopecode', 'Hierachielevel Scopecode', 'gmd:MD_Metadata/gmd:hierarchyLevel/gmd:MD_ScopeCode'),
    ('bbox_east', 'Bounding Box Ost', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:eastBoundLongitude/gco:Decimal'),
    ('bbox_north', 'Bounding Box Nord', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:northBoundLatitude/gco:Decimal'),
    ('bbox_south', 'Bounding Box Süd', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:southBoundLatitude/gco:Decimal'),
    ('bbox_west', 'Bounding Box West', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:westBoundLongitude/gco:Decimal'),
    ('resource_fields.url', 'Daten und Ressourcen: URL', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource/gmd:linkage/gmd:URL'),
    ('resource_fields.name', 'Daten und Ressourcen: Name', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource/gmd:name/gco:CharacterString'),
]


def _collect_namespaces(xml_path: str) -> Dict[str, str]:
    ns: Dict[str, str] = {}
    for _, (prefix, uri) in ET.iterparse(xml_path, events=("start-ns",)):
        ns[prefix or ""] = ns.get(prefix or "", uri)
        if (prefix or "") not in ns:
            ns[prefix or ""] = uri
    return ns


def _collect_ns_from_element(root: Any) -> Dict[str, str]:
    """
    Collect namespaces when we don't have a file path.

    Prefer lxml's nsmap (if available) because xml.etree.ElementTree Elements
    do not retain original prefixes.

    Falls back to a small ISO19139 heuristic mapping.
    """
    # lxml root elements provide .nsmap: {prefix: uri}
    nsmap = getattr(root, "nsmap", None)
    if isinstance(nsmap, dict) and nsmap:
        out: Dict[str, str] = {}
        for p, u in nsmap.items():
            if not u:
                continue
            out[p or ""] = u
        return out

    # Heuristic fallback: map known ISO19139 URIs to common prefixes
    known = {
        "http://www.isotc211.org/2005/gmd": "gmd",
        "http://www.isotc211.org/2005/gco": "gco",
        "http://www.isotc211.org/2005/srv": "srv",
        "http://www.isotc211.org/2005/gml": "gml",
        "http://www.isotc211.org/2005/gmx": "gmx",
        "http://www.isotc211.org/2005/xlink": "xlink",
    }

    found_uris: List[str] = []
    try:
        for el in root.iter():
            if isinstance(getattr(el, "tag", None), str) and el.tag.startswith("{"):
                uri = el.tag.split("}", 1)[0][1:]
                if uri not in found_uris:
                    found_uris.append(uri)
            for ak in getattr(el, "attrib", {}).keys():
                if isinstance(ak, str) and ak.startswith("{"):
                    uri = ak.split("}", 1)[0][1:]
                    if uri not in found_uris:
                        found_uris.append(uri)
    except Exception:
        pass

    out: Dict[str, str] = {}
    used_prefixes = set()

    # Assign known prefixes first
    for uri in found_uris:
        if uri in known and known[uri] not in used_prefixes:
            out[known[uri]] = uri
            used_prefixes.add(known[uri])

    # Assign remaining URIs as ns0, ns1, ...
    i = 0
    for uri in found_uris:
        if uri in out.values():
            continue
        while f"ns{i}" in used_prefixes:
            i += 1
        out[f"ns{i}"] = uri
        used_prefixes.add(f"ns{i}")
        i += 1

    return out


def _ensure_et_element(xml_tree: Any) -> ET.Element:
    """Convert common XML element types to xml.etree.ElementTree.Element."""
    if isinstance(xml_tree, ET.Element):
        return xml_tree
    if isinstance(xml_tree, ET.ElementTree):
        return xml_tree.getroot()

    # Try lxml element -> bytes -> ET.Element
    try:
        from lxml import etree as LET  # type: ignore

        if isinstance(xml_tree, LET._Element):
            return ET.fromstring(LET.tostring(xml_tree))
        if isinstance(xml_tree, LET._ElementTree):
            return ET.fromstring(LET.tostring(xml_tree.getroot()))
    except Exception:
        pass

    raise TypeError("xml_tree must be an Element, ElementTree, or lxml element")


def _get_root_and_ns(xml_input: Any) -> Tuple[ET.Element, Dict[str, str]]:
    """
    Accepts:
      1) str: path to XML file
      2) dict: must contain key 'xml_tree'
      3) Element / ElementTree (xml.etree or lxml)

    Returns:
      (root_element_as_ET, nsmap_prefix_to_uri)
    """
    # 1) file path
    if isinstance(xml_input, str):
        nsmap = _collect_namespaces(xml_input)
        tree = ET.parse(xml_input)
        return tree.getroot(), nsmap

    # 2) dict with xml_tree
    if isinstance(xml_input, dict) and "xml_tree" in xml_input:
        raw_root = xml_input["xml_tree"]
        nsmap = _collect_ns_from_element(raw_root)
        return _ensure_et_element(raw_root), nsmap

    # 3) direct element / tree
    nsmap = _collect_ns_from_element(xml_input)
    return _ensure_et_element(xml_input), nsmap


def _invert_nsmap(nsmap: Dict[str, str]) -> Dict[str, str]:
    inv: Dict[str, str] = {}
    for p, u in nsmap.items():
        inv.setdefault(u, p)
    return inv


def _get_nilreason_value(elem: ET.Element) -> Optional[str]:
    for k, v in elem.attrib.items():
        if k == "nilReason" or k.endswith("}nilReason"):
            return v
    return None


def _prefixed_tag(tag: str, uri_to_prefix: Dict[str, str]) -> str:
    if tag.startswith("{"):
        uri, local = tag[1:].split("}", 1)
        prefix = uri_to_prefix.get(uri, "")
        return f"{prefix}:{local}" if prefix else local
    return tag


def _build_full_xpath(
    elem: ET.Element,
    root: ET.Element,
    parent_map: Dict[ET.Element, ET.Element],
    uri_to_prefix: Dict[str, str],
) -> str:
    parts: List[str] = []
    cur: Optional[ET.Element] = elem

    while cur is not None:
        tag = _prefixed_tag(cur.tag, uri_to_prefix)
        parent = parent_map.get(cur)

        if parent is None:
            idx = 1
        else:
            siblings_same = [c for c in list(parent) if c.tag == cur.tag]
            idx = siblings_same.index(cur) + 1

        parts.append(f"{tag}[{idx}]")
        if cur is root:
            break
        cur = parent

    return "/" + "/".join(reversed(parts))


def _normalize_path(mapped_path: str) -> str:
    """
    ElementTree findall() on root expects paths relative to the root.
    Your mappings start with 'gmd:MD_Metadata/...', which will never match
    when root *is already* gmd:MD_Metadata.
    """
    if mapped_path == "gmd:MD_Metadata":
        return "."
    if mapped_path.startswith("gmd:MD_Metadata/"):
        return mapped_path[len("gmd:MD_Metadata/"):]
    return mapped_path


def extract_nilreasons(xml_input: Any) -> List[Dict[str, str]]:
    root, nsmap = _get_root_and_ns(xml_input)
    uri_to_prefix = _invert_nsmap(nsmap)

    parent_map: Dict[ET.Element, ET.Element] = {child: parent for parent in root.iter() for child in parent}

    results: List[Dict[str, str]] = []

    for field_name, label, mapped_path in MAPPING_PAIRS:
        mapped_path = _normalize_path(mapped_path)

        try:
            matches = root.findall(mapped_path, namespaces=nsmap)
        except SyntaxError:
            continue

        for leaf in matches:
            # nilReason on leaf or any ancestor
            nil_elem: Optional[ET.Element] = None
            nil_val = _get_nilreason_value(leaf)

            if nil_val is not None:
                nil_elem = leaf
            else:
                cur = parent_map.get(leaf)
                while cur is not None:
                    nil_val = _get_nilreason_value(cur)
                    if nil_val is not None:
                        nil_elem = cur
                        break
                    cur = parent_map.get(cur)

            if nil_elem is None or nil_val is None:
                continue

            related_value = (leaf.text or "").strip()
            nil_xpath = _build_full_xpath(nil_elem, root, parent_map, uri_to_prefix)

            results.append({
                "field_name": field_name,
                "label": label,
                "nilreason_xpath": nil_xpath,
                "nilReason": nil_val,
                "related_value": related_value,
            })

    return results
