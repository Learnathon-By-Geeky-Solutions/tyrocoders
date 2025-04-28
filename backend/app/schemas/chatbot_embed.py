from pydantic import BaseModel, Field
from typing import Optional


class ChatbotEmbedUpdateModel(BaseModel):
    widget_size: Optional[str] = None
    button_size: Optional[str] = None
    offset_bottom_desktop: Optional[float] = None
    offset_bottom_mobile: Optional[float] = None
    offset_right_desktop: Optional[float] = None
    offset_right_mobile: Optional[float] = None
    widget_display: Optional[str] = None
    specific_url_for_hide_or_show: Optional[str] = None
    allow_widget_movable: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "widget_size": "normal",
                "button_size": "large",
                "offset_bottom_desktop": 20.5,
                "offset_bottom_mobile": 10.0,
                "offset_right_desktop": 15.0,
                "offset_right_mobile": 5.0,
                "widget_display": "entire_site",
                "specific_url_for_hide_or_show": "",
                "allow_widget_movable": True,
            }
        }