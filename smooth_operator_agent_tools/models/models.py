"""
Models for the Smooth Operator Agent Tools, mirroring the C# implementation.
"""

from __future__ import annotations  # Enable postponed evaluation of annotations

import json
import base64
from enum import Enum
from typing import Dict, List, Optional, Any, TypeVar, Type, cast, Union, get_type_hints, get_origin, get_args
from datetime import datetime
import re  # Added for case conversion
import inspect  # Added for checking __init__ args
import logging  # Added for logging errors

# Configure basic logging
logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

# Helper function for JSON serialization of complex objects
def _default_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, 'to_dict'):  # Use to_dict if available
        return obj.to_dict()
    if hasattr(obj, '__dict__'):
        # Filter out private attributes for cleaner JSON
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    return str(obj)

# Helper function to convert PascalCase to snake_case
def _pascal_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# Helper function to convert snake_case to PascalCase
def _snake_to_pascal(name):
    return ''.join(word.capitalize() for word in name.split('_'))

# Generic Type Variable for factory methods
T = TypeVar('T', bound='BaseModel')

class BaseModel:
    """Base class for models to provide common functionality like from_dict and to_json_string."""

    @classmethod
    def from_dict(cls: Type[T], data: Optional[Dict[str, Any]], parent_obj: Optional[BaseModel] = None, processed_ids: Optional[set[str]] = None) -> Optional[T]:
        if data is None: return None
        obj_id = data.get('Id')
        current_processed_ids = processed_ids.copy() if processed_ids else set()
        if obj_id and obj_id in current_processed_ids:
             log.warning(f"Cycle detected for {cls.__name__} with ID {obj_id}, returning None.")
             return None
        if obj_id: current_processed_ids.add(obj_id)

        try:
            try: type_hints = get_type_hints(cls.__init__, globalns=globals(), localns=vars())
            except NameError: type_hints = get_type_hints(cls.__init__)
            init_signature = inspect.signature(cls.__init__)
            valid_keys = set(init_signature.parameters.keys()) - {'self'}
            constructor_args = {}
            child_list_data = {}

            for pascal_key, value in data.items():
                snake_key = _pascal_to_snake(pascal_key)
                if snake_key == 'parent':
                    continue

                if snake_key in valid_keys:
                    param_type = init_signature.parameters[snake_key].annotation
                    if isinstance(param_type, str):
                         try:
                              param_type = type_hints[snake_key]
                         except KeyError:
                              log.warning(f"Cannot resolve type hint for {snake_key} in {cls.__name__}")
                              continue
                    origin_type = get_origin(param_type); args_type = get_args(param_type)

                    if value is None: constructor_args[snake_key] = None
                    elif origin_type is list and args_type and isinstance(args_type[0], type) and issubclass(args_type[0], BaseModel):
                         child_list_data[snake_key] = (args_type[0], value); constructor_args[snake_key] = []
                    elif origin_type is Union and args_type and get_origin(args_type[0]) is list and len(get_args(args_type[0])) > 0 and isinstance(get_args(args_type[0])[0], type) and issubclass(get_args(args_type[0])[0], BaseModel):
                         child_list_data[snake_key] = (get_args(args_type[0])[0], value); constructor_args[snake_key] = []
                    elif (isinstance(param_type, type) and issubclass(param_type, BaseModel)) or \
                         (origin_type is Union and args_type and any(isinstance(at, type) and issubclass(at, BaseModel) for at in args_type)):
                         nested_model_type = param_type if isinstance(param_type, type) and issubclass(param_type, BaseModel) else next(at for at in args_type if isinstance(at, type) and issubclass(at, BaseModel))
                         if isinstance(value, dict): constructor_args[snake_key] = nested_model_type.from_dict(value, None, current_processed_ids)
                         else: constructor_args[snake_key] = None
                    elif param_type is datetime or (origin_type is Union and datetime in args_type):
                         try:
                              str_val = str(value).rstrip('Z')
                              if '.' in str_val:
                                   dt_obj = datetime.fromisoformat(str_val)
                              else:
                                   dt_obj = datetime.strptime(str_val, "%Y-%m-%dT%H:%M:%S")
                              constructor_args[snake_key] = dt_obj
                         except (ValueError, TypeError):
                              logging.warning(f"Bad datetime '{value}'")
                              constructor_args[snake_key] = None
                    else: constructor_args[snake_key] = value

            for key in valid_keys:
                 if key not in constructor_args:
                      param = init_signature.parameters[key]; param_type = param.annotation
                      if isinstance(param_type, str):
                           try:
                                param_type = type_hints[key]
                           except KeyError:
                                pass # Cannot resolve type, keep as string or handle otherwise?
                      origin_type = get_origin(param_type); args_type = get_args(param_type)
                      if param.default is not inspect.Parameter.empty: constructor_args[key] = param.default
                      elif origin_type is Union and type(None) in args_type: constructor_args[key] = None
                      else: constructor_args[key] = None # Default to None if mandatory field missing

            init_keys = set(inspect.signature(cls.__init__).parameters) - {'self'}
            filtered_args = {k: v for k, v in constructor_args.items() if k in init_keys}
            try: instance = cls(**filtered_args)
            except TypeError as te: log.error(f"TypeError creating {cls.__name__}: {te}. Args: {filtered_args}"); return None

            # Assign parent using the parameter passed during recursion,
            # UNLESS the original data had a 'Parent' key causing a cycle.
            assign_parent = True
            if 'Parent' in data and isinstance(data['Parent'], dict):
                parent_id_in_data = data['Parent'].get('Id')
                # Check if the parent ID from data is the one being processed higher up
                if parent_id_in_data and processed_ids and parent_id_in_data in processed_ids:
                    # This indicates a cycle defined explicitly in the data.
                    # The test expects child.parent to be None in this case.
                    log.warning(f"Cycle detected via Parent key in data for {cls.__name__} ID {obj_id}. Setting parent to None.")
                    assign_parent = False

            if assign_parent and parent_obj is not None and hasattr(instance, 'parent'):
                instance.parent = parent_obj
            elif hasattr(instance, 'parent'): # Ensure parent is None otherwise
                instance.parent = None

            for snake_key, (child_type, child_data_list) in child_list_data.items():
                 if hasattr(instance, snake_key):
                      children_list = [child_type.from_dict(item, instance, current_processed_ids) for item in child_data_list if isinstance(item, dict)]
                      setattr(instance, snake_key, [child for child in children_list if child is not None])

            return instance
        except Exception as e: log.error(f"Failed {cls.__name__} from dict: {e}"); import traceback; logging.error(traceback.format_exc()); return None

    def to_dict(self, is_child_call: bool = False) -> Dict[str, Any]:
        result = {}
        excluded_properties = set()
        if isinstance(self, ControlDTO): excluded_properties.update({'children_recursive', 'parents_recursive', 'parent_window'})

        for key, value in self.__dict__.items():
            if key.startswith('_') or key in excluded_properties: continue
            pascal_key = _snake_to_pascal(key)

            if key == 'parent':
                if isinstance(self, ControlDTO) and is_child_call and value is not None:
                    parent_info = {"Id": value.id, "Name": value.name, "ControlType": value.control_type}
                    result[pascal_key] = parent_info
                continue

            if isinstance(value, list): result[pascal_key] = [item.to_dict(is_child_call=True) if isinstance(item, BaseModel) else item for item in value if item is not None]
            elif isinstance(value, BaseModel): result[pascal_key] = value.to_dict(is_child_call=True)
            elif isinstance(value, datetime): result[pascal_key] = value.isoformat() + 'Z'
            elif isinstance(value, Enum): result[pascal_key] = value.value
            elif value is not None: result[pascal_key] = value
        return result

    def to_json_string(self) -> str:
        """
        Returns a JSON representation of the current object.
        
        Returns:
            JSON string representation.
        """
        return json.dumps(self, default=_default_serializer)


