# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.admin.options import BaseModelAdmin
from django.db.models import FileField
from django.utils.safestring import mark_safe

from .settings import (ADMIN_THUMBNAIL_BACKGROUND_STYLE,
                       ADMIN_THUMBNAIL_DEFAULT_LABEL,
                       ADMIN_THUMBNAIL_FIELD_SUFFIX,
                       ADMIN_THUMBNAIL_STYLE,
                       ADMIN_THUMBNAIL_THUMBNAIL_ALIAS)
from .utils import unpack_styles


try:
    from easy_thumbnails.fields import ThumbnailerImageField
    from easy_thumbnails.alias import aliases
except ImportError:
    ThumbnailerImageField = None
    aliases = None


def thumbnail(field_name, *args, **kwargs):
    ''' admin class decorator that returns a function that accepts the admin
        class as its single argument
    '''

    ''' optional label arg '''
    try:
        label = args[0]
    except IndexError:
        label = ADMIN_THUMBNAIL_DEFAULT_LABEL

    ''' gather other arguments '''
    background = kwargs.get('background', False)
    append = kwargs.get('append', True)
    alias = kwargs.get('alias', ADMIN_THUMBNAIL_THUMBNAIL_ALIAS)

    def _model_admin_wrapper(admin_class):
        ''' validate supplied class '''
        if not issubclass(admin_class, BaseModelAdmin):
            raise ValueError(
                'admin_thumbnails: Wrapped class must be a subclass of '
                'django.contrib.admin.options.BaseModelAdmin'
            )

        ''' define the thumbnail field method using the above configuration '''
        def thumbnail_field(self, obj):
            field = obj._meta.get_field(field_name)
            field_value = getattr(obj, field_name)
            if not field_value:
                return ''

            ''' determine the image url based on the field type - in the case
                of `ThumbnailerImageField` instances, check the alias given
                against the list of available aliases from `easy_thumbnails`
            '''
            if (ThumbnailerImageField and
                    isinstance(field, ThumbnailerImageField) and
                    aliases.get(alias)):
                url = field_value[alias].url
            elif isinstance(field, FileField):
                url = field_value.url
            else:
                raise TypeError(
                    'admin_thumbnails: Specified field must be an instance of '
                    'Django’s `ImageField`, `FileField` or easy_thumbnails’ '
                    '`ThumbnailerImageField` (received: {0})'.format(
                        field.get_internal_name())
                )

            ''' generate styles and build <img> tag '''
            style = dict(ADMIN_THUMBNAIL_STYLE)
            if background:
                style.update(ADMIN_THUMBNAIL_BACKGROUND_STYLE)
            return mark_safe(
                '<img src="{0}" style="{1}" alt="Thumbnail">'.format(
                    url, unpack_styles(style))
            )
        thumbnail_field.short_description = label

        ''' augment the supplied class '''
        new_field_name = '{0}{1}'.format(field_name,
                                         ADMIN_THUMBNAIL_FIELD_SUFFIX)
        setattr(admin_class, new_field_name, thumbnail_field)
        if append:
            admin_class.readonly_fields = admin_class.readonly_fields + (new_field_name, )  # noqa: E501
        return admin_class

    return _model_admin_wrapper
