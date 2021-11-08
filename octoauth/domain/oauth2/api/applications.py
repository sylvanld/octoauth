from typing import List

from fastapi import APIRouter, Depends

from octoauth.architecture.query import Filters
from octoauth.domain.oauth2.dtos import (
    ApplicationCreateDTO,
    ApplicationReadDTO,
    ApplicationReadOnceDTO,
    ApplicationUpdateDTO,
    RedirectURIEditDTO,
    RedirectURIReadDTO,
)
from octoauth.domain.oauth2.query import parse_application_query
from octoauth.domain.oauth2.services import ApplicationService

router = APIRouter()


@router.get("/applications", response_model=List[ApplicationReadDTO])
def browse_oauth2_client_applications(filters: Filters = Depends(parse_application_query)):
    return ApplicationService.search(filters)


@router.get("/applications/{application_uid}", response_model=ApplicationReadDTO)
def get_oauth2_client_application(application_uid: str):
    return ApplicationService.find_one(uid=application_uid)


@router.post("/applications", response_model=ApplicationReadOnceDTO, status_code=201)
def create_oauth2_client_application(application_create_dto: ApplicationCreateDTO):
    return ApplicationService.create(application_create_dto)


@router.put("/applications/{application_uid}", response_model=ApplicationReadDTO)
def edit_oauth2_client_application(application_uid: str, application_create_dto: ApplicationUpdateDTO):
    return ApplicationService.update(application_uid, application_create_dto)


@router.delete("/applications/{application_uid}", status_code=202)
def get_oauth2_client_application(application_uid: str):
    return ApplicationService.delete(application_uid)


@router.get("/applications/{application_uid}/redirect_uris", response_model=List[RedirectURIReadDTO])
def get_application_authorized_redirect_uris(application_uid: str):
    return ApplicationService.get_authorized_redirect_uris(application_uid)


@router.post("/applications/{application_uid}/redirect_uris", response_model=RedirectURIReadDTO, status_code=201)
def add_authorized_redirect_uri(application_uid: str, redirect_uri_edit_dto: RedirectURIEditDTO):
    return ApplicationService.add_authorized_redirect_uri(application_uid, redirect_uri_edit_dto)


@router.put("/applications/{application_uid}/redirect_uris/{redirect_uri_uid}", response_model=RedirectURIReadDTO)
def update_authorized_redirect_uri(
    application_uid: str, redirect_uri_uid: str, redirect_uri_edit_dto: RedirectURIEditDTO
):
    return ApplicationService.update_authorized_redirect_uri(application_uid, redirect_uri_uid, redirect_uri_edit_dto)


@router.delete("/applications/{application_uid}/redirect_uris/{redirect_uri_uid}", status_code=202)
def remove_authorized_redirect_uri(application_uid: str, redirect_uri_uid: str):
    return ApplicationService.remove_authorized_redirect_uri(application_uid, redirect_uri_uid)
