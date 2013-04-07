# encoding: utf-8


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
    """

    default_values = {}

    def __new__(klass, *args, **kwargs):
        attr_names = []
        class_dict = klass.__dict__
        if '_registered_attrs' not in class_dict:
            for name in class_dict:
                obj = class_dict[name]
                if isinstance(obj, Attribute):
                    attr_names.append(name)
                    attr_descriptor = AttributeDescriptor(
                        name, obj,
                    )
                    setattr(klass, name, attr_descriptor)
            setattr(klass, '_registered_attrs', tuple(attr_names))
        instance = object.__new__(klass)
        return instance

    def __init__(self, source=None, **init_attrs):
        self._data = {}
        # Attribute values' overwrites are ordered
        # by asccending assignment-style explicity.
        self._attrs_default()
        if source is not None:
            self._attrs_from_source(source)
        self._overwrite_kw_attrs(init_attrs)
        # For Validation.
        self._is_valid = True
        self._yet_to_validate = set(self._registered_attrs)
        self._errors = {}

    @property
    def errors(self):
        return self._errors.copy()

    def _attrs_default(self):
        self._update_attrs(self.__class__.default_values)

    def _attrs_from_source(self, attr_source):
        self._update_attrs(attr_source)

    def _overwrite_kw_attrs(self, init_attrs):
        self._update_attrs(init_attrs)

    def _update_attrs(self, attr_source):
        registered_attrs = self._registered_attrs
        for name in attr_source:
            if name not in registered_attrs:
                raise TypeError(
                    "'{klass}' has no attirbute {attr}".format(
                        klass=self.__class__.__name__,
                        attr=name,
                    )
                )
            else:
                self._set_attr_data(name, attr_source[name])

    def _set_attr_data(self, name, input_value):
        self._data[name] = input_value

    def validate(self, hu=False):
        """
        Validate input/stored values -> boolean.

        Also store error messages if input is invalid.
        """
        is_valid = self._is_valid
        for attr_name in self._yet_to_validate:
            attr_is_valid, value_to_store = self._validate_attr_data(attr_name)
            self._set_attr_validation_data(
                attr_name, attr_is_valid, value_to_store
            )
            is_valid &= attr_is_valid
        self._is_valid = is_valid
        self._yet_to_validate.clear()
        return is_valid

    def _validate_attr_data(self, attr_name):
        attr_obj = getattr(self.__class__, attr_name)
        return attr_obj._validate(self._data[attr_name])

    def _set_attr_validation_data(self, attr_name,
                                  attr_is_valid, value_to_store):
        if attr_is_valid:
            self._errors.pop(attr_name, None)
            self._data[attr_name] = value_to_store
        else:
            self._errors[attr_name] = value_to_store


class Attribute(object):
    """
    Base class for Froshki objects' attributes.
    """

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

    def __get__(self, instance, klass):
        if not instance:
            return self._attr
        else:
            return instance._data.get(self._attr_name, None)

    def __set__(self, instance, value):
        if not instance:
            return object.__set__(self, instance, value)
        else:
            self._set_data(instance, value)

    def _set_data(self, froshki, input_value):
        attr_name = self._attr_name
        froshki._data[attr_name] = input_value
        froshki._yet_to_validate.add(attr_name)
