class QueryParser:

    def parse(self, query: str, ui_filters: dict):

        return {"query": query.strip(), "filters": self._build_filters(ui_filters)}

    def _build_filters(self, ui_filters: dict):
        """
        Translate UI filter names to ChromaDB where clause format.

        UI sends: min_experience, max_experience, languages, location
        ChromaDB metadata has: experience_years (int), languages (str), location (str)
        """
        if not ui_filters:
            return None

        conditions = []

        # Experience range → ChromaDB experience_years field
        min_exp = ui_filters.get("min_experience")
        max_exp = ui_filters.get("max_experience")

        if min_exp is not None:
            conditions.append({"experience_years": {"$gte": int(min_exp)}})
        if max_exp is not None:
            conditions.append({"experience_years": {"$lte": int(max_exp)}})

        if not conditions:
            return None

        if len(conditions) == 1:
            return conditions[0]

        return {"$and": conditions}
