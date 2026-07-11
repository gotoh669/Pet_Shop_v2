import json
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.pet import PetProfile
from app.models.product import Product
from app.repositories.pet_repository import PetRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.agent import (
    ShoppingGuideProduct,
    ShoppingGuideRequest,
    ShoppingGuideResponse,
)
from app.services.deepseek_service import DeepSeekClient
from app.services.product_service import to_product_public


KEYWORD_GROUPS = {
    "food": ["粮", "猫粮", "狗粮", "零食", "罐头", "冻干", "营养", "主食", "吃", "肠胃"],
    "clean": ["清洁", "除臭", "猫砂", "洗", "沐浴", "尿", "消毒", "湿巾"],
    "groom": ["掉毛", "毛", "梳", "美容", "指甲", "护理", "化毛"],
    "toy": ["玩具", "球", "逗猫", "互动", "磨牙", "抓板"],
    "home": ["窝", "笼", "垫", "碗", "饮水", "出行", "牵引", "项圈"],
    "health": ["驱虫", "疫苗", "健康", "泪痕", "皮肤", "关节", "口腔"],
}

GROUP_ADVICE = {
    "food": "优先选择适合宠物类型和年龄阶段的主粮，预算充足时再搭配零食。",
    "clean": "清洁用品建议按消耗频率购买，除臭、湿巾、猫砂这类可以作为常备品。",
    "groom": "掉毛或毛发护理需求明显时，梳毛工具和化毛类用品比单纯零食更实用。",
    "toy": "玩具类建议选择互动性强、材质安全、尺寸适合宠物体型的商品。",
    "home": "窝垫、食碗和出行用品更看重尺寸、耐用度和清洗便利性。",
    "health": "健康相关商品只能作为日常护理辅助，异常症状请及时咨询兽医。",
}


