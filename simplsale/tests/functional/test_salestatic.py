from simplsale.tests import *

class TestSalestaticController(TestController):

    def test_minimal_standard_css(self):
        response = self.app.get(url_for(
            controller='salestatic',
            sale_template='minimal',
            path='css/master.css',
            ))
        assert response.body.startswith('/* master.css */')
        content_type = response.header_dict['content-type']
        assert content_type.startswith('text/css')
