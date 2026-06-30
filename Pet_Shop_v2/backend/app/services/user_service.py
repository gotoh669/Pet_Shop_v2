from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.user import Permission, Role, User
from app.repositories.user_repository import UserRepository
from app.schemas.common import PageData
from app.schemas.user import PermissionPublic, RolePublic, UserAdminPublic, UserPublic


def _changes(payload: Any) -> dict[str, Any]:
    return payload.dict(exclude_unset=True)


def to_user_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        phone=user.phone,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        gender=user.gender,
        city=user.city,
        bio=user.bio,
        has_pet=bool(user.has_pet),
        pet_count=user.pet_count,
        interest_tags=user.interest_tags,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def to_user_admin_public(user: User, roles: list[Role]) -> UserAdminPublic:
    data = to_user_public(user).dict()
    return UserAdminPublic(
        **data,
        roles=[to_role_public(role) for role in roles],
        last_login_at=user.last_login_at,
    )


def to_role_public(role: Role) -> RolePublic:
    return RolePublic(
        id=role.id,
        code=role.code,
        name=role.name,
        description=role.description,
    )


def to_permission_public(permission: Permission) -> PermissionPublic:
    return PermissionPublic(
        id=permission.id,
        code=permission.code,
        name=permission.name,
        module=permission.module,
    )


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def update_profile(self, user: User, payload: Any) -> UserPublic:
        values = _changes(payload)
        if not values:
            return to_user_public(user)
        try:
            updated = self.repo.update_user(user, values)
            self.db.commit()
            self.db.refresh(updated)
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("User profile update conflicts with existing data") from exc
        return to_user_public(updated)

    def get_roles(self, user: User) -> list[RolePublic]:
        return [to_role_public(role) for role in self.repo.get_user_roles(user.id)]

    def get_permissions(self, user: User) -> list[PermissionPublic]:
        return [
            to_permission_public(permission)
            for permission in self.repo.get_user_permissions(user.id)
        ]

    def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        status: str | None = None,
    ) -> PageData:
        users, total = self.repo.list_users(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=status,
        )
        items = [
            to_user_admin_public(user, self.repo.get_user_roles(user.id))
            for user in users
        ]
        return PageData(items=items, total=total, page=page, page_size=page_size)

    def get_user_detail(self, target_user_id: int) -> UserAdminPublic:
        target_user = self.repo.get_user(target_user_id)
        if not target_user:
            raise NotFoundError("User not found")
        return to_user_admin_public(target_user, self.repo.get_user_roles(target_user.id))

    def set_user_status(
        self,
        target_user_id: int,
        status: str,
        operator: User | None = None,
    ) -> UserAdminPublic:
        if status not in {"active", "disabled"}:
            raise BadRequestError("Unsupported user status")

        target_user = self.repo.get_user(target_user_id)
        if not target_user:
            raise NotFoundError("User not found")
        if operator and operator.id == target_user.id and status == "disabled":
            raise BadRequestError("Cannot disable current user")

        target_user.status = status
        self.db.flush()
        self.db.commit()
        self.db.refresh(target_user)
        return to_user_admin_public(target_user, self.repo.get_user_roles(target_user.id))

    def update_user_roles(
        self,
        target_user_id: int,
        role_codes: list[str],
        operator: User | None = None,
    ) -> UserAdminPublic:
        target_user = self.repo.get_user(target_user_id)
        if not target_user:
            raise NotFoundError("User not found")

        unique_role_codes = list(dict.fromkeys(role_codes))
        roles = self.repo.get_roles_by_codes(unique_role_codes)
        found_codes = {role.code for role in roles}
        missing_codes = [code for code in unique_role_codes if code not in found_codes]
        if missing_codes:
            raise BadRequestError(f"Unknown role code: {', '.join(missing_codes)}")
        if not roles:
            raise BadRequestError("At least one valid role is required")

        if operator and operator.id == target_user.id:
            current_roles = self.repo.get_user_role_codes(target_user.id)
            next_roles = {role.code for role in roles}
            if "admin" in current_roles and "admin" not in next_roles:
                raise BadRequestError("Cannot remove admin role from current user")

        self.repo.replace_user_roles(target_user.id, roles)
        self.db.commit()
        self.db.refresh(target_user)
        return to_user_admin_public(target_user, self.repo.get_user_roles(target_user.id))
