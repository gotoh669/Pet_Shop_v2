from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine
from app.models import Permission, Role, RolePermission, User, UserRole


ROLE_DEFINITIONS = [
    ("user", "普通用户", "Pet owner or future pet owner"),
    ("merchant", "商家", "Product seller or service provider"),
    ("admin", "管理员", "Platform administrator"),
]

PERMISSION_DEFINITIONS = [
    ("pet_profile:manage", "管理宠物档案", "pet_profile"),
    ("product:view", "浏览商品", "mall"),
    ("cart:manage", "管理购物车", "mall"),
    ("order:create", "创建订单", "mall"),
    ("post:create", "发布社区动态", "community"),
    ("adoption:apply", "提交领养申请", "adoption"),
    ("pet_coin:view", "查看宠物币流水", "pet_coin"),
    ("product:manage", "管理商品", "merchant"),
    ("order:ship", "订单发货", "merchant"),
    ("user:manage", "管理用户", "admin"),
    ("product:audit", "审核商品", "admin"),
    ("post:audit", "审核社区内容", "admin"),
    ("adoption:audit", "审核领养信息", "admin"),
    ("order:view", "查看订单", "admin"),
]

ROLE_PERMISSIONS = {
    "user": [
        "pet_profile:manage",
        "product:view",
        "cart:manage",
        "order:create",
        "post:create",
        "adoption:apply",
        "pet_coin:view",
    ],
    "merchant": [
        "product:manage",
        "order:ship",
    ],
    "admin": [
        "user:manage",
        "product:audit",
        "post:audit",
        "adoption:audit",
        "order:view",
        "pet_coin:view",
    ],
}


def init_database() -> None:
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        seed_roles_and_permissions(db)
        seed_default_admin(db)


def seed_roles_and_permissions(db: Session) -> None:
    roles_by_code: dict[str, Role] = {}
    permissions_by_code: dict[str, Permission] = {}

    for code, name, description in ROLE_DEFINITIONS:
        role = db.scalar(select(Role).where(Role.code == code))
        if not role:
            role = Role(code=code, name=name, description=description)
            db.add(role)
            db.flush()
        roles_by_code[code] = role

    for code, name, module in PERMISSION_DEFINITIONS:
        permission = db.scalar(select(Permission).where(Permission.code == code))
        if not permission:
            permission = Permission(code=code, name=name, module=module)
            db.add(permission)
            db.flush()
        permissions_by_code[code] = permission

    for role_code, permission_codes in ROLE_PERMISSIONS.items():
        role = roles_by_code[role_code]
        for permission_code in permission_codes:
            permission = permissions_by_code[permission_code]
            exists = db.get(
                RolePermission,
                {"role_id": role.id, "permission_id": permission.id},
            )
            if not exists:
                db.add(RolePermission(role_id=role.id, permission_id=permission.id))

    db.commit()


def seed_default_admin(db: Session) -> None:
    if not settings.default_admin_phone:
        return

    admin_role = db.scalar(select(Role).where(Role.code == "admin"))
    if not admin_role:
        return

    user = db.scalar(select(User).where(User.phone == settings.default_admin_phone))
    if not user:
        user = User(
            phone=settings.default_admin_phone,
            nickname="平台管理员",
            status="active",
        )
        db.add(user)
        db.flush()

    exists = db.get(UserRole, {"user_id": user.id, "role_id": admin_role.id})
    if not exists:
        db.add(UserRole(user_id=user.id, role_id=admin_role.id))

    db.commit()
