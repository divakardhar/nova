# Copyright 2013 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from webob import exc

from nova.api.openstack import extensions
from nova import exception
from nova.i18n import _
from nova.openstack.common import strutils
from nova import utils

ALIAS = "os-multiple-create"
MIN_ATTRIBUTE_NAME = "%s:min_count" % ALIAS
MAX_ATTRIBUTE_NAME = "%s:max_count" % ALIAS
RRID_ATTRIBUTE_NAME = "%s:return_reservation_id" % ALIAS


class MultipleCreate(extensions.V3APIExtensionBase):
    """Allow multiple create in the Create Server v3 API."""

    name = "MultipleCreate"
    alias = ALIAS
    version = 1

    def get_resources(self):
        return []

    def get_controller_extensions(self):
        return []

    # use nova.api.extensions.server.extensions entry point to modify
    # server create kwargs
    def server_create(self, server_dict, create_kwargs):
        # min_count and max_count are optional.  If they exist, they may come
        # in as strings.  Verify that they are valid integers and > 0.
        # Also, we want to default 'min_count' to 1, and default
        # 'max_count' to be 'min_count'.
        min_count = server_dict.get(MIN_ATTRIBUTE_NAME, 1)
        max_count = server_dict.get(MAX_ATTRIBUTE_NAME, min_count)
        return_id = server_dict.get(RRID_ATTRIBUTE_NAME, False)

        try:
            min_count = utils.validate_integer(min_count,
                                               "min_count", min_value=1)
            max_count = utils.validate_integer(max_count,
                                               "max_count", min_value=1)
            return_id = strutils.bool_from_string(return_id, strict=True)
        except exception.InvalidInput as e:
            raise exc.HTTPBadRequest(explanation=e.format_message())

        if min_count > max_count:
            msg = _('min_count must be <= max_count')
            raise exc.HTTPBadRequest(explanation=msg)

        create_kwargs['min_count'] = min_count
        create_kwargs['max_count'] = max_count
        create_kwargs['return_reservation_id'] = return_id
