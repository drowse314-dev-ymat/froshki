# encoding: utf-8

"""
    froshki.model
    ~~~~~~~~~~~~~

    Implements model bases for froshki functionalities.

    :copyright: (c) 2013 by ymat<drowse314@gmail.com>.
    :license: BSD, see LICENSE for more details.
"""


class Attribute(object):
    """
    Base class for Froshki objects' attributes.
    """

    def __init__(self, nullable=False, key_alias=None):
        self._nullable = nullable
        self._key_alias = key_alias

    @property
    def nullable(self):
        return self._nullable

    @property
    def key_alias(self):
        return self._key_alias

    @classmethod
    def transform(klass, input_value):
        """
        Transform input values to store into Froshki._data.

        klass.transform(input_value) -> value_to_store
        Override this method for customization.
        """
        return input_value

    @classmethod
    def validate(klass, input_value):
        """
        Validate input values to store into Froshki._data.

        klass.validate(input_value)
            -> True, input_value
        or
            -> False, error_message
        Override this method for customization.
        """
        return True, input_value

    @classmethod
    def _validate(klass, input_value):
        """Validation hook for Froshki object."""
        try:
            value_to_store = klass.transform(input_value)
        except:
            return False, 'data conversion error: {}'.format(input_value)
        return klass.validate(value_to_store)


class AttributeDescriptor(object):
    """
    Abstracts attribute access to Froshki objects.
    """

    def __init__(self, attr_name, attr_obj):
        self._attr_name = attr_name
        self._attr = attr_obj

    @property
    def attr_key_alias(self):
        return self._attr.key_alias

    def __get__(self, instance, klass):
        if not instance:
            return self._attr
        else:
            return instance._get_attr_data(self._attr_name)

    def __set__(self, instance, value):
        if not instance:
            pass
        else:
            self._set_data(instance, value)

    def _set_data(self, froshki, input_value):
        attr_name = self._attr_name
        froshki._set_attr_data(attr_name, input_value)


class ValidatorMethod(object):
    """
    Decorates a method to register as an extra/attr-relation validator.

    Hooked validation occurs after per-attribute validations are finished.
    Example usage:
    >>> class ModifyPassword(Froshki):
    ...     user_id = Attribute()
    ...     old_password = Attribute()
    ...     new_password = Attribute()
    ...     confirm_new_password = Attribute()
    ...     @validation_hook
    ...     def confirm_password(self):  # Taken as (unbound) function.
    ...         '''validator_method(<Froshki object>) -> boolean.'''
    ...         if self.new_password == self.confirm_new_password:
    ...             return True
    ...         else:
    ...             return False
    >>>
    >>> modify_password = ModifyPassword(user_id='ymat', old_password='vxf', new_password='f8a73', confirm_new_password='f8a773')
    >>> modify_password.validate()
    False
    """

    def __init__(self, validator_method, error=None):
        self._validator = validator_method
        self._error = error

    @property
    def error(self):
        return self._error

    def validate(self, attr_name, froshki):
        return self._validator(froshki)

    @classmethod
    def extend(klass, error=None):
        def _validation_hook(validator_method):
            return klass(
                validator_method,
                error=error,
            )
        return _validation_hook

validation_hook = ValidatorMethod


