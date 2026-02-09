def decide_buy_property(self, property_tile):
    # היוריסטיקה פשוטה:
    # 1. תמיד תקנה אם זה משלים לך מונופול
    # 2. אל תקנה אם זה משאיר אותך עם פחות מ-100$
    # 3. תעדיף צבעים מסוימים (כתום, אדום)

    if self.money - property_tile.price < 100:
        return False

    if property_tile.color in ["orange", "red"]:
        return True

    return True  # ברירת מחדל