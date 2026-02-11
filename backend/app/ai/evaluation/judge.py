from google import genai
import os
import time
import json

class LLMJudge:
    def __init__(self):
        # استخدم Gemini 1.5 Flash لأنه الأكثر استقراراً في الحصة المجانية
        self.model_name = "gemini-1.5-flash"
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def judge(self, query, chunks):
        context = "\n".join(chunks)
        prompt = f"""
        Evaluate CV relevance to the query. 
        Query: {query}
        Context: {context}
        Return JSON: {{"score": 1-5, "reasoning": "short explanation"}}
        """

        # محاولة الطلب مع نظام إعادة المحاولة في حال الخطأ 429
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={'response_mime_type': 'application/json'}
                )
                return json.loads(response.text)
            
            except Exception as e:
                if "429" in str(e):
                    print(f"⚠️ زحمة طلبات! محاولة {attempt+1}... سأنتظر 10 ثواني")
                    time.sleep(10) # انتظار إجباري لتفريغ الحصة
                else:
                    print(f"❌ خطأ غير متوقع: {e}")
                    break
        
        return {"score": 0, "reasoning": "Failed to get response after retries"}