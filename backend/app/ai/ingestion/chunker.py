import uuid


class CVChunker:

    def __init__(self):
        pass


    def chunk(self, cv_json: dict):

        chunks = []

        cv_id = str(uuid.uuid4())

        # -------- Extract Languages (for metadata) --------
        languages = cv_json.get("languages", [])

        language_names = []

        for lang in languages:
            name = lang.get("name")
            if name:
                language_names.append(name)


        # -------- Profile --------
        summary = cv_json.get("summary")
        title = cv_json.get("title")

        profile_text = ""

        if title:
            profile_text += f"Job Title: {title}. "

        if summary:
            profile_text += f"Summary: {summary}"

        if profile_text.strip():

            chunks.append(
                self._build_chunk(
                    cv_id,
                    "profile",
                    profile_text,
                    cv_json,
                    language_names
                )
            )


        # -------- Skills --------
        skills = cv_json.get("skills", [])

        if skills:

            skills_text = "Skills: " + ", ".join(skills)

            chunks.append(
                self._build_chunk(
                    cv_id,
                    "skills",
                    skills_text,
                    cv_json,
                    language_names
                )
            )


        # -------- Experience --------
        experiences = cv_json.get("experience", [])

        for i, exp in enumerate(experiences):

            text = (
                f"Role: {exp.get('role')}. "
                f"Company: {exp.get('organization')}. "
                f"Period: {exp.get('from')} - {exp.get('to')}. "
                f"Description: {exp.get('description')}"
            )

            chunks.append(
                self._build_chunk(
                    cv_id,
                    f"experience_{i}",
                    text,
                    cv_json,
                    language_names
                )
            )


        # -------- Education --------
        educations = cv_json.get("education", [])

        for i, edu in enumerate(educations):

            text = (
                f"Degree: {edu.get('degree')}. "
                f"Field: {edu.get('field')}. "
                f"Institution: {edu.get('institution')}. "
                f"Period: {edu.get('from')} - {edu.get('to')}"
            )

            chunks.append(
                self._build_chunk(
                    cv_id,
                    f"education_{i}",
                    text,
                    cv_json,
                    language_names
                )
            )


        # -------- Languages Chunk --------
        if languages:

            langs = []

            for lang in languages:
                langs.append(
                    f"{lang.get('name')} ({lang.get('level')})"
                )

            text = "Languages: " + ", ".join(langs)

            chunks.append(
                self._build_chunk(
                    cv_id,
                    "languages",
                    text,
                    cv_json,
                    language_names
                )
            )


        # -------- Certifications --------
        certs = cv_json.get("certifications", [])

        if certs:

            text = "Certifications: " + ", ".join(certs)

            chunks.append(
                self._build_chunk(
                    cv_id,
                    "certifications",
                    text,
                    cv_json,
                    language_names
                )
            )


        # -------- Projects --------
        projects = cv_json.get("projects_or_work", [])

        for i, proj in enumerate(projects):

            text = f"Project: {proj}"

            chunks.append(
                self._build_chunk(
                    cv_id,
                    f"project_{i}",
                    text,
                    cv_json,
                    language_names
                )
            )


        return chunks


    def _build_chunk(self, cv_id, chunk_type, text, cv_json, language_names):

        return {
            "id": f"{cv_id}_{chunk_type}",
            "text": text,
            "metadata": {
                "cv_id": cv_id,
                "chunk_type": chunk_type,
                "name": cv_json.get("name"),
                "location": cv_json.get("location"),
                "experience_years": cv_json.get("experience_years"),
                "title": cv_json.get("title"),

                # ✅ Convert list to a comma-separated string
                "languages": ", ".join(language_names) if language_names else None,
            }
        }
