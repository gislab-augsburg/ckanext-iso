"""
Tests for plugin.py.

Tests are written using the pytest library (https://docs.pytest.org), and you
should read the testing guidelines in the CKAN docs:
https://docs.ckan.org/en/2.9/contributing/testing.html

To write tests for your extension you should install the pytest-ckan package:

    pip install pytest-ckan

This will allow you to use CKAN specific fixtures on your tests.

For instance, if your test involves database access you can use `clean_db` to
reset the database:

    import pytest

    from ckan.tests import factories

    @pytest.mark.usefixtures("clean_db")
    def test_some_action():

        dataset = factories.Dataset()

        # ...

For functional tests that involve requests to the application, you can use the
`app` fixture:

    from ckan.plugins import toolkit

    def test_some_endpoint(app):

        url = toolkit.url_for('myblueprint.some_endpoint')

        response = app.get(url)

        assert response.status_code == 200


To temporary patch the CKAN configuration for the duration of a test you can use:

    import pytest

    @pytest.mark.ckan_config("ckanext.myext.some_key", "some_value")
    def test_some_action():
        pass
"""
import pytest
from types import SimpleNamespace
from uuid import UUID

import ckanext.iso.plugin as plugin

def test_plugin():
    pass


@pytest.fixture
def create_schema(monkeypatch):
    monkeypatch.setattr(plugin.toolkit, 'get_validator', lambda name: name)
    monkeypatch.setattr(
        plugin.lib_plugins, 'lookup_package_plugin',
        lambda package_type: SimpleNamespace(
            create_package_schema=lambda: {'title': ['existing-validator']}
        ),
    )


def _return_data(context, data_dict):
    return data_dict.copy()


def test_create_assigns_id_and_empty_identifiers(create_schema):
    data = {'type': 'geoportal', 'file_identifier': '  '}
    result = plugin.package_create(_return_data, {}, data)

    assert str(UUID(result['id'])) == result['id']
    assert result['ident_identifier'] == result['id']
    assert result['file_identifier'] == result['id']


def test_create_preserves_harvest_id_and_file_identifier(create_schema):
    data = {
        'type': 'geoportal',
        'id': 'harvest-package-id',
        'ident_identifier': 'old-id',
        'file_identifier': 'csw-file-id',
    }
    result = plugin.package_create(_return_data, {'schema': {}}, data)

    assert result['id'] == 'harvest-package-id'
    assert result['ident_identifier'] == 'harvest-package-id'
    assert result['file_identifier'] == 'csw-file-id'


def test_create_leaves_other_dataset_types_unchanged(create_schema):
    data = {'type': 'dataset', 'ident_identifier': 'old-id'}
    result = plugin.package_create(_return_data, {}, data)

    assert result == data
    assert 'id' not in result


def test_create_does_not_accept_caller_id_from_regular_user(create_schema):
    data = {'type': 'geoportal', 'id': 'caller-chosen-id'}
    result = plugin.package_create(_return_data, {}, data)

    assert result['id'] != 'caller-chosen-id'
    assert result['ident_identifier'] == result['id']
    assert result['file_identifier'] == result['id']


def test_create_keeps_ckan_id_uniqueness_check(create_schema):
    original_schema = {'title': ['custom-validator']}
    context = {'schema': original_schema}
    seen = {}

    def original_action(action_context, data_dict):
        seen['schema'] = action_context['schema'].copy()
        return data_dict.copy()

    plugin.package_create(original_action, context, {'type': 'geoportal'})

    assert seen['schema']['id'] == [
        'ignore_missing', 'unicode_safe', 'package_id_does_not_exist'
    ]
    assert seen['schema']['title'] == ['custom-validator']
    assert context['schema'] is original_schema


class _Package:
    def __init__(self, package_type='geoportal', extras=None):
        self.id = 'package-id'
        self.type = package_type
        self.extras = extras or {}


class _PackageModel:
    package = _Package()

    @classmethod
    def get(cls, name_or_id):
        assert name_or_id in ('package-id', 'package-name')
        return cls.package


def _context(package):
    _PackageModel.package = package
    return {'model': SimpleNamespace(Package=_PackageModel)}


def test_update_uses_stored_type_and_package_id():
    data = {
        'name': 'package-name',
        'type': 'dataset',
        'ident_identifier': 'old-id',
        'file_identifier': '',
    }
    result = plugin.package_update(_return_data, _context(_Package()), data)

    assert result['ident_identifier'] == 'package-id'
    assert result['file_identifier'] == 'package-id'


def test_update_preserves_existing_file_identifier_when_omitted():
    data = {'id': 'package-id'}
    result = plugin.package_update(
        _return_data, _context(_Package(extras={'file_identifier': 'csw-file-id'})), data
    )

    assert result['ident_identifier'] == 'package-id'
    assert result['file_identifier'] == 'csw-file-id'


def test_update_preserves_supplied_file_identifier():
    data = {'id': 'package-id', 'file_identifier': 'new-file-id'}
    result = plugin.package_update(_return_data, _context(_Package()), data)

    assert result['file_identifier'] == 'new-file-id'
    assert result['ident_identifier'] == 'package-id'


def test_update_leaves_other_dataset_types_unchanged():
    data = {'id': 'package-id', 'ident_identifier': 'old-id'}
    result = plugin.package_update(
        _return_data, _context(_Package(package_type='dataset')), data
    )

    assert result == data


def test_actions_are_registered():
    actions = plugin.LHM_GP_Harvester.get_actions(None)

    assert actions['package_create'] is plugin.package_create
    assert actions['package_update'] is plugin.package_update
