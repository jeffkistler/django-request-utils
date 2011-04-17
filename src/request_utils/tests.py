import unittest

from django.test import RequestFactory
from django.http import QueryDict
from django import template

class RequestUtilsTemplateTagTestCase(unittest.TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def render_template(self, string, context=None):
        context = context or {}
        t = template.Template(string)
        return t.render(template.Context(context))

    def get_request(self, path='/'):
        return self.request_factory.get(path)

    def testResolveValue(self):
        from request_utils.templatetags.request_utils import resolve_value
        parser = template.Parser([])
        context = template.Context({})
        filter_expr = parser.compile_filter('"foo"')
        resolved = resolve_value(filter_expr, context)
        self.assertEquals('foo', resolved)
        filter_expr = parser.compile_filter('foo')
        self.assertRaises(
            template.VariableDoesNotExist,
            resolve_value, filter_expr, context
        )
        filter_expr = parser.compile_filter('foo')
        resolved = resolve_value(filter_expr, template.Context({'foo': 'bar'}))
        self.assertEquals('bar', resolved)
        var = template.Variable('foo')
        self.assertRaises(
            template.VariableDoesNotExist,
            resolve_value, var, context
        )
        literal = 'foo'
        resolved = resolve_value(literal, context)
        self.assertEquals('foo', resolved)

    def testAppendKey(self):
        t = '{% load request_utils %}{% append_key query_dict "foo" "baz" %}{{ query_dict.urlencode|safe }}'
        c = {
            'query_dict': QueryDict("foo=bar", mutable=True),
        }
        rendered = self.render_template(t, c)
        self.assertEquals("foo=bar&foo=baz", rendered)

    def testAppendKeyBadArgs(self):
        t = '{% load request_utils %}{% append_key query_dict %}'
        self.assertRaises(
            template.TemplateSyntaxError,
            template.Template, t
        )

    def testAppendKeyBadVar(self):
        t = '{% load request_utils %}{% append_key query_dict "foo" "baz" %}{{ query_dict.urlencode|safe }}'
        rendered = self.render_template(t)
        self.assertEquals("", rendered)

    def testAppendKeyKeyNotInContext(self):
        t = '{% load request_utils %}{% append_key query_dict foo "bar" %}'
        c = {
            'query_dict': QueryDict('foo=bar', mutable=True),
        }
        rendered = self.render_template(t, c)
        self.assertEquals("", rendered)

    def testAppendKeyValueNotInContext(self):
        t = '{% load request_utils %}{% append_key query_dict "foo" bar %}'
        c = {
            'query_dict': QueryDict('foo=bar', mutable=True),
        }
        rendered = self.render_template(t, c)
        self.assertEquals("", rendered)
        
    def testReplaceKey(self):
        t = '{% load request_utils %}{% replace_key query_dict "foo" "baz" %}{{ query_dict.urlencode|safe }}'
        c = {
            'query_dict': QueryDict("foo=bar", mutable=True),
        }
        rendered = self.render_template(t, c)
        self.assertEquals("foo=baz", rendered)

    def testReplaceKeyBadArgs(self):
        t = '{% load request_utils %}{% replace_key query_dict %}'
        self.assertRaises(
            template.TemplateSyntaxError,
            template.Template, t
        )

    def testReplaceKeyBadVar(self):
        t = '{% load request_utils %}{% replace_key query_dict "foo" "baz" %}{{ query_dict.urlencode|safe }}'
        rendered = self.render_template(t)
        self.assertEquals("", rendered)

    def testReplaceKeyKeyNotInContext(self):
        t = '{% load request_utils %}{% replace_key query_dict foo "bar" %}'
        c = {
            'query_dict': QueryDict('foo=bar', mutable=True),
        }
        rendered = self.render_template(t, c)
        self.assertEquals("", rendered)

    def testAppendKeyValueNotInContext(self):
        t = '{% load request_utils %}{% replace_key query_dict "foo" bar %}'
        c = {
            'query_dict': QueryDict('foo=bar', mutable=True),
        }
        rendered = self.render_template(t, c)
        self.assertEquals("", rendered)

    def testDeleteKey(self):
        t = '{% load request_utils %}{{ query_dict.urlencode|safe }}{% delete_key query_dict "foo" %}{{ query_dict.urlencode|safe }}'
        c = {
            'query_dict': QueryDict('foo=bar', mutable=True)
        }
        rendered = self.render_template(t, c)
        self.assertEquals("foo=bar", rendered)

    def testDeleteKeyBadArgs(self):
        t = '{% load request_utils %}{% delete_key query_dict %}'
        self.assertRaises(
            template.TemplateSyntaxError,
            template.Template, t
        )

    def testDeleteKeyKeyNotInContext(self):
        t = '{% load request_utils %}{% delete_key query_dict foo %}{{ query_dict.urlencode|safe }}'
        c = {
            'query_dict': QueryDict('foo=bar', mutable=True)
        }
        rendered = self.render_template(t, c)
        self.assertEquals("foo=bar", rendered)

    def testDeleteKeyKeyNotInDict(self):
        t = '{% load request_utils %}{% delete_key query_dict "foo" %}{{ query_dict.urlencode|safe }}'
        c = {
            'query_dict': QueryDict('bar=baz', mutable=True)
        }
        rendered = self.render_template(t, c)
        self.assertEquals('bar=baz', rendered)

    def testUpdateQueryDict(self):
        t = '{% load request_utils %}{% update_query_dict original new %}{{ original.urlencode|safe }}'
        c = {
            'original': QueryDict('foo=bar', mutable=True),
            'new': {'baz': 'quux'},
        }
        rendered = self.render_template(t, c)
        self.assertEquals('foo=bar&baz=quux', rendered)

    def testUpdateQueryDictBadArgs(self):
        t = '{% load request_utils %}{% update_query_dict query_dict %}'
        self.assertRaises(
            template.TemplateSyntaxError,
            template.Template, t
        )

    def testUpdateQueryDictUpdateDictNotInContext(self):
        t = '{% load request_utils %}{% update_query_dict query_dict other %}{{ query_dict.urlencode|safe }}'
        c = {
            'query_dict': QueryDict('foo=bar', mutable=True),
        }
        rendered = self.render_template(t, c)
        self.assertEquals('foo=bar', rendered)

    def testCloneQueryDict(self):
        t = '{% load request_utils %}{% clone_query_dict query_dict as "new" %}{{ new.urlencode|safe }}'
        c = {
            'query_dict': QueryDict('foo=bar', mutable=True),
        }
        rendered = self.render_template(t, c)
        self.assertEquals('foo=bar', rendered)

    def testCloneQueryDictBadArgs(self):
        t = '{% load request_utils %}{% clone_query_dict query_dict %}'
        self.assertRaises(
            template.TemplateSyntaxError,
            template.Template, t
        )

    def testCloneQueryDictDestinationNotInContext(self):
        t = '{% load request_utils %}{% clone_query_dict query_dict as destination %}{{ some_var.urlencode|safe }}'
        c = {
            'query_dict': QueryDict('foo=bar'),
        }
        rendered = self.render_template(t, c)
        self.assertEquals('', rendered)

    def testQueryDict(self):
        t = '{% load request_utils %}{% query_dict as "foo" %}{% append_key foo "foo" "bar" %}{{ foo.urlencode|safe }}'
        rendered = self.render_template(t)
        self.assertEquals('foo=bar', rendered)

    def testQueryDictBadArgs(self):
        t = '{% load request_utils %}{% query_dict %}'
        self.assertRaises(
            template.TemplateSyntaxError,
            template.Template, t
        )

    def testQueryDictDestinationNotInContext(self):
        t = '{% load request_utils %}{% query_dict as destination %}{{ some_var.urlencode|safe }}'
        rendered = self.render_template(t)
        self.assertEquals('', rendered)
        
    def testQualifiedURL(self):
        t = '{% load request_utils %}{% qualified_url request.path %}'
        request = self.get_request('/foo/')
        c = {
            'request': request,
        }
        rendered = self.render_template(t, c)
        self.assertEquals('http://testserver/foo/', rendered)

    def testQualifiedURLWithAsVar(self):
        t = '{% load request_utils %}{% qualified_url request.path as "foo" %}No output, then suddenly: {{ foo|safe }}'
        request = self.get_request('/foo/')
        c = {
            'request': request,
        }
        rendered = self.render_template(t, c)
        self.assertEquals('No output, then suddenly: http://testserver/foo/', rendered)

    def testQualifiedURLBadArgs(self):
        t = '{% load request_utils %}{% qualified_url %}'
        self.assertRaises(
            template.TemplateSyntaxError,
            template.Template, t
        )

    def testQualifiedURLDestinationNotInContext(self):
        t = '{% load request_utils %}{% qualified_url request.path as destination %}{{ some_var.urlencode|safe }}'
        request = self.get_request('/foo/')
        c = {
            'request': request,
        }
        rendered = self.render_template(t, c)
        self.assertEquals('', rendered)
        
    def testCurrentLocation(self):
        t = '{% load request_utils %}{% current_location %}'
        request = self.get_request('/foo/')
        c = {
            'request': request,
        }
        rendered = self.render_template(t, c)
        self.assertEquals('/foo/', rendered)

    def testCurrentLocationWithAsVar(self):
        t = '{% load request_utils %}{% current_location as "path" %}No output, then suddenly: {{ path|safe }}'
        request = self.get_request('/foo/')
        c = {
            'request': request,
        }
        rendered = self.render_template(t, c)
        self.assertEquals('No output, then suddenly: /foo/', rendered)

    def testCurrentLocationBadArgs(self):
        t = '{% load request_utils %}{% current_location as "foo" "bar" %}'
        self.assertRaises(
            template.TemplateSyntaxError,
            template.Template, t
        )

    def testCurrentLocationDestinationNotInContext(self):
        t = '{% load request_utils %}{% current_location as destination %}{{ some_var.urlencode|safe }}'
        request = self.get_request('/foo/')
        c = {
            'request': request,
        }
        rendered = self.render_template(t, c)
        self.assertEquals('', rendered)