class MechanismType(str, Enum):
    """Specifies the mechanism to use for AI-based UI element interaction."""
    SCREEN_GRASP2 = "screengrasp2"
    SCREEN_GRASP2_LOW = "screengrasp2-low"
    SCREEN_GRASP_MEDIUM = "screengrasp-medium"
    SCREEN_GRASP_HIGH = "screengrasp-high"
    LLABS = "llabs"
    ANTHROPIC_COMPUTER_USE = "anthropic-computer-use"
    OPENAI_COMPUTER_USE = "openai-computer-use"
    QWEN25_VL_72B = "qwen25-vl-72b"

    # In Python, accessing the value is direct via .value
    # No need for GetDescription extension method like in C#


class Point(BaseModel):
    """Represents a point on the screen with X and Y coordinates."""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"Point(X={self.x}, Y={self.y})"


class ActionResponse(BaseModel):
    """Generic response for action endpoints."""
    def __init__(self, success: bool, message: Optional[str], data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        # Captures extra fields similar to C#'s [JsonExtensionData]
        self.data = data if data is not None else {}

    def __str__(self) -> str:
        return f"ActionResponse(Success={self.success}, Message='{self.message}', Data={self.data})"


class ScreenshotResponse(BaseModel):
    """Response from the screenshot endpoint."""
    # Allow PascalCase for backward compatibility if needed, but prefer snake_case
    def __init__(self, success: bool = True, image_base64: Optional[str] = None, timestamp: Optional[datetime] = None, message: Optional[str] = None):
        self.success = success
        self.image_base64 = image_base64
        self.timestamp = timestamp
        self.message = message

    @property
    def image_bytes(self) -> Optional[bytes]:
        """Get the image as bytes."""
        return base64.b64decode(self.image_base64) if self.image_base64 else None

    @property
    def image_mime_type(self) -> str:
        """Get the image MIME type."""
        return "image/jpeg"  # Assuming JPEG based on C#

    def __str__(self) -> str:
        return f"ScreenshotResponse(Success={self.success}, Message='{self.message}', Timestamp={self.timestamp}, HasImage={self.image_base64 is not None})"


class ScreenGrasp2Response(ActionResponse):
    """Response from the ScreenGrasp2 endpoint (find-ui-element-by-description)."""
    def __init__(self, success: bool, message: Optional[str], data: Optional[Dict[str, Any]] = None,
                 x: Optional[int] = None, y: Optional[int] = None, status: Optional[str] = None):
        # Call parent init with snake_case args
        super().__init__(success=success, message=message, data=data)
        self.x = x
        self.y = y
        self.status = status

    def __str__(self) -> str:
        # Access parent attributes using snake_case
        return f"ScreenGrasp2Response(Success={self.success}, Message='{self.message}', X={self.x}, Y={self.y}, Status='{self.status}', Data={self.data})"


class ChromeTab(BaseModel):
    """Information about a Chrome browser tab."""
    def __init__(self, id: Optional[str] = None, title: Optional[str] = None, url: Optional[str] = None, is_active: bool = False):
        self.id = id
        self.title = title
        self.url = url
        self.is_active = is_active

    def __str__(self) -> str:
        return f"ChromeTab(Id='{self.id}', Title='{self.title}', Url='{self.url}', IsActive={self.is_active})"


class ChromeTabDetails(BaseModel):
    """Detailed information about a Chrome tab."""
    def __init__(self, title: Optional[str] = None, url: Optional[str] = None, content: Optional[str] = None,
                 elements: Optional[List[Dict[str, Any]]] = None, summary: Optional[str] = None):
        self.title = title
        self.url = url
        self.content = content
        self.elements = elements if elements is not None else []
        self.summary = summary

    def __str__(self) -> str:
        return f"ChromeTabDetails(Title='{self.title}', Url='{self.url}', HasContent={self.content is not None}, ElementCount={len(self.elements)}, HasSummary={self.summary is not None})"


class ChromeScriptResponse(ActionResponse):
    """Response from Chrome script execution."""
    def __init__(self, success: bool, message: Optional[str], data: Optional[Dict[str, Any]] = None, result: Optional[str] = None):
        super().__init__(success=success, message=message, data=data)
        self.result = result

    def __str__(self) -> str:
        return f"ChromeScriptResponse(Success={self.success}, Message='{self.message}', Result='{self.result}', Data={self.data})"


class CSharpCodeResponse(ActionResponse):
    """Response from C# code execution."""
    def __init__(self, success: bool, message: Optional[str], data: Optional[Dict[str, Any]] = None, result: Optional[str] = None):
        super().__init__(success=success, message=message, data=data)
        self.result = result

    def __str__(self) -> str:
        return f"CSharpCodeResponse(Success={self.success}, Message='{self.message}', Result='{self.result}', Data={self.data})"


class ControlDTO(BaseModel):
    """Information about a UI control element."""
    def __init__(self, id: Optional[str] = None, name: Optional[str] = None, creation_date: Optional[datetime] = None,
                 control_type: Optional[str] = None, supports_set_value: Optional[bool] = None,
                 supports_invoke: Optional[bool] = None, current_value: Optional[str] = None,
                 children: Optional[List[ControlDTO]] = None, parent: Optional[ControlDTO] = None,
                 is_smooth_operator: bool = False):
        self.id = id
        self.name = name
        self.creation_date = creation_date
        self.control_type = control_type
        self.supports_set_value = supports_set_value
        self.supports_invoke = supports_invoke
        self.current_value = current_value
        # Ensure children is initialized correctly if None is passed
        self.children: List[ControlDTO] = children if children is not None else []
        self.parent: Optional[ControlDTO] = parent
        self.is_smooth_operator = is_smooth_operator

    @property
    def children_recursive(self) -> List[ControlDTO]:  # Changed to return List for easier use, mirrors C# List return
        """Recursively get all descendant controls."""
        descendants = []
        if not self.children:
            return descendants
        for child in self.children:
            if child:  # Check if child is not None (due to cycle detection in from_dict)
                descendants.append(child)
                descendants.extend(child.children_recursive)  # Recursive call
        return descendants

    @property
    def parents_recursive(self) -> List[ControlDTO]:  # Changed to return List
        """Get all ancestor controls."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent  # Move up the hierarchy
        return ancestors

    @property
    def parent_window(self) -> Optional[ControlDTO]:
        """Find the closest ancestor control that is a Window."""
        current = self.parent
        while current:
            if current.control_type == "Window":
                return current
            current = current.parent
        return None

    def __str__(self) -> str:
        value_info = f" Value='{self.current_value}'" if self.current_value else ""
        name_id = self.name or self.id or "N/A"
        return f"{self.control_type or 'Control'} '{name_id}'{value_info}"


class WindowDetailResponse(BaseModel):
    """Wrapper for WindowDetailInfosDTO, potentially from older API versions."""
    def __init__(self, details: Optional[WindowDetailInfosDTO] = None, message: Optional[str] = None):
        self.details = details
        self.message = message

    def __str__(self) -> str:
        return f"WindowDetailResponse(Message='{self.message}', HasDetails={self.details is not None})"


class WindowInfoDTO(BaseModel):
    """Information about a window."""
    def __init__(self, id: Optional[str] = None, title: Optional[str] = None, executable_path: Optional[str] = None,
                 is_foreground: Optional[bool] = None, process_name: Optional[str] = None,
                 is_minimized: Optional[bool] = None, detail_infos: Optional[WindowDetailResponse] = None):
        self.id = id
        self.title = title
        self.executable_path = executable_path
        self.is_foreground = is_foreground  # null == false in C#
        self.process_name = process_name
        self.is_minimized = is_minimized
        self.detail_infos = detail_infos  # Contains WindowDetailInfosDTO

    def __str__(self) -> str:
        foreground_marker = "[FOREGROUND] " if self.is_foreground else ""
        display_name = self.title or self.process_name or self.executable_path or self.id or "N/A"
        return f"{foreground_marker}{display_name}"


class WindowDetailInfosDTO(BaseModel):
    """Detailed UI automation information for a window."""
    # Note: C# has Window and UserInterfaceElements as readonly properties set in constructor.
    # Python __init__ will set them directly.
    def __init__(self, note: Optional[str] = None, window: Optional[WindowInfoDTO] = None,
                 user_interface_elements: Optional[ControlDTO] = None):
        self.note = note
        self.window = window
        self.user_interface_elements = user_interface_elements  # Root element

    def __str__(self) -> str:
        # Avoid overly verbose output, summarize
        window_str = str(self.window) if self.window else "N/A"
        elements_str = "Available" if self.user_interface_elements else "None"
        return f"{{ Window = {window_str}, UserInterfaceElements = {elements_str} }}"


class ChromeElementInfo(BaseModel):
    """Detailed information about an element within a Chrome tab."""
    def __init__(self, smooth_op_id: Optional[str] = None, tag_name: Optional[str] = None,
                 css_selector: Optional[str] = None, inner_text: Optional[str] = None,
                 is_visible: Optional[bool] = None, score: Optional[float] = None,
                 role: Optional[str] = None, value: Optional[str] = None,
                 type: Optional[str] = None, name: Optional[str] = None,
                 class_name: Optional[str] = None, semantic: Optional[str] = None,
                 data_attributes: Optional[str] = None, truncated_html: Optional[str] = None,
                 bounding_rect: Optional[List[int]] = None, center_point: Optional[Point] = None):
        self.smooth_op_id = smooth_op_id
        self.tag_name = tag_name
        self.css_selector = css_selector
        self.inner_text = inner_text
        self.is_visible = is_visible
        self.score = score
        self.role = role
        self.value = value
        self.type = type
        self.name = name
        self.class_name = class_name
        self.semantic = semantic
        self.data_attributes = data_attributes
        self.truncated_html = truncated_html
        self.bounding_rect = bounding_rect if bounding_rect is not None else []
        self.center_point = center_point

    def __str__(self) -> str:
        display_text = self.inner_text or self.value or ""
        role_info = f" role={self.role}" if self.role else ""
        type_info = f" type={self.type}" if self.type else ""
        visibility_info = " (hidden)" if self.is_visible is False else ""
        semantic_info = f" semantic={self.semantic}" if self.semantic else ""
        score_info = f" (score: {self.score})" if self.score is not None else ""
        return f"<{self.tag_name}{role_info}{type_info}>{display_text}{visibility_info}{semantic_info}{score_info}"


class FocusInformation(BaseModel):
    """Information about the currently focused element."""
    def __init__(self, focused_element: Optional[ControlDTO] = None,
                 focused_element_parent_window: Optional[WindowInfoDTO] = None,
                 some_other_elements_in_same_window_that_might_be_relevant: Optional[List[ControlDTO]] = None,
                 current_chrome_tab_most_relevant_elements: Optional[List[ChromeElementInfo]] = None,
                 is_chrome: bool = False, note: Optional[str] = None):
        self.focused_element = focused_element
        self.focused_element_parent_window = focused_element_parent_window
        self.some_other_elements_in_same_window_that_might_be_relevant = some_other_elements_in_same_window_that_might_be_relevant if some_other_elements_in_same_window_that_might_be_relevant is not None else []
        self.current_chrome_tab_most_relevant_elements = current_chrome_tab_most_relevant_elements if current_chrome_tab_most_relevant_elements is not None else []
        self.is_chrome = is_chrome
        self.note = note

    def __str__(self) -> str:
        if self.focused_element:
            return str(self.focused_element)
        if self.focused_element_parent_window:
            return str(self.focused_element_parent_window)
        return "No focused element"


class TabData(BaseModel):
    """Data for a single tab within a Chrome instance."""
    def __init__(self, id: Optional[str] = None, url: Optional[str] = None, is_active: Optional[bool] = None,
                 html: Optional[str] = None, text: Optional[str] = None, id_string: Optional[str] = None,
                 tab_nr: int = 0):
        self.id = id
        self.url = url
        self.is_active = is_active
        self.html = html
        self.text = text
        self.id_string = id_string  # Seems redundant with Id? Included for C# parity
        self.tab_nr = tab_nr

    def __str__(self) -> str:
        active_marker = " [Active]" if self.is_active else ""
        display_url = self.url or self.id_string or "N/A"
        return f"Tab {self.tab_nr}{active_marker}: {display_url}"


class ChromeOverview(BaseModel):
    """Overview information about a single Chrome instance."""
    def __init__(self, instance_id: Optional[str] = None, tabs: Optional[List[TabData]] = None,
                 last_update: Optional[datetime] = None):
        self.instance_id = instance_id
        self.tabs = tabs if tabs is not None else []
        self.last_update = last_update

    def __str__(self) -> str:
        tabs_count = len(self.tabs) if self.tabs else 0
        return f"{self.instance_id}: {tabs_count} Tabs"


class TaskbarIconDTO(BaseModel):
    """Information about an icon pinned to the taskbar."""
    def __init__(self, name: Optional[str] = None, path: Optional[str] = None):
        self.name = name
        self.path = path

    def __str__(self) -> str:
        return f"TaskbarIconDTO(Name='{self.name}', Path='{self.path}')"


class DesktopIconDTO(BaseModel):
    """Information about an icon on the desktop."""
    def __init__(self, name: Optional[str] = None, path: Optional[str] = None):
        self.name = name
        self.path = path

    def __str__(self) -> str:
        return f"DesktopIconDTO(Name='{self.name}', Path='{self.path}')"


class InstalledProgramDTO(BaseModel):
    """Information about an installed program."""
    def __init__(self, name: Optional[str] = None, executable_path: Optional[str] = None):
        self.name = name
        self.executable_path = executable_path

    def __str__(self) -> str:
        return f"InstalledProgramDTO(Name='{self.name}', Path='{self.executable_path}')"


class OverviewResponse(BaseModel):
    """Response from the system overview endpoint."""
    def __init__(self, windows: Optional[List[WindowInfoDTO]] = None,
                 chrome_instances: Optional[List[ChromeOverview]] = None,
                 focus_info: Optional[FocusInformation] = None,
                 top_pinned_taskbar_icons: Optional[List[TaskbarIconDTO]] = None,
                 top_desktop_icons: Optional[List[DesktopIconDTO]] = None,
                 top_installed_programs: Optional[List[InstalledProgramDTO]] = None,
                 important_note: Optional[str] = None):
        self.windows = windows if windows is not None else []
        self.chrome_instances = chrome_instances if chrome_instances is not None else []
        self.focus_info = focus_info
        self.top_pinned_taskbar_icons = top_pinned_taskbar_icons if top_pinned_taskbar_icons is not None else []
        self.top_desktop_icons = top_desktop_icons if top_desktop_icons is not None else []
        self.top_installed_programs = top_installed_programs if top_installed_programs is not None else []
        self.important_note = important_note

    def __str__(self) -> str:
        windows_count = len(self.windows) if self.windows else 0
        chrome_count = len(self.chrome_instances) if self.chrome_instances else 0
        focus_str = str(self.focus_info) if self.focus_info else "N/A"
        return f"Overview: {windows_count} Windows, {chrome_count} Chrome Instances. Focus: {focus_str}"


class SimpleResponse(BaseModel):
    """Simple response with message, potentially internal message."""
    def __init__(self, message: Optional[str] = None, internal_message: Optional[str] = None):
        self.message = message
        self.internal_message = internal_message

    def __str__(self) -> str:
        return f"SimpleResponse(Message='{self.message}', InternalMessage='{self.internal_message}')"
