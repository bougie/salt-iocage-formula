# -*- coding: utf-8 -*-
'''
Support for iocage (jails tooks on FreeBSD)
'''
from __future__ import absolute_import

# Import python libs
# import os

import logging
# Import salt libs
import salt.utils
from salt.exceptions import CommandExecutionError, SaltInvocationError

log = logging.getLogger(__name__)

__virtualname__ = 'iocage'


def __virtual__():
    '''
    Module load only if php is installed
    '''
    if salt.utils.which('iocage'):
        return __virtualname__
    else:
        return False


def _option_exists(name, **kwargs):
    '''
    Check if a given property is in the all properties list
    '''
    return name in list_properties(name, **kwargs)


def _exec(cmd, output='stdout'):
    cmd_ret = __salt__['cmd.run_all'](cmd)
    if cmd_ret['retcode'] == 0:
        return cmd_ret[output]
    else:
        raise CommandExecutionError(
            'Error in command "%s" : %s' % (cmd, str(cmd_ret)))


def _list_properties(jail_name, **kwargs):
    '''
    Returns result of iocage get all or iocage defaults (according to the
    jail name)
    '''
    if jail_name == 'defaults':
        cmd = 'iocage defaults'
    else:
        cmd = 'iocage get all %s' % (jail_name,)

    return _exec(cmd).split('\n')


def _list(option=None, **kwargs):
    '''
    Returns list of jails, templates or releases
    '''
    if option not in [None, '-t', '-r']:
        raise SaltInvocationError('Bad option name in command _list')

    cmd = 'iocage list'
    if option == '-t' or option == '-r':
        cmd = '%s %s' % (cmd, option)
    lines = _exec(cmd, **kwargs).split('\n')

    if len(lines) > 0:
        if option == '-r':
            headers = ['RELEASE']
        else:
            headers = [_ for _ in lines[0].split(' ') if len(_) > 0]

        jails = []
        if len(lines) > 1:
            for l in lines[1:]:
                jails.append({
                    headers[k]: v for k, v in enumerate([_ for _ in l.split(' ')
                                                         if len(_) > 0])
                })

        return jails
    else:
        raise CommandExecutionError(
            'Error in command "%s" : no results found' % (cmd, ))


def _display_list(items_list):
    '''
    Format display for the list of jails, templates or releases
    '''
    ret = ''

    for item in items_list:
        ret += '%s\n' % (','.join(['%s=%s' % (k, v) for k, v in item.items()]),)

    return ret


def list_jails(**kwargs):
    '''
    Get list of jails

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.list_jails
    '''
    return _display_list(_list())


def list_templates(**kwargs):
    '''
    Get list of template jails

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.list_templates
    '''
    return _display_list(_list('-t'))


def list_releases(**kwargs):
    '''
    Get list of downloaded releases

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.list_releases
    '''
    return _display_list(_list('-r'))


def list_properties(jail_name, **kwargs):
    '''
    List all properies for a given jail or defaults value

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.list_properties <jail_name>
        salt '*' iocage.list_properties defaults
    '''
    props = _list_properties(jail_name, **kwargs)

    # hack to have the same output with defaults or for a given jail
    if jail_name == 'defaults':
        return '\n'.join(props)
    else:
        return '\n'.join([_.replace(':', '=', 1) for _ in props])


def get_property(property_name, jail_name, **kwargs):
    '''
    Get property value for a given jail (or default value)

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.get_property <property> <jail_name>
        salt '*' iocage.get_property <property> defaults
    '''
    if property_name == 'all':
        return list_properties(jail_name, **kwargs)
    else:
        return _exec('iocage get %s %s' % (property_name, jail_name))


if __name__ == "__main__":
    __salt__ = ''

    import sys
    sys.exit(0)
