# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

RESPONSE_ERR = 1
RESPONSE_OK = 0
RESPONSE_NONE = -1


class BaseResponse(object):
    """
    Base response class
    """

    def __init__(self, dic: dict):
        """
        init
        :param dic:
        """
        self.__errcode = dic.get('errcode', RESPONSE_NONE)
        self.__message = dic.get('message', "")

    @property
    def errcode(self) -> int:
        """
        get error code
        :return:
        """
        return self.__errcode

    @property
    def message(self) -> str:
        """
        get message
        :return:
        """
        return self.__message