class Froshki(object):
    """
    Base class for Froshki objetcs.

    Basic usage:
    >>> # Define attribute types.
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
    >>> class Filetype(Attribute):
    ...     @classmethod
    ...     def validate(klass, input_value):
    ...         if input_value in ('pdf', 'txt', 'mobi'):
    ...             return True, input_value
    ...         else:
    ...             return False, 'filetype unavailable'
    >>> # Attach to Froshki subclass.
    >>> class Download(Froshki):
    ...     resource_id = ResourceId()
    ...     filetype = Filetype()
    >>>
    >>> download = Download(resource_id='9', filetype='pdf')
    >>> download.validate()  # Must be called for data transformation or validation.
    True
    >>> download.resource_id
    9
    >>> download.filetype
    'pdf'
    >>>
    >>> # Attribute mixin.
    >>> class UserMixin(object):
    ...     user = Attribute()
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
    """

    default_values = {}
    ignore_unknown_keys = False

    _attribute_class = Attribute
    _descriptor_class = AttributeDescriptor

    def __new__(klass, *args, **kwargs):

        attr_names, attr_aliases = klass.find_attributes()
        inherited_attrs, inherited_aliases = klass.find_attributes_in_bases()
        attr_names.extend(inherited_attrs)
        attr_aliases.update(inherited_aliases)
        setattr(klass, '_registered_attrs', tuple(attr_names))
        setattr(klass, '_attr_aliases', attr_aliases)

        extra_validators = klass.find_extra_validators()
        setattr(klass, '_extra_validators', tuple(extra_validators))

        instance = object.__new__(klass)
        return instance

    @classmethod
    def find_attributes(klass):
        attr_names = []
        attr_aliases = {}
        class_dict = klass.__dict__
        attribute_class = klass._attribute_class
        descriptor_class = klass._descriptor_class
        for name in class_dict:
            obj = class_dict[name]
            if isinstance(obj, attribute_class):
                attr_names.append(name)
                attr_descriptor = descriptor_class(
                    name, obj,
                )
                setattr(klass, name, attr_descriptor)
                if obj.key_alias is not None:
                    attr_aliases[obj.key_alias] = name
            elif isinstance(obj, descriptor_class):
                # Only when modified after declaration.
                attr_names.append(name)
                if obj.attr_key_alias is not None:
                    attr_aliases[obj.attr_key_alias] = name
        return attr_names, attr_aliases

    @classmethod
    def find_attributes_in_bases(klass):
        attr_names = []
        attr_aliases = {}
        attribute_class = klass._attribute_class
        descriptor_class = klass._descriptor_class
        for base in klass.mro()[1:]:
            base_dict = base.__dict__
            for name in base_dict:
                obj = base_dict[name]
                if isinstance(obj, attribute_class):
                    attr_names.append(name)
                    attr_descriptor = descriptor_class(
                        name, obj,
                    )
                    # No modifications to the base class.
                    setattr(klass, name, attr_descriptor)
                    if obj.key_alias is not None:
                        attr_aliases[obj.key_alias] = name
                # Also capture `descriptor_class` instances, for the cases when its bases
                # have been instantiated before subclassed.
                elif isinstance(obj, descriptor_class):
                    attr_names.append(name)
                    if obj.attr_key_alias is not None:
                        attr_aliases[obj.attr_key_alias] = name
        return attr_names, attr_aliases

    @classmethod
    def find_extra_validators(klass):
        class_dict = klass.__dict__
        extra_validators = []
        for name in class_dict:
            obj = class_dict[name]
            if isinstance(obj, ValidatorMethod):
                extra_validators.append(name)
        return extra_validators

    def __init__(self, source=None, ignore_unknown_keys=None,
                 **init_attrs_by_kws):
        self._data = {}
        # Override class attribute.
        if ignore_unknown_keys is not None:
            self.ignore_unknown_keys = ignore_unknown_keys
        # Attribute values' overwrites are ordered
        # by asccending assignment-style explicity.
        self._source_attr_defaults()
        if source is not None:
            self._init_attrs(
                source,
                ignore_unknown_keys=self.ignore_unknown_keys,
            )
        self._init_attrs(init_attrs_by_kws)
        # For validation.
        self._yet_to_validate = set(self._registered_attrs)
        self._errors = {}

    @property
    def errors(self):
        return self._errors.copy()

    @property
    def data(self):
        return self._data.copy()

    def _source_attr_defaults(self):
        self._init_attrs(self.__class__.default_values)

    def _init_attrs(self, attr_source, ignore_unknown_keys=False):
        registered_attrs = self._registered_attrs
        attr_aliases = self._attr_aliases
        for name in attr_source:
            if name in registered_attrs:
                self._set_attr_data(
                    name, attr_source[name],
                    mark_as_unvalidated=False,
                )
            elif name in attr_aliases:
                self._set_attr_data(
                    attr_aliases[name], attr_source[name],
                    mark_as_unvalidated=False,
                )
            elif not ignore_unknown_keys:
                raise TypeError(
                    "'{klass}' has no attirbute {attr}".format(
                        klass=self.__class__.__name__,
                        attr=name,
                    )
                )

    def _set_attr_data(self, name, input_value,
                       mark_as_unvalidated=True):
        self._data[name] = input_value
        if mark_as_unvalidated:
            self._yet_to_validate.add(name)

    def _get_attr_data(self, name):
        return self._data.get(name, None)

    def validate(self):
        """
        Validate input/stored values -> boolean.

        Also store error messages if input is invalid.
        """
        is_valid = True
        yet_to_validate = self._yet_to_validate
        yet_to_validate.update(set(self.errors))
        for attr_name in yet_to_validate:
            attr_is_valid, value_to_store = self._validate_attr_data(attr_name)
            self._set_attr_validation_data(
                attr_name, attr_is_valid, value_to_store
            )
            is_valid &= attr_is_valid
        for validator_name in self._extra_validators:
            is_valid &= self._handle_validation_hook(validator_name)
        self._yet_to_validate.clear()
        return is_valid

    def _validate_attr_data(self, attr_name):
        attr_obj = getattr(self.__class__, attr_name)
        attr_data = self._data.get(attr_name, None)
        if attr_obj.nullable and attr_data is None:
            return True, attr_data
        return attr_obj._validate(attr_data)

    def _set_attr_validation_data(self, attr_name,
                                  attr_is_valid, value_to_store):
        if attr_is_valid:
            self._errors.pop(attr_name, None)
            self._data[attr_name] = value_to_store
        else:
            self._errors[attr_name] = value_to_store

    def _handle_validation_hook(self, validator_name):
        self._errors.pop(validator_name, None)
        validator = getattr(self, validator_name)
        is_valid = validator.validate(
            validator_name, self
        )
        if not is_valid and validator.error is not None:
            self._errors[validator_name] = validator.error
        return is_valid
