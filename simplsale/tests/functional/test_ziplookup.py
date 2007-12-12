from simplejson import loads

from simplsale.tests import *

class TestZipLookupApp(TestController):

    def test_index(self):
        response = self.app.get(url_for('ziplookup', zipcode='98230'))
        data = loads(response.body)
        assert data == dict(city='Blaine', state='WA')
        content_type = response.header_dict['content-type']
        assert content_type.startswith('application/json')
