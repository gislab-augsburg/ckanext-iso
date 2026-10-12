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
import ckanext.iso.plugin as plugin

def test_plugin():
    pass


class _Organization:
    def __init__(self, name):
        self.name = name


class _Group:
    @staticmethod
    def get(owner_org):
        if owner_org == 'geoportal-id':
            return _Organization('geoportal')
        return _Organization('other')


class _Model:
    Group = _Group


def test_geoportal_identifiers_are_set_on_create_and_update(monkeypatch):
    current = {
        'id': 'package-id',
        'owner_org': 'geoportal-id',
        'ident_identifier': 'old-metadata-id',
        'file_identifier': '',
    }
    patches = []

    def get_action(name):
        if name == 'package_show':
            return lambda context, data: current.copy()
        if name == 'package_patch':
            def patch(context, data):
                patches.append(data.copy())
                current.update(data)
                plugin.LHM_GP_Harvester.after_update(
                    None, context, current.copy()
                )
            return patch
        raise AssertionError(name)

    monkeypatch.setattr(plugin.toolkit, 'get_action', get_action)
    context = {'model': _Model()}
    pkg_dict = {'id': 'package-id'}

    plugin.LHM_GP_Harvester.after_create(None, context, pkg_dict)
    assert patches == [{
        'id': 'package-id',
        'ident_identifier': 'package-id',
        'file_identifier': 'package-id',
    }]

    current['ident_identifier'] = 'changed-via-api'
    current['file_identifier'] = 'csw-file-id'
    plugin.LHM_GP_Harvester.after_update(None, context, pkg_dict)
    assert patches[-1] == {
        'id': 'package-id',
        'ident_identifier': 'package-id',
    }
    assert current['file_identifier'] == 'csw-file-id'

    plugin.LHM_GP_Harvester.after_update(None, context, pkg_dict)
    assert len(patches) == 2


def test_other_organizations_are_unchanged(monkeypatch):
    def get_action(name):
        if name == 'package_show':
            return lambda context, data: {
                'id': 'package-id',
                'owner_org': 'other-id',
            }
        raise AssertionError(name)

    monkeypatch.setattr(plugin.toolkit, 'get_action', get_action)
    plugin.LHM_GP_Harvester.after_create(
        None, {'model': _Model()}, {'id': 'package-id'}
    )


def test_harvested_file_identifier_is_preserved_on_create(monkeypatch):
    current = {
        'id': 'package-id',
        'owner_org': 'geoportal-id',
        'ident_identifier': 'csw-metadata-id',
        'file_identifier': 'csw-file-id',
    }
    patches = []

    def get_action(name):
        if name == 'package_show':
            return lambda context, data: current.copy()
        if name == 'package_patch':
            return lambda context, data: patches.append(data.copy())
        raise AssertionError(name)

    monkeypatch.setattr(plugin.toolkit, 'get_action', get_action)
    plugin.LHM_GP_Harvester.after_create(
        None, {'model': _Model()}, {'id': 'package-id'}
    )
    assert patches == [{
        'id': 'package-id',
        'ident_identifier': 'package-id',
    }]
