from urlparse import urljoin

from django import template
from django.http import QueryDict

register = template.Library()

def resolve_value(variable, context):
    """
    If given a ``template.Variable`` or ``template.FilterExpression``,
    return the resolved value, otherwise return the given variable object.
    """
    if hasattr(variable, "resolve"):
        if isinstance(variable, template.FilterExpression):
            result = variable.resolve(context, ignore_failures=True)
            if result is None:
                raise template.VariableDoesNotExist(
                    'Failed lookup for "%s"' % variable
                )
            return result
        return variable.resolve(context)
    return variable

#
# Nodes
#

class QueryDictAppendNode(template.Node):
    def __init__(self, query_dict, key, values):
        self.query_dict = query_dict
        self.key = key
        self.values = values

    def render(self, context):
        try:
            query_dict = resolve_value(self.query_dict, context)
            key = resolve_value(self.key, context)
        except template.VariableDoesNotExist:
            return u""
        for value in self.values:
            try:
                query_dict.appendlist(key, resolve_value(value, context))
            except template.VariableDoesNotExist:
                continue
        return u""

class QueryDictReplaceNode(template.Node):
    def __init__(self, query_dict, key, values):
        self.query_dict = query_dict
        self.key = key
        self.values = values

    def render(self, context):
        try:
            query_dict = resolve_value(self.query_dict, context)
            key = resolve_value(self.key, context)
        except template.VariableDoesNotExist:
            return u""
        if key in query_dict:
            del query_dict[key]
        for value in self.values:
            try:
                query_dict.appendlist(key, resolve_value(value, context))
            except template.VariableDoesNotExist:
                continue
        return u""

class QueryDictDeleteKeyNode(template.Node):
    def __init__(self, query_dict, keys):
        self.query_dict = query_dict
        self.keys = keys

    def render(self, context):
        try:
            query_dict = resolve_value(self.query_dict, context)
        except template.VariableDoesNotExist:
            return u""
        for key in self.keys:
            try:
                key = resolve_value(key, context)
                del query_dict[key]
            except (KeyError, template.VariableDoesNotExist):
                continue
        return u""

class QueryDictUpdateNode(template.Node):
    def __init__(self, query_dict, others):
        self.query_dict = query_dict
        self.others = others

    def render(self, context):
        try:
            query_dict = resolve_value(self.query_dict, context)
        except template.VariableDoesNotExist:
            return u""
        for other in self.others:
            try:
                other = resolve_value(other, context)
                query_dict.update(other)
            except template.VariableDoesNotExist:
                continue
        return u""

class QueryDictCloneNode(template.Node):
    def __init__(self, query_dict, as_var):
        self.var = query_dict
        self.as_var = as_var

    def render(self, context):
        try:
            query_dict = resolve_value(self.var, context)
            as_var = resolve_value(self.as_var, context)
            context[as_var] = query_dict.copy()
        except template.VariableDoesNotExist:
            pass
        return u""

class QueryDictNode(template.Node):
    def __init__(self, as_var):
        self.as_var = as_var

    def render(self, context):
        try:
            as_var = resolve_value(self.as_var, context)
            context[as_var] = QueryDict("", mutable=True)
        except template.VariableDoesNotExist:
            pass
        return u""

class QualifiedURLNode(template.Node):
    def __init__(self, path, as_var=None):
        self.path = path
        self.as_var = as_var

    def render(self, context):
        try:
            request = template.Variable("request").resolve(context)
            path = resolve_value(self.path, context)
        except template.VariableDoesNotExist:
            return u""
        url = request.build_absolute_uri(path)
        if self.as_var:
            try:
                as_var = resolve_value(self.as_var, context)
                context[as_var] = url
                return u""
            except template.VariableDoesNotExist:
                return u""
        return url

class CurrentLocationNode(template.Node):
    def __init__(self, as_var=None):
        self.as_var = as_var

    def render(self, context):
        try:
            request = template.Variable("request").resolve(context)
        except template.VariableDoesNotExist:
            return u""
        url = request.path
        querystring = request.GET.urlencode()
        if querystring:
            url = "?".join([url, querystring])
        if self.as_var:
            try:
                as_var = resolve_value(self.as_var, context)
                context[as_var] = url
                return u""
            except template.VariableDoesNotExist:
                return u""
        return url

#
# Compilation Functions
#

def compile_append_key(parser, token):
    """
    Appends one or more value(s) to the list of values for the given ``key``
    in the given ``QueryDict``.

    Usage::

        {% append_key <querydict> <key> [<value> ...] %}

    Note that the ``key`` and ``value`` arguments may be specified as template
    context variable names or quoted literals.
    """
    bits = token.split_contents()
    if not len(bits) > 3:
        raise template.TemplateSyntaxError(
            "'%s' tag requires at least three values: a querydict, a key, and"
            " one or more values to append" % bits[0]
        )
    query_dict = parser.compile_filter(bits[1])
    key = parser.compile_filter(bits[2])
    values = [parser.compile_filter(bit) for bit in bits[3:]]
    return QueryDictAppendNode(query_dict, key, values)

