# encoding: utf-8

"""
    froshki.ext.voluptuous_attr
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements froshki.Attribute extension with
    voluptuous<https://github.com/alecthomas/voluptuous> data validation library.

    :copyright: (c) 2013 by ymat<drowse314@gmail.com>.
    :license: BSD, see LICENSE for more details.
"""

try:
    import voluptuous
except ImportError:
    raise ImportError('voluptuous is not installed')
from froshki import Attribute


class VoluptuousPoweredAttribute(Attribute):
    """
    froshki.Attribute subclass using voluptuous validation
    callable.

    classmethod validate(klass, input_value) is used for handling
    voluptuous validation, which is to be non-overridable.
    """

    schema = voluptuous.Schema(voluptuous.Any())

    @classmethod
    def validate(klass, input_value):
        try:
            validated = klass.schema(input_value)
            return True, validated
        except voluptuous.Invalid as err:
            return False, err.msg


def voluptuous_attr(voluptuous_schema, name='VoluptuousAttribute'):
    """
    voluptuous_attr(voluptuous_schema) -> VoluptuousPoweredAttribute subclass.

    VoluptuousPoweredAttribute subclass factory.
    Usage:
    >>> from voluptuous import Schema, All, Length, Range
    >>> from froshki import Froshki, validation_hook
    >>> class CloneRepo(Froshki):
    ...     repo_name = voluptuous_attr(Schema(str))()
    ...     commit_id = voluptuous_attr(Schema(All(str, Length(min=7, max=7))))()
    ...     trial_limit = voluptuous_attr(Schema(All(int, Range(min=1))))()
    ...     readonly = voluptuous_attr(Schema(bool))()
    ...     user_id = voluptuous_attr(Schema(str))(nullable=True)
    ...     password = voluptuous_attr(Schema(str))(nullable=True)
    ...     @validation_hook
    ...     def auth(self):
    ...         if self.readonly:
    ...             return True
    ...         else:
    ...             pwmap = {'ymat': 'vvvv'}
    ...             return pwmap[self.user_id] == self.password
    >>>
    >>> clone_repo = CloneRepo(
    ...     repo_name='froshki', commit_id='c0b89cd',
    ...     trial_limit=3,
    ...     readonly=False,
    ...     user_id='ymat', password='vvvv'
    ... )
    >>> clone_repo.validate()
    True
    """
    return type(
        name, (VoluptuousPoweredAttribute,),
        dict(
            schema=voluptuous_schema,
        ),
    )
