Froshki
=======

Froshki is a simple and poor object data mapper library.

Looking quite similar to `WTForms
<http://wtforms.simplecodes.com/>`_,
rather intended to focus on data input/output abstraction,
separating validation or conversion functions as APIs & extensions.

Instead of integrating with web forms etc., designed to achieve more flexible attribute sourcing.

Features
........

* Define data schema as class definition.
* Supply data inputs by keyword arguments, dict, or both.
* Convert and validate data inputs with user defined methods or built-in integration with 3rd party libraries.
* Access validated data as attributes / mapping.
* Easy to hook your functions on validation.

Simple usage
------------

Primitive demo:: 

    >>> from froshki import Froshki, Attribute
    >>>
    >>> class ResourceId(Attribute):
    ...     @classmethod
    ...     def transform(klass, input_value):
    ...         return int(input_value)
    ...     @classmethod
    ...     def validate(klass, input_value):
    ...         if input_value in (1,5,7,9):
    ...             return True, input_value
    ...         else:
    ...             return False, 'resource id not found'
    >>>
    >>> class Filetype(Attribute):
    ...     @classmethod
    ...     def transform(klass, input_value):
    ...         return input_value.lower()
    ...     @classmethod
    ...     def validate(klass, input_value):
    ...         if input_value in ('pdf', 'txt', 'mobi'):
    ...             return True, input_value
    ...         else:
    ...             return False, 'filetype unavailable'
    >>>
    >>> class Download(Froshki):
    ...     resource_id = ResourceId()
    ...     filetype = Filetype()
    >>>
    >>> download = Download(resource_id='9', filetype='PDF')
    >>> download.validate()
    True
    >>> download.resource_id
    9
    >>> download.filetype
    'pdf'
 
To use any functions of Froshki, extend ``froshki.Froshki`` to define data model schema.
Attributes are represented by attaching ``froshki.Attribute`` subclasses onto the model.

You can add any data conversion (``Attribute.transform``) or validation (``Attribute.validate``) methods for attributes.
``Froshki.validate`` converts and validates all attributes as defined.
But it's a bit bothersome, and you can use a built-in extension supporting attribute definition.

Using trafaret extension
------------------------

You need to pre-install `trafaret
<https://github.com/Deepwalker/trafaret>`_ to use the extension.
Usage::

    >>> from froshki import Froshki
    >>> import trafaret
    >>> from froshki.ext import trafaret_attr
    >>>
    >>> class SendInquiry(Froshki):
    ...     user_name = trafaret_attr(trafaret.String())()
    ...     user_contact = trafaret_attr(trafaret.Email())()
    ...     message = trafaret_attr(trafaret.String(regex=r'\w{10,400}'))()
    >>>
    >>> send_inquiry = SendInquiry(
    ...     user_name='yu mat', user_contact='drowse314@gmail.com',
    ...     message='cannot post messages to my group'
    ... )
    >>> send_inquiry.validate()
    True

If you prefer other validation libraries,
you will find it so easy to extend ``froshki.Attribute.validate``.
Or some more libraries are built-in supported:

* `voluptuous <https://github.com/alecthomas/voluptuous>`_

See ``froshki/ext/*_attr.py`` for documentation or details of extension wrinting.

Other features
--------------

Data as mappings
................

Some utility properties are available for accessing validated data::

    (...)
    >>> send_inquiry.data
    {'user_name': 'yu mat', 'user_contact': 'drowse314@gmail.com', 'message': 'cannot post messages to my group'}
    >>> send_inquiry.errors  # error messages are registered if validation failed
    {}

Further, you can initialize ``froshki.Froshki`` with mappings::

    (...)
    >>> data = {'user_name': 'ymat', 'user_contact': 'drowse314.gmail.com', 'message': 'cannot post messages to my group'}
    >>> another_inquiry = SendInquiry(source=data)
    >>> another_inquiry.validate()
    False

Source attributes with alias names
..................................

You can use the names differring from the class attribute names for sourcing attributes::

    >>> class ResourceAccess(Froshki):
    ...     resource_id = Attribute()
    ...     user_id = Attribute()
    ...     resource_key = Attribute(key_alias='password')
    >>> access = ResourceAccess(resource_id='1276', user_id='ymat', password='VXFPF93')
    >>> access.resource_key
    'VXFPF93'

Extra validation
................

You can add attribute dependent extra validator methods for attribute relations etc., using ``validation_hook`` decorator::

    >>> from froshki import Froshki, Attribute, validation_hook
    >>>
    >>> class SendInquiry(Froshki):
    ...     user_name = Attribute()
    ...     user_contact = Attribute()
    ...     user_contact_confirmation = Attribute()
    ...     message = Attribute()
    ...     @validation_hook
    ...     def confirm_email(self):
    ...         return self.user_contact == self.user_contact_confirmation
    >>>
    >>> send_inquiry = SendInquiry(
    ...     user_name='yu mat', user_contact='drowse314@gmail.com', user_contact_confirmation='drose@gmail.com',
    ...     message='cannot post messages to my group'
    ... )
    >>> send_inquiry.validate()
    False

If you need error information with these extra validators, extend the decorator as following::

    (...)
    >>> class SendInquiryExt(SendInquiry):
    ...     @validation_hook.extend(error='inconsistent email inputs')
    ...     def confirm_email(self):
    ...         return self.user_contact == self.user_contact_confirmation
    >>>
    >>> send_inquiry = SendInquiry(
    ...     user_name='yu mat', user_contact='drowse314@gmail.com', user_contact_confirmation='drose@gmail.com',
    ...     message='cannot post messages to my group'
    ... )
    >>> send_inquiry.validate()
    False
    >>> send_inquiry.errors
    {'confirm_email': 'inconsistent email inputs'}

Subclassing and attribute mixin
...............................

``froshki.Froshki`` subclasses are usable as base classes::

    (...)
    >>> class Resource(Froshki):
    ...     resource_id = ResourceId()
    >>>
    >>> class Download(Resource):
    ...     filetype = Filetype()
    >>>
    >>> download = Download(resource_id='9', filetype='pdf')
    >>> download.validate()
    True

Mixins are useful if you want to share some attribute definitions between schemas::

    (...)
    >>> class UserMixin(object):
    ...     user = Attribute()
    >>>
    >>> class DownloadAsUser(Download, UserMixin):
    ...     pass
    >>>
    >>> download_as_someone = DownloadAsUser(
    ...     resource_id='5', filetype='mobi',
    ...     user='ymat',
    ... )
    >>> download_as_someone.validate()
    True
    >>> download_as_someone.user
    'ymat'

You can use any classes as attribute mixins by attaching ``froshki.Attribute`` instances,
with the exception of ``froshki.Froshki`` subclass which causes MRO issue.

Other options
.............

``froshki.Froshki`` class has some useful options.

* ``Froshki.default_values``: provide attribute defaults as dict.
* ``Froshki.ignore_unkown_keys``: control if ``source`` argument accepts names that are not defined as attributes, or not (True/False).

Also some options for ``froshki.Attribute``.

* (As argument) ``Attribute(nullable=<bool>)``: allows ``None`` in validation (with any validation methods set).
