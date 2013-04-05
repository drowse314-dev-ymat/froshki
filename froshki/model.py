# encoding: utf-8


class Froshki(object):
    """
    Base class for Froshki objetcs.
    """

    default_values = {}

    def __new__(klass, *args, **kwargs):
        attr_names = []
        class_dict = klass.__dict__
        for name in class_dict:
            attr_names.append(name)
            obj = class_dict[name]
            if isinstance(obj, Attribute):
                attr_descriptor = AttributeDescriptor(
                    name, obj,
                )
                setattr(klass, name, attr_descriptor)
        instance = object.__new__(klass)
        instance._registered_attrs = attr_names
        return instance

    def __init__(self, source=None, **init_attrs):
        self._data = {}
        # Attribute values' overwrites are ordered
        # by asccending assignment-style explicity.
        self._attrs_default()
        if source is not None:
            self._attrs_from_source(source)
        self._overwrite_kw_attrs(init_attrs)

    def _attrs_default(self):
        self._update_attrs(self.__class__.default_values)

    def _attrs_from_source(self, attr_source):
        self._update_attrs(attr_source)

    def _overwrite_kw_attrs(self, init_attrs):
        self._update_attrs(init_attrs)

    def _update_attrs(self, attr_source):
        for name in attr_source:
            if name not in self._registered_attrs:
                raise TypeError(
                    "'{klass}' has no attirbute {attr}".format(
                        klass=self.__class__.__name__,
                        attr=name,
                    )
                )
            else:
                self._set_attr_data(name, attr_source[name])

    def _set_attr_data(self, name, input_value):
        attr_obj = getattr(self.__class__, name)
        input_value = attr_obj.transform(input_value)
        self._data[name] = input_value


class Attribute(object):
    """
    Base class for Froshki objects' attributes.
    """

    @classmethod
    def transform(klass, input_value):
        """
        Transform input values to store into Froshki_data.


        Override this method for customization.
        """
        return input_value


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
        attr_obj = self._attr
        input_value = attr_obj.transform(input_value)
        froshki._data[self._attr_name] = input_value
