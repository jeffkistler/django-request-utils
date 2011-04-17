.. templatetags:

.. highlight:: django

Available Template Tags
=======================

Django Request Utils offers the following template tags for working with
request and ``QueryDict`` objects.

``query_dict``
--------------

Creates a ``QueryDict`` in the context with the specified ``name``.

Usage::

    {% query_dict as <name> %}

``clone_query_dict``
--------------------

Clone the specified ``QueryDict`` template variable into a context variable
specified by ``name``.

Usage::
                  
    {% clone_query_dict <querydict> as <name> %}

``append_key``
--------------

Appends one or more value(s) to the list of values for the given ``key`` in
the given ``QueryDict``.

Usage::

    {% append_key <querydict> <key> [<value> ...] %}

Note that the ``key`` and ``value`` arguments may be specified as template
context variable names or quoted literals.

``replace_key``
---------------

Replaces the values for a given key in the given ``QueryDict`` with the given
values. 

Usage::

    {% replace_key <querydict> <key> [<value> ...] %}

Note that ``key`` and each ``value`` may refer to other template context
variables or be given as quoted literals.

``delete_key``
--------------

Removes the given ``key`` from the specified ``QueryDict``.

Usage::

    {% delete_key <querydict> [<key> ...] %}

Note that the ``key`` arguments may be specified as template context variables
or as quoted literals.

``update_query_dict``
---------------------

Updates the given ``QueryDict`` context variable with the values from the
specified ``other`` context variables.

Usage::

    {% update_query_dict <querydict> [<other> ...] %}

``qualified_url``
-----------------

Render the given path as a fully qualified URL using the current request.

.. note::
        
    This tag requires that the request object be available in context by
    the name ``'request'``.


Usage::

    {% qualified_url <path> [as <name>] %}

``current_location``
--------------------

Render the current URL path with querystring.

.. note::
        
    This tag requires that the request object be available in context by
    the name ``'request'``.

Usage::

    {% current_location [as <name>] %}
