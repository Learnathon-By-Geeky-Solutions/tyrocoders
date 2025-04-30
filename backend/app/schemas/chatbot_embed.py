from pydantic import BaseModel, Field
from typing import Optional


class ChatbotEmbedUpdateModel(BaseModel):
    """
    Model for updating the configuration of the chatbot widget's embedding settings.

    This model allows customization of the chatbot widget's appearance and behavior,
    including widget size, button size, positioning on the screen, and whether it can
    be moved. It also supports conditions for when the widget should be displayed or
    hidden based on the URL.

    Attributes:
        widget_size (Optional[str]): The size of the widget. Possible values could include 'normal', 'small', 'large'.
        button_size (Optional[str]): The size of the widget button. Possible values could include 'small', 'large', etc.
        offset_bottom_desktop (Optional[float]): The distance from the bottom of the screen for desktop views.
        offset_bottom_mobile (Optional[float]): The distance from the bottom of the screen for mobile views.
        offset_right_desktop (Optional[float]): The distance from the right of the screen for desktop views.
        offset_right_mobile (Optional[float]): The distance from the right of the screen for mobile views.
        widget_display (Optional[str]): Specifies when the widget is displayed. Possible values could be 'entire_site', 'specific_page', etc.
        specific_url_for_hide_or_show (Optional[str]): A specific URL where the widget should be hidden or shown.
        allow_widget_movable (Optional[bool]): A flag indicating if the widget can be moved around by the user.

    Config:
        json_schema_extra (dict): Provides an example schema for API documentation and testing.
    """
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
