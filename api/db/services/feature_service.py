#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import hashlib
from datetime import datetime

import peewee
from werkzeug.security import generate_password_hash, check_password_hash

from api.db import UserTenantRole
from api.db.db_models import DB, UserTenant
from api.db.db_models import User, Tenant
from api.db.services.common_service import CommonService
from api.utils import get_uuid, current_timestamp, datetime_format
from api.db import StatusEnum
from rag.settings import MINIO


class FeatureService(CommonService):
    """Service class for managing feature-related database operations.
    
    This class extends CommonService to provide specialized functionality for well's feature management,
    including add, delete, update, and query operations.

    
    Attributes:
        model: The Feature model class for database operations.
    """
    model = Feature

    @classmethod
    @DB.connection_context()
    def filter_by_well_id(cls, well_id):   #query
        """Retrieve a feature list by their well ID.
        
        Args:
            well_id: The unique identifier of the well.
            
        Returns:
            Feature object if found, None otherwise.
        """
        try:
            feature = cls.model.select().where(cls.model.well_id == well_id).get()
            return feature
        except peewee.DoesNotExist:
            return None

    @classmethod
    @DB.connection_context()
    def filter_by_doc_id(cls, doc_id):   #query
        try:
            feature = cls.model.select().where(cls.model.document_id == doc_id).get()
            return feature
        except peewee.DoesNotExist:
            return None
        
    @classmethod
    @DB.connection_context()    #add
    def save(cls, **kwargs):
        kwargs["create_time"] = current_timestamp()
        kwargs["create_date"] = datetime_format(datetime.now())
        kwargs["update_time"] = current_timestamp()
        kwargs["update_date"] = datetime_format(datetime.now())
        obj = cls.model(**kwargs).save(force_insert=False)
        return obj

    @classmethod
    @DB.connection_context()
    def delete_by_doc_id(cls, doc_ids):            #soft delete
        with DB.atomic():
            cls.model.update({"status": 0}).where(
                cls.model.document_id.in_(doc_ids)).execute()

    @classmethod
    @DB.connection_context()                         #update
    def update_by_doc_id(cls, doc_id, feature_dict):
        with DB.atomic():
            if feature_dict:
                feature_dict["update_time"] = current_timestamp()
                feature_dict["update_date"] = datetime_format(datetime.now())
                cls.model.update(feature_dict).where(
                    cls.model.document_id == doc_id).execute()