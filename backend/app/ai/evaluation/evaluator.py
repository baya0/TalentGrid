from app.ai.evaluation.judge import LLMJudge


class Evaluator:

    def __init__(self):
        self.judge = LLMJudge()

    def evaluate(self, query, results):
        all_chunks = []
        for item in results:
            # إذا كان العنصر tuple (مثلاً: (id, data))
            if isinstance(item, tuple) and len(item) == 2:
                data = item[1]
            else:
                data = item
            # حاول استخراج "chunks" إذا وجدت وكانت قائمة
            chunks = data.get("chunks") if isinstance(data, dict) else None
            if chunks and isinstance(chunks, list):
                all_chunks.extend(chunks)
        score = self.judge.judge(query, all_chunks)
        return score