class ShoppingGuideAgent:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.product_repo = ProductRepository(db)
        self.pet_repo = PetRepository(db)

    def recommend(
        self,
        payload: ShoppingGuideRequest,
        user_id: int | None = None,
    ) -> ShoppingGuideResponse:
        pet = self.pet_repo.get_current_pet(user_id) if user_id else None
        products, _ = self.product_repo.list_products(page=1, page_size=100, status="active")
        available_products = [product for product in products if product.stock > 0]
        ranked = self._rank_products(payload, pet, available_products)
        selected = ranked[:4]

        ai_summary = self._call_deepseek(payload, pet, selected)
        source = "deepseek" if ai_summary else "rules"
        summary = ai_summary or self._build_summary(payload, pet, selected)
        advice = self._build_advice(payload, pet)

        return ShoppingGuideResponse(
            summary=summary,
            advice=advice,
            products=[
                ShoppingGuideProduct(
                    id=product.id,
                    title=product.title,
                    price=product.price,
                    cover_url=product.cover_url,
                    category_name=to_product_public(product, self.product_repo.get_category(product.category_id)).category_name,
                    stock=product.stock,
                    reason=reason,
                )
                for product, reason in selected
            ],
            source=source,
        )

    def _rank_products(
        self,
        payload: ShoppingGuideRequest,
        pet: PetProfile | None,
        products: list[Product],
    ) -> list[tuple[Product, str]]:
        query = self._normalize(" ".join(
            filter(
                None,
                [
                    payload.message,
                    payload.pet_type,
                    payload.breed,
                    pet.pet_type if pet else None,
                    pet.breed if pet else None,
                    pet.health_notes if pet else None,
                ],
            )
        ))
        budget = payload.budget
        matched_groups = self._matched_groups(query)

        ranked: list[tuple[int, Product, str]] = []
        for product in products:
            score = 0
            text = self._product_text(product)
            reasons = []

            for group in matched_groups:
                hits = [word for word in KEYWORD_GROUPS[group] if word in text or word in query]
                if hits:
                    score += 8 + len(hits)
                    reasons.append(GROUP_ADVICE[group])

            if pet and pet.pet_type and pet.pet_type in text:
                score += 8
                reasons.append(f"适合当前宠物类型：{pet.pet_type}")
            if payload.pet_type and payload.pet_type in text:
                score += 8
                reasons.append(f"匹配你填写的宠物类型：{payload.pet_type}")
            if budget is not None:
                price = Decimal(str(product.price))
                if price <= budget:
                    score += 6
                    reasons.append(f"价格在预算 ￥{budget} 内")
                else:
                    score -= 6

            score += min(int(product.sales_count or 0), 30) // 5
            if product.stock > 0:
                score += 2

            if not reasons:
                reasons.append("综合标题、分类和库存推荐")
            ranked.append((score, product, self._compact_reason(reasons)))

        ranked.sort(key=lambda item: (item[0], item[1].sales_count or 0, item[1].id), reverse=True)
        return [(product, reason) for score, product, reason in ranked if score > -5]

    def _matched_groups(self, query: str) -> list[str]:
        groups = [group for group, words in KEYWORD_GROUPS.items() if any(word in query for word in words)]
        return groups or ["food", "clean", "toy"]

    def _build_summary(
        self,
        payload: ShoppingGuideRequest,
        pet: PetProfile | None,
        products: list[tuple[Product, str]],
    ) -> str:
        pet_label = self._pet_label(payload, pet)
        if not products:
            return f"暂时没有找到特别匹配的商品，可以换一个更具体的需求试试，例如宠物类型、预算、年龄或护理问题。"
        top_names = "、".join(product.title for product, _ in products[:2])
        return f"我按{pet_label}和你的需求筛了一轮，建议先看 {top_names}，再根据预算补充清洁或玩具类商品。"

    def _build_advice(self, payload: ShoppingGuideRequest, pet: PetProfile | None) -> list[str]:
        query = self._normalize(payload.message)
        groups = self._matched_groups(query)
        advice = [GROUP_ADVICE[group] for group in groups[:3]]
        if payload.budget is not None:
            advice.append(f"当前预算是 ￥{payload.budget}，建议优先买高频刚需，再考虑趣味类商品。")
        if pet:
            advice.append(f"已结合当前宠物档案：{pet.name}（{pet.pet_type}{' / ' + pet.breed if pet.breed else ''}）。")
        return advice[:4]

    def _call_deepseek(
        self,
        payload: ShoppingGuideRequest,
        pet: PetProfile | None,
        products: list[tuple[Product, str]],
    ) -> str | None:
        if not products:
            return None

        product_lines = [
            {
                "title": product.title,
                "price": str(product.price),
                "category": to_product_public(product, self.product_repo.get_category(product.category_id)).category_name,
                "reason": reason,
            }
            for product, reason in products
        ]
        prompt = (
            "你是宠物商城的导购 Agent。请用中文输出 1 段不超过 80 字的推荐总结，"
            "不要诊断疾病，不要夸大功效。\n"
            f"用户需求：{payload.message}\n"
            f"预算：{payload.budget or '未填写'}\n"
            f"宠物档案：{self._pet_label(payload, pet)}\n"
            f"候选商品：{json.dumps(product_lines, ensure_ascii=False)}"
        )
        try:
            result = DeepSeekClient().simple_chat(
                message=prompt,
                system_prompt="你是谨慎、实用的宠物电商导购。",
                temperature=0.4,
                max_tokens=180,
            )
        except AppError:
            return None
        content = result.get("content")
        return content.strip() if isinstance(content, str) and content.strip() else None

    def _pet_label(self, payload: ShoppingGuideRequest, pet: PetProfile | None) -> str:
        pet_type = payload.pet_type or (pet.pet_type if pet else "")
        breed = payload.breed or (pet.breed if pet else "")
        if pet_type and breed:
            return f"{pet_type} / {breed}"
        return pet_type or breed or "通用宠物需求"

    def _product_text(self, product: Product) -> str:
        parts = [
            product.title,
            product.subtitle,
            product.brand,
            product.spec,
            product.applicable_pet,
            product.detail,
            json.dumps(product.tags, ensure_ascii=False) if product.tags else "",
        ]
        return self._normalize(" ".join(part for part in parts if part))

    def _normalize(self, value: str) -> str:
        return value.lower().replace(" ", "")

    def _compact_reason(self, reasons: list[str]) -> str:
        seen = []
        for reason in reasons:
            if reason not in seen:
                seen.append(reason)
        return "；".join(seen[:2])
