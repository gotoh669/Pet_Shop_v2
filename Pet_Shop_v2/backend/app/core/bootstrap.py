from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine
from app.models import LivePet, Permission, PetProfile, Product, ProductCategory, Role, RolePermission, User, UserRole


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

CATEGORY_DEFINITIONS = [
    ("宠物食品", 10),
    ("宠物零食", 20),
    ("玩具用品", 30),
    ("清洁护理", 40),
    ("日用出行", 50),
    ("宠物服饰", 60),
    ("药品保健", 70),
]

DEMO_PRODUCTS = [
    {
        "category": "宠物食品",
        "title": "鲜肉冻干双拼猫粮",
        "subtitle": "高蛋白配方，适合成猫日常主粮",
        "brand": "PawFresh",
        "price": 89.90,
        "original_price": 119.00,
        "stock": 68,
        "spec": "1.5kg",
        "applicable_pet": "猫",
        "tags": ["猫粮", "冻干", "主粮"],
        "detail": "鸡肉、鱼肉冻干双拼，颗粒适中，适合成猫日常喂养。",
    },
    {
        "category": "宠物零食",
        "title": "低温烘焙鸡肉粒",
        "subtitle": "训练奖励零食，少盐无香精",
        "brand": "TailJoy",
        "price": 29.90,
        "original_price": 39.90,
        "stock": 120,
        "spec": "200g",
        "applicable_pet": "猫狗通用",
        "tags": ["零食", "训练", "鸡肉"],
        "detail": "低温烘焙锁住肉香，适合作为训练奖励或日常互动零食。",
    },
    {
        "category": "玩具用品",
        "title": "耐咬洁齿发声玩具",
        "subtitle": "消耗精力，也能帮助清洁牙齿",
        "brand": "HappyPet",
        "price": 19.90,
        "original_price": 25.90,
        "stock": 86,
        "spec": "中号",
        "applicable_pet": "狗",
        "tags": ["玩具", "洁齿", "耐咬"],
        "detail": "柔韧材质，内置发声结构，适合中小型犬玩耍。",
    },
    {
        "category": "清洁护理",
        "title": "温和除臭宠物湿巾",
        "subtitle": "外出擦爪、饭后清洁都方便",
        "brand": "CleanPaw",
        "price": 16.80,
        "original_price": 22.00,
        "stock": 150,
        "spec": "80 抽",
        "applicable_pet": "猫狗通用",
        "tags": ["清洁", "湿巾", "除臭"],
        "detail": "温和配方，适合擦拭爪子、毛发和口鼻周边。",
    },
]

