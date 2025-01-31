# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.api_core import exceptions
from google.api_core import retry
from google.auth import exceptions as auth_exceptions
import requests.exceptions


_RETRYABLE_REASONS = frozenset(
    ["rateLimitExceeded", "backendError", "internalError", "badGateway"]
)

_UNSTRUCTURED_RETRYABLE_TYPES = (
    ConnectionError,
    exceptions.TooManyRequests,
    exceptions.InternalServerError,
    exceptions.BadGateway,
    requests.exceptions.ChunkedEncodingError,
    requests.exceptions.ConnectionError,
    auth_exceptions.TransportError,
)


def _should_retry(exc):
    """Predicate for determining when to retry.

    We retry if and only if the 'reason' is 'backendError'
    or 'rateLimitExceeded'.
    """
    if not hasattr(exc, "errors") or len(exc.errors) == 0:
        # Check for unstructured error returns, e.g. from GFE
        return isinstance(exc, _UNSTRUCTURED_RETRYABLE_TYPES)

    reason = exc.errors[0]["reason"]
    return reason in _RETRYABLE_REASONS


DEFAULT_RETRY = retry.Retry(predicate=_should_retry, deadline=600.0)
"""The default retry object.

Any method with a ``retry`` parameter will be retried automatically,
with reasonable defaults. To disable retry, pass ``retry=None``.
To modify the default retry behavior, call a ``with_XXX`` method
on ``DEFAULT_RETRY``. For example, to change the deadline to 30 seconds,
pass ``retry=bigquery.DEFAULT_RETRY.with_deadline(30)``.
"""
