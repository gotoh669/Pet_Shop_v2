from datetime import datetime
from typing import Any, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.user import Permission, Role, RolePermission, SmsCode, User, UserRole


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_user_by_phone(self, phone: str) -> Optional[User]:
        return self.db.scalar(select(User).where(User.phone == phone))

    def create_user(
        self,
        phone: str,
        nickname: str,
        password_hash: Optional[str] = None,
    ) -> User:
        user = User(
            phone=phone,
            password_hash=password_hash,
            nickname=nickname,
            status="active",
        )
        self.db.add(user)
        self.db.flush()
        return user

    def update_user(self, user: User, values: dict[str, Any]) -> User:
        for key, value in values.items():
            setattr(user, key, value)
        self.db.flush()
        return user

    def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[User], int]:
        stmt = select(User)
        count_stmt = select(func.count()).select_from(User)

        conditions = []
        if keyword:
            pattern = f"%{keyword}%"
            conditions.append(or_(User.phone.like(pattern), User.nickname.like(pattern)))
        if status:
            conditions.append(User.status == status)

        for condition in conditions:
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        total = self.db.scalar(count_stmt) or 0
        users = list(
            self.db.scalars(
                stmt.order_by(User.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return users, total

    def grant_role_if_exists(self, user_id: int, role_code: str) -> None:
        role = self.db.scalar(select(Role).where(Role.code == role_code))
        if not role:
            return

        exists = self.db.get(UserRole, {"user_id": user_id, "role_id": role.id})
        if exists:
            return

        self.db.add(UserRole(user_id=user_id, role_id=role.id))
        self.db.flush()

    def get_roles_by_codes(self, role_codes: list[str]) -> list[Role]:
        if not role_codes:
            return []
        stmt = select(Role).where(Role.code.in_(role_codes)).order_by(Role.id)
        return list(self.db.scalars(stmt))

    def replace_user_roles(self, user_id: int, roles: list[Role]) -> None:
        existing_stmt = select(UserRole).where(UserRole.user_id == user_id)
        for user_role in self.db.scalars(existing_stmt):
            self.db.delete(user_role)

        self.db.flush()
        for role in roles:
            self.db.add(UserRole(user_id=user_id, role_id=role.id))
        self.db.flush()

    def get_user_roles(self, user_id: int) -> list[Role]:
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .order_by(Role.id)
        )
        return list(self.db.scalars(stmt))

    def get_user_permissions(self, user_id: int) -> list[Permission]:
        role_ids_stmt = select(UserRole.role_id).where(UserRole.user_id == user_id)
        stmt = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id.in_(role_ids_stmt))
            .order_by(Permission.module, Permission.code)
            .distinct()
        )
        return list(self.db.scalars(stmt))

    def get_user_role_codes(self, user_id: int) -> set[str]:
        return {role.code for role in self.get_user_roles(user_id)}

    def get_user_permission_codes(self, user_id: int) -> set[str]:
        return {permission.code for permission in self.get_user_permissions(user_id)}

    def list_roles(self) -> list[Role]:
        return list(self.db.scalars(select(Role).order_by(Role.id)))

    def list_permissions(self) -> list[Permission]:
        return list(self.db.scalars(select(Permission).order_by(Permission.module, Permission.code)))

    def create_sms_code(
        self,
        phone: str,
        code: str,
        expires_at: datetime,
        purpose: str = "login",
    ) -> SmsCode:
        sms_code = SmsCode(
            phone=phone,
            code=code,
            purpose=purpose,
            status="active",
            expires_at=expires_at,
        )
        self.db.add(sms_code)
        self.db.flush()
        return sms_code

    def expire_active_sms_codes(self, phone: str, purpose: str = "login") -> None:
        stmt = select(SmsCode).where(
            SmsCode.phone == phone,
            SmsCode.purpose == purpose,
            SmsCode.status == "active",
        )
        for sms_code in self.db.scalars(stmt):
            sms_code.status = "expired"
        self.db.flush()

    def get_latest_active_sms_code(self, phone: str, purpose: str = "login") -> Optional[SmsCode]:
        stmt = (
            select(SmsCode)
            .where(
                SmsCode.phone == phone,
                SmsCode.purpose == purpose,
                SmsCode.status == "active",
            )
            .order_by(SmsCode.id.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
