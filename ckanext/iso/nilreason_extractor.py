# iso19139_nilreason_extractor.py
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple, Union


# Preferred, well-known ISO19139/OGC namespace URIs.
# When you parse from a FILE, we can read the original prefix mapping from the XML.
# When you pass an in-memory Element (or a dict containing one), ElementTree typically
# does not preserve original prefixes, only the namespace URIs in tags ("{uri}Local").
# To keep your prefixed XPaths (gmd:..., gco:..., srv:...) working, we map URIs back
# to these preferred prefixes.
PREFERRED_PREFIX_BY_URI: Dict[str, str] = {
    "http://www.isotc211.org/2005/gmd": "gmd",
    "http://www.isotc211.org/2005/gco": "gco",
    "http://www.isotc211.org/2005/srv": "srv",
    "http://www.isotc211.org/2005/gmx": "gmx",
    "http://www.opengis.net/gml": "gml",
    "http://www.w3.org/1999/xlink": "xlink",
    "http://www.w3.org/2001/XMLSchema-instance": "xsi",
}


# Embedded mapping pairs (as before)
MAPPING_PAIRS: List[Tuple[str, str]] = [
    ('ident_individual', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString'),
    ('ident_title', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString'),
    ('ident_abstract', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:abstract/gco:CharacterString'),
    ('ident_keywords', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString'),
    ('ident_topic', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:topicCategory/gmd:MD_TopicCategoryCode'),
    ('ident_datetype', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode'),
    ('ident_date_', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date'),
    ('ident_maintenancefrequency', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd:maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode'),
    ('ident_organisation', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString'),
    ('ident_deliverypoint', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:deliveryPoint/gco:CharacterString'),
    ('ident_city', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:city/gco:CharacterString'),
    ('ident_administrativearea', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:administrativeArea/gco:CharacterString'),
    ('ident_postalcode', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:postalCode/gco:CharacterString'),
    ('ident_country', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:country/gco:CharacterString'),
    ('ident_voice', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString'),
    ('ident_facsimile', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile/gco:CharacterString'),
    ('ident_email', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString'),
    ('ident_online', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource/gmd:linkage/gmd:URL'),
    ('ident_role', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode'),
    ('ident_classification', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_SecurityConstraints/gmd:classification/gmd:MD_ClassificationCode'),
    ('ident_accessconstraints', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_RestrictionCode'),
    ('ident_uselimitation', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco:CharacterString'),
    ('ident_otherconstraints', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString'),
    ('ident_useconstraints', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useConstraints/gmd:MD_RestrictionCode'),
    ('distrib_organisation', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString'),
    ('distrib_individual', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString'),
    ('distrib_position', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:positionName/gco:CharacterString'),
    ('distrib_voice', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString'),
    ('distrib_facsimile', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile/gco:CharacterString'),
    ('distrib_email', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString'),
    ('distrib_online', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource/gmd:linkage/gmd:URL'),
    ('distrib_role', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode'),
    ('dataquality_scopedescription_dataset', 'gmd:MD_Metadata/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:levelDescription/gmd:MD_ScopeDescription/gmd:dataset/gco:CharacterString'),
    ('dataquality_scopedescription_other', 'gmd:MD_Metadata/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:levelDescription/gmd:MD_ScopeDescription/gmd:other/gco:CharacterString'),
    ('ident_alternatetitle', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:alternateTitle/gco:CharacterString'),
    ('quantitativeresult', 'gmd:MD_Metadata/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_QuantitativeAttributeAccuracy/gmd:result/gmd:DQ_QuantitativeResult/gmd:value/gco:Record/gco:Integer'),
    ('refsystem_code', 'gmd:MD_Metadata/gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gco:CharacterString'),
    ('refsystem_codespace', 'gmd:MD_Metadata/gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:codeSpace/gco:CharacterString'),
    ('refsystem_version', 'gmd:MD_Metadata/gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:version/gco:CharacterString'),
    ('contact_organisation', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString'),
    ('contact_individual', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString'),
    ('contact_deliverypoint', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:deliveryPoint/gco:CharacterString'),
    ('contact_city', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:city/gco:CharacterString'),
    ('contact_administrativearea', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:administrativeArea/gco:CharacterString'),
    ('contact_postalcode', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:postalCode/gco:CharacterString'),
    ('contact_country', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:country/gco:CharacterString'),
    ('contact_voice', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString'),
    ('contact_facsimile', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile/gco:CharacterString'),
    ('contact_email', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString'),
    ('contact_online', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource/gmd:linkage/gmd:URL'),
    ('contact_role', 'gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode'),
    ('dataquality_scopecode', 'gmd:MD_Metadata/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode'),
    ('distrib_format_name', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString'),
    ('distrib_format_version', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:version/gco:CharacterString'),
    ('ident_identifier', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString'),
    ('iso_standard', 'gmd:MD_Metadata/gmd:metadataStandardName/gco:CharacterString'),
    ('iso_version', 'gmd:MD_Metadata/gmd:metadataStandardVersion/gco:CharacterString'),
    ('service_type', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/srv:serviceType/gco:LocalName'),
    ('file_identifier', 'gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString'),
    ('hierarchylevel_scopecode', 'gmd:MD_Metadata/gmd:hierarchyLevel/gmd:MD_ScopeCode'),
    ('bbox_east', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:eastBoundLongitude/gco:Decimal'),
    ('bbox_north', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:northBoundLatitude/gco:Decimal'),
    ('bbox_south', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:southBoundLatitude/gco:Decimal'),
    ('bbox_west', 'gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:westBoundLongitude/gco:Decimal'),
    ('resource_fields.url', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource/gmd:linkage/gmd:URL'),
    ('resource_fields.name', 'gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource/gmd:name/gco:CharacterString')
]


def _collect_namespaces(xml_path: str) -> Dict[str, str]:
    """Collect prefix->URI mappings from an XML file."""
    ns: Dict[str, str] = {}
    for _, (prefix, uri) in ET.iterparse(xml_path, events=("start-ns",)):
        prefix = prefix or ""
        # keep the first occurrence for a prefix
        ns.setdefault(prefix, uri)
    return ns


def _collect_ns_from_element(root: ET.Element) -> Dict[str, str]:
    """
    Collect a prefix->URI map from an in-memory ElementTree element.

    NOTE: ElementTree does not preserve original prefixes, so we rebuild a map
    using the URIs we find and attach preferred prefixes (gmd/gco/srv...).
    """
    uris: List[str] = []

    def add_uri(uri: str) -> None:
        if uri and uri not in uris:
            uris.append(uri)

    # scan element tags and attribute names for "{uri}local" patterns
    for el in root.iter():
        if isinstance(el.tag, str) and el.tag.startswith("{"):
            add_uri(el.tag.split("}")[0][1:])
        for ak in el.attrib.keys():
            if isinstance(ak, str) and ak.startswith("{"):
                add_uri(ak.split("}")[0][1:])

    nsmap: Dict[str, str] = {}
    used_prefixes: set[str] = set()

    for uri in uris:
        pref = PREFERRED_PREFIX_BY_URI.get(uri)
        if pref and pref not in used_prefixes:
            nsmap[pref] = uri
            used_prefixes.add(pref)
        else:
            # fallback prefix
            i = 0
            while True:
                cand = f"ns{i}"
                if cand not in used_prefixes and cand not in nsmap:
                    nsmap[cand] = uri
                    used_prefixes.add(cand)
                    break
                i += 1

    # ensure preferred prefixes exist when their URIs are present (or generally useful)
    for uri, pref in PREFERRED_PREFIX_BY_URI.items():
        nsmap.setdefault(pref, uri)
    return nsmap


def _coerce_to_et_element(obj: Any) -> ET.Element:
    """Convert various 'element-like' objects to xml.etree.ElementTree.Element."""
    if isinstance(obj, ET.Element):
        return obj
    if isinstance(obj, ET.ElementTree):
        return obj.getroot()

    # Common case: lxml element
    try:
        from lxml import etree as LET  # type: ignore

        if isinstance(obj, LET._Element):  # type: ignore[attr-defined]
            return ET.fromstring(LET.tostring(obj))
    except Exception:
        pass

    raise TypeError(
        "xml_input must be a file path, an ElementTree Element/ElementTree, or a dict with key 'xml_tree'"
    )


def _get_root_and_ns(xml_input: Union[str, Dict[str, Any], ET.Element, ET.ElementTree]) -> Tuple[ET.Element, Dict[str, str]]:
    """
    Supports the three call styles:
      1) file path (str)
      2) dict with key 'xml_tree'
      3) direct Element (or ElementTree)
    """
    if isinstance(xml_input, str):
        nsmap = _collect_namespaces(xml_input)
        root = ET.parse(xml_input).getroot()
        return root, nsmap

    if isinstance(xml_input, dict):
        if "xml_tree" not in xml_input:
            raise TypeError("dict input must contain key 'xml_tree'")
        root = _coerce_to_et_element(xml_input["xml_tree"])
        return root, _collect_ns_from_element(root)

    root = _coerce_to_et_element(xml_input)
    return root, _collect_ns_from_element(root)


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


def extract_nilreasons(xml_input: Union[str, Dict[str, Any], ET.Element, ET.ElementTree]) -> List[Dict[str, str]]:
    """
    Extract nilReason occurrences for nodes listed in MAPPING_PAIRS.

    Supported inputs:
      1) file path (str)
      2) dict with key 'xml_tree' (your case)
      3) direct Element / ElementTree
    """
    root, nsmap = _get_root_and_ns(xml_input)
    uri_to_prefix = _invert_nsmap(nsmap)

    parent_map: Dict[ET.Element, ET.Element] = {child: parent for parent in root.iter() for child in parent}

    results: List[Dict[str, str]] = []

    for short_name, mapped_path in MAPPING_PAIRS:
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
                "short_name": short_name,
                "nilreason_xpath": nil_xpath,
                "nilReason": nil_val,
                "related_value": related_value,
            })

    return results
