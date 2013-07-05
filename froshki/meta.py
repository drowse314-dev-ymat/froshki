# encoding: utf-8

"""
    froshki.meta
    ~~~~~~~~~~~~

    Implements metaprogramming features for froshki.

    :copyright: (c) 2013 by ymat<drowse314@gmail.com>.
    :license: BSD, see LICENSE for more details.
"""


def with_metaclass(meta, bases=(object, )):
    return meta('NewBase', bases, {})


class Prebuilt(type):
    """
    Metaclass for instantiating the class once right after the definition time.

    Given the `TargetClass`, `TargetClass.prebuild_args` and
    `TargetClass.prebuild_kwargs` are available for explicitly passing
    the arguments in the automatic instantiation.
    """

    def __new__(klass, name, bases, attrs):
        new_class = type.__new__(klass, name, bases, attrs)
        prebuild_args = attrs.get('prebuild_args', [])
        prebuild_kwargs = attrs.get('prebuild_kwargs', {})
        instance = new_class(*prebuild_args, **prebuild_kwargs)
        return new_class
