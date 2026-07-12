from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime
import json

Base = declarative_base()


class VideoJob(Base):
    __tablename__ = "video_jobs"

    id = Column(Integer, primary_key=True)
    job_uuid = Column(String, unique=True, index=True)
    original_name = Column(String)
    stored_path = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)

    # uploaded (awaiting style selection) | queued | processing | done | error
    status = Column(String, default="uploaded")
    progress = Column(String, default="")        # human-readable current step
    error = Column(Text, default="")

    transcript = Column(Text, default="")
    visual_summary = Column(Text, default="")

    # Style selection (set once the user picks a style / hits Generate)
    selected_styles = Column(Text, default="[]")        # JSON list of base style keys
    personalize_prompt = Column(Text, default="")       # empty unless Personalize was used
    combined_style_name = Column(String, default="")    # set only when 2+ styles selected
    combined_style_description = Column(Text, default="")

    # Generation output — one style/tone per job now, not four
    captions = Column(Text, default="[]")   # JSON list of {start, end, text}
    summary = Column(Text, default="")
    output_file = Column(String, default="")  # filename in OUTPUT_DIR

    def get(self, field):
        return json.loads(getattr(self, field) or "[]")

    def set(self, field, value):
        setattr(self, field, json.dumps(value))

    def to_dict(self):
        return {
            "id": self.id,
            "job_uuid": self.job_uuid,
            "original_name": self.original_name,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "status": self.status,
            "progress": self.progress,
            "error": self.error,
            "transcript": self.transcript,
            "selected_styles": self.get("selected_styles"),
            "personalize_prompt": self.personalize_prompt,
            "combined_style_name": self.combined_style_name,
            "combined_style_description": self.combined_style_description,
            "captions": self.get("captions"),
            "summary": self.summary,
            "output_file": self.output_file,
        }