def compile_replace_key(parser, token):
    """
    Replaces the values for a given key in the given ``QueryDict`` with
    the given values. 

    Usage::

        {% replace_key <querydict> <key> [<value> ...] %}

    Note that ``key`` and each ``value`` may refer to other template context
    variables or be given as quoted literals.
    """
    bits = token.split_contents()
    if not len(bits) > 3:
        raise template.TemplateSyntaxError(
            "'%s' tag requires at least three values: a querydict, a key,"
            " and one or more values to set for the key" % bits[0]
        )
    query_dict = parser.compile_filter(bits[1])
    key = parser.compile_filter(bits[2])
    values = [parser.compile_filter(bit) for bit in bits[3:]]
    return QueryDictReplaceNode(query_dict, key, values)

def compile_delete_key(parser, token):
    """
    Removes the given ``key``(s) from the specified ``QueryDict``.

    Usage::

        {% delete_key <querydict> [<key> ...] %}

    Note that the ``key`` arguments may be specified as template context
    variables or as quoted literals.
    """
    bits = token.split_contents()
    if not len(bits) >= 3:
        raise template.TemplateSyntaxError(
            "'%s' tag requires at least two values: a querydict and one"
            " or more keys to delete" % bits[0]
        )
    query_dict = parser.compile_filter(bits[1])
    keys = [parser.compile_filter(bit) for bit in bits[2:]]
    return QueryDictDeleteKeyNode(query_dict, keys)

def compile_update_query_dict(parser, token):
    """
    Updates the given ``QueryDict`` context variable with the values from
    the specified ``other`` context variables.

    Usage::

        {% update_query_dict <querydict> [<other> ...] %}

    """
    bits = token.split_contents()
    if not len(bits) >= 3:
        raise template.TemplateSyntaxError(
            "'%s' tag requires at least two values: a querydict to update"
            " and one or more dicts to merge" % bits[0]
        )
    query_dict = parser.compile_filter(bits[1])
    others = [parser.compile_filter(bit) for bit in bits[2:]]
    return QueryDictUpdateNode(query_dict, others)

def compile_clone_query_dict(parser, token):
    """
    Clone the specified ``QueryDict`` template variable into a context
    variable specified by ``name``.

    Usage::
      
        {% clone_query_dict <querydict> as <name> %}
    
    """
    bits = token.split_contents()
    if not len(bits) == 4 or not bits[2] == u"as":
        raise template.TemplateSyntaxError(
            "'%s' tag must be called with the arguments: querydict variable,"
            " 'as', and a context variable name" % bits[0]
        )
    query_dict = parser.compile_filter(bits[1])
    as_var = parser.compile_filter(bits[3])
    return QueryDictCloneNode(query_dict, as_var)

def compile_query_dict(parser, token):
    """
    Creates a ``QueryDict`` in the context with the specified ``name``.

    Usage::

        {% query_dict as <name> %}

    """
    bits = token.split_contents()
    if not len(bits) == 3 or not bits[1] == u"as":
        raise template.TemplateSyntaxError(
            "'%s' tag must be called with the arguments: 'as', and a context"
            " variable name" % bits[0]
        )
    as_var = parser.compile_filter(bits[2])
    return QueryDictNode(as_var)

def compile_qualified_url(parser, token):
    """
    Render the given path as a fully qualified URL using the current request.

    .. note::
        
        This tag requires that the request object be available in context by
        the name ``'request'``.
    

    Usage::

        {% qualified_url <path> [as <name>] %}

    """
    bits = token.split_contents()
    if len(bits) == 2:
        as_var = None
    elif not len(bits) == 4 or not bits[2] == u"as":
        raise template.TemplateSyntaxError(
            "'%s' tag must be called with the arguments: 'as', and a context"
            " variable name" % bits[0]
        )
    else:
        as_var = parser.compile_filter(bits[3])
    path = parser.compile_filter(bits[1])
    return QualifiedURLNode(path, as_var)
    

def compile_current_location(parser, token):
    """
    Render the current URL path with querystring into a context variable.

    .. note::
        
        This tag requires that the request object be available in context by
        the name ``'request'``.

    Usage::

        {% current_location [as <name>] %}

    """
    bits = token.split_contents()
    if len(bits) == 1:
        as_var = None
    elif not len(bits) == 3 or not bits[1] == u"as":
        raise template.TemplateSyntaxError(
            "'%s' tag must be called with the arguments: 'as', and a context"
            " variable name" % bits[0]
        )
    else:
        as_var = parser.compile_filter(bits[2])
    return CurrentLocationNode(as_var)

# Register those bad boys
register.tag("append_key", compile_append_key)
register.tag("replace_key", compile_replace_key)
register.tag("delete_key", compile_delete_key)
register.tag("update_query_dict", compile_update_query_dict)
register.tag("clone_query_dict", compile_clone_query_dict)
register.tag("query_dict", compile_query_dict)
register.tag("qualified_url", compile_qualified_url)
register.tag("current_location", compile_current_location)
