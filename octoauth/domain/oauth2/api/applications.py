from typing import List

from fastapi import APIRouter

from octoauth.domain.oauth2.dtos import ApplicationCreateDTO, ApplicationReadDTO
from octoauth.domain.oauth2.services import ApplicationService

router = APIRouter()


@router.get("/applications", response_model=List[ApplicationReadDTO])
def browse_oauth2_client_applications():
    return ApplicationService.search()


@router.get("/applications/{application_uid}", response_model=ApplicationReadDTO)
def get_oauth2_client_application(application_uid: str):
    return ApplicationService.find_one(uid=application_uid)


@router.post("/applications", response_model=ApplicationReadDTO, status_code=201)
def create_oauth2_client_application(application_create_dto: ApplicationCreateDTO):
    return ApplicationService.create(application_create_dto)


@router.put("/applications/{application_uid}", response_model=ApplicationReadDTO)
def edit_oauth2_client_application(application_uid: str, application_create_dto: ApplicationCreateDTO):
    return ApplicationService.update(application_uid, application_create_dto)


@router.delete("/applications/{application_uid}", status_code=202)
def get_oauth2_client_application(application_uid: str):
    return ApplicationService.delete(application_uid)