DEMO_LIVE_PETS = [
    {
        "pet_code": "CAT-NEKO-001",
        "display_name": "糯米",
        "pet_type": "cat",
        "breed": "布偶",
        "gender": "female",
        "color": "海双",
        "weight": 2.60,
        "city": "上海",
        "price": 3600.00,
        "vaccine_info": "已完成首免，附疫苗本",
        "deworm_info": "体内外驱虫完成",
        "description": "性格亲人，适合家庭陪伴。",
    },
    {
        "pet_code": "DOG-CORGI-001",
        "display_name": "豆包",
        "pet_type": "dog",
        "breed": "柯基",
        "gender": "male",
        "color": "黄白",
        "weight": 4.10,
        "city": "杭州",
        "price": 4200.00,
        "vaccine_info": "两针疫苗，健康检查正常",
        "deworm_info": "定期驱虫",
        "description": "活泼亲人，食欲好，适合有陪伴时间的家庭。",
    },
    {
        "pet_code": "RABBIT-LOP-001",
        "display_name": "雪球",
        "pet_type": "rabbit",
        "breed": "垂耳兔",
        "gender": "unknown",
        "color": "白色",
        "weight": 1.20,
        "city": "苏州",
        "price": 499.00,
        "vaccine_info": "基础健康检查正常",
        "deworm_info": "无需常规驱虫，按饲养建议观察",
        "description": "温顺安静，适合小宠饲养新手。",
    },
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
        ensure_runtime_schema(db)
        seed_roles_and_permissions(db)
        seed_product_categories(db)
        seed_default_admin(db)
        seed_demo_products(db)
        seed_demo_pets(db)
        seed_demo_live_pets(db)


def ensure_runtime_schema(db: Session) -> None:
    if engine.dialect.name != "sqlite":
        return

    columns = {
        row[1]
        for row in db.execute(text("PRAGMA table_info(pet_profiles)")).fetchall()
    }
    if "source_type" not in columns:
        db.execute(text("ALTER TABLE pet_profiles ADD COLUMN source_type VARCHAR(32) NOT NULL DEFAULT 'manual'"))
    if "source_live_pet_id" not in columns:
        db.execute(text("ALTER TABLE pet_profiles ADD COLUMN source_live_pet_id BIGINT NULL"))
    if "source_purchase_id" not in columns:
        db.execute(text("ALTER TABLE pet_profiles ADD COLUMN source_purchase_id BIGINT NULL"))
    db.commit()


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


def seed_product_categories(db: Session) -> None:
    for name, sort_order in CATEGORY_DEFINITIONS:
        category = db.scalar(select(ProductCategory).where(ProductCategory.name == name))
        if category:
            continue
        db.add(ProductCategory(name=name, sort_order=sort_order, status="enabled"))

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


def seed_demo_products(db: Session) -> None:
    if not table_has_columns("products", {"merchant_user_id", "category_id", "title"}):
        return

    merchant = db.scalar(select(User).where(User.phone == "16600000000"))
    if not merchant:
        merchant = User(
            phone="16600000000",
            nickname="示例宠物商家",
            status="active",
        )
        db.add(merchant)
        db.flush()

    merchant_role = db.scalar(select(Role).where(Role.code == "merchant"))
    if merchant_role:
        exists = db.get(UserRole, {"user_id": merchant.id, "role_id": merchant_role.id})
        if not exists:
            db.add(UserRole(user_id=merchant.id, role_id=merchant_role.id))

    categories = {
        category.name: category
        for category in db.scalars(select(ProductCategory)).all()
    }
    for item in DEMO_PRODUCTS:
        exists = db.scalar(select(Product).where(Product.title == item["title"]))
        if exists:
            continue
        category = categories.get(item["category"])
        if not category:
            continue
        db.add(
            Product(
                merchant_user_id=merchant.id,
                category_id=category.id,
                title=item["title"],
                subtitle=item["subtitle"],
                brand=item["brand"],
                cover_url="/static/logo.png",
                image_urls=["/static/logo.png"],
                price=item["price"],
                original_price=item["original_price"],
                stock=item["stock"],
                spec=item["spec"],
                applicable_pet=item["applicable_pet"],
                tags=item["tags"],
                detail=item["detail"],
                status="active",
                audit_note="示例商品",
            )
        )

    db.commit()


def seed_demo_pets(db: Session) -> None:
    if not table_has_columns("pet_profiles", {"user_id", "name", "visibility"}):
        return

    user = db.scalar(select(User).where(User.phone == "13800138000"))
    if not user:
        user = User(
            phone="13800138000",
            nickname="示例宠物主人",
            status="active",
            has_pet=True,
            pet_count=1,
        )
        db.add(user)
        db.flush()

    user_role = db.scalar(select(Role).where(Role.code == "user"))
    if user_role:
        exists = db.get(UserRole, {"user_id": user.id, "role_id": user_role.id})
        if not exists:
            db.add(UserRole(user_id=user.id, role_id=user_role.id))

    exists = db.scalar(select(PetProfile).where(PetProfile.user_id == user.id, PetProfile.name == "奶茶"))
    if exists:
        return

    db.add(
        PetProfile(
            user_id=user.id,
            name="奶茶",
            pet_type="cat",
            breed="英短",
            gender="female",
            weight=4.20,
            avatar_url="/static/logo.png",
            sterilized="yes",
            vaccine_status="completed",
            deworm_status="regular",
            health_notes="性格温顺，喜欢冻干零食。",
            visibility="private",
            is_current=True,
        )
    )
    user.has_pet = True
    user.pet_count = 1
    db.commit()


def seed_demo_live_pets(db: Session) -> None:
    if not table_has_columns("live_pets", {"merchant_user_id", "pet_code"}):
        return

    merchant = db.scalar(select(User).where(User.phone == "16600000000"))
    if not merchant:
        return

    for item in DEMO_LIVE_PETS:
        exists = db.scalar(select(LivePet).where(LivePet.pet_code == item["pet_code"]))
        if exists:
            continue
        db.add(
            LivePet(
                merchant_user_id=merchant.id,
                cover_url="/static/logo.png",
                image_urls=["/static/logo.png"],
                health_certificate_url="/static/logo.png",
                status="active",
                audit_note="示例活体宠物",
                **item,
            )
        )

    db.commit()


def table_has_columns(table_name: str, column_names: set[str]) -> bool:
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        return False
    existing = {column["name"] for column in inspector.get_columns(table_name)}
    return column_names.issubset(existing)
