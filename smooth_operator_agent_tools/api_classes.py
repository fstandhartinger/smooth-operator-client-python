"""
API classes for the Smooth Operator Agent Tools.
"""

from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING
# Import the models module with an alias
from .models import models as M

# Use TYPE_CHECKING to avoid circular import for type hinting the client
if TYPE_CHECKING:
    from .smooth_operator_client import SmoothOperatorClient


class ScreenshotApi:
    """API endpoints for screenshot and analysis operations."""

    def __init__(self, client: 'SmoothOperatorClient'): # Add type hint
        """
        Initialize the ScreenshotApi.

        Args:
            client: The SmoothOperatorClient instance
        """
        self._client = client

    def take(self) -> Optional[M.ScreenshotResponse]: # Update return type hint
        """
        Captures a screenshot of the entire screen as Base64-encoded image.

        Returns:
            Screenshot response containing image_base64 property or None on error
        """
        # Use _get_internal with expected_type
        return self._client._get_internal("/tools-api/screenshot", expected_type=M.ScreenshotResponse)

    def find_ui_element(self, user_element_description: str,
                        mechanism: M.MechanismType = M.MechanismType.SCREEN_GRASP2) -> Optional[M.ScreenGrasp2Response]: # Update return type hint and mechanism type
        """
        Uses AI to find the x/y coordinate of a UI element based on text description.
        Takes a fresh screenshot each time.

        Args:
            user_element_description: Text description of the element to find
            mechanism: The AI mechanism to use for finding the element (defaults to ScreenGrasp2)

        Returns:
            Response with X/Y coordinates or None on error
        """
        # Server expects TaskDescription and Mechanism
        # Use _post_internal with expected_type
        return self._client._post_internal(
            "/tools-api/screenshot/find-ui-element",
            expected_type=M.ScreenGrasp2Response,
            data={"taskDescription": user_element_description, "Mechanism": mechanism.value} # Use mechanism.value
        )

    def __str__(self) -> str:
        """Return a string representation of the ScreenshotApi class."""
        return "ScreenshotApi"


class SystemApi:
    """API endpoints for system operations."""

    def __init__(self, client: 'SmoothOperatorClient'): # Add type hint
        """
        Initialize the SystemApi.

        Args:
            client: The SmoothOperatorClient instance
        """
        self._client = client

    def get_overview(self) -> Optional[M.OverviewResponse]: # Update return type hint
        """
        Gets detailed overview of computer state including open applications and windows.

        Returns:
            OverviewResponse with FocusInfo, Windows array and Chrome details or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/system/overview", expected_type=M.OverviewResponse, data={})

    def get_window_details(self, window_id: str) -> Optional[M.WindowDetailInfosDTO]: # Update return type hint
        """
        Gets detailed UI automation information for a window.

        Args:
            window_id: Window ID from get_overview

        Returns:
            WindowDetailInfosDTO with element hierarchy and properties or None on error
        """
        # Use _post_internal with expected_type
        # Note: The server endpoint is under /automation/, not /system/
        return self._client._post_internal("/tools-api/automation/get-details", expected_type=M.WindowDetailInfosDTO, data={"windowId": window_id})

    def open_chrome(self, url: Optional[str] = None, strategy: Optional[str] = None) -> Optional[M.SimpleResponse]: # Update return type hint
        """
        Opens Chrome browser (Playwright-managed instance).

        Args:
            url: Optional URL to navigate to immediately
            strategy: Optional strategy for opening Chrome

        Returns:
            SimpleResponse indicating success or failure or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/system/open-chrome", expected_type=M.SimpleResponse, data={"url": url, "strategy": strategy})

    def open_application(self, app_name_or_path: str) -> Optional[M.SimpleResponse]: # Update return type hint
        """
        Launches an application by path or name.

        Args:
            app_name_or_path: Full path to executable or application name,
                             alternatively exe name if in path (e.g. notepad, calc).
                             For chrome don't use this, use open_chrome instead.

        Returns:
            SimpleResponse indicating success or failure or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/system/open-application", expected_type=M.SimpleResponse, data={"appNameOrPath": app_name_or_path})

    def __str__(self) -> str:
        """Return a string representation of the SystemApi class."""
        return "SystemApi"


class MouseApi:
    """API endpoints for mouse operations."""

    def __init__(self, client: 'SmoothOperatorClient'): # Add type hint
        """
        Initialize the MouseApi.

        Args:
            client: The SmoothOperatorClient instance
        """
        self._client = client

    def click(self, x: int, y: int) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Performs left mouse click at screen coordinates (0,0 is top-left).

        Args:
            x: Horizontal pixel coordinate
            y: Vertical pixel coordinate

        Returns:
            Action response with success status or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/mouse/click", expected_type=M.ActionResponse, data={"x": x, "y": y})

    def double_click(self, x: int, y: int) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Perform a double click at the specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Action response or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/mouse/doubleclick", expected_type=M.ActionResponse, data={"x": x, "y": y})

    def right_click(self, x: int, y: int) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Perform a right mouse button click at the specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Action response or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/mouse/rightclick", expected_type=M.ActionResponse, data={"x": x, "y": y})

    def move(self, x: int, y: int) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Move the mouse cursor to the specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Action response or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/mouse/move", expected_type=M.ActionResponse, data={"x": x, "y": y})

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Perform a mouse drag operation from start coordinates to end coordinates.

        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate

        Returns:
            Action response or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/mouse/drag", expected_type=M.ActionResponse, data={
            "startX": start_x,
            "startY": start_y,
            "endX": end_x,
            "endY": end_y
        })

    def scroll(self, x: int, y: int, clicks: int, direction: Optional[str] = None) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Scrolls mouse wheel at specified coordinates.

        Args:
            x: Horizontal pixel coordinate
            y: Vertical pixel coordinate
            clicks: Number of scroll clicks (positive for down, negative for up)
            direction: Direction to scroll ("up" or "down"). Overrides clicks sign if provided.

        Returns:
            Action response with success status or None on error
        """
        # Map clicks to server's expectation (positive=down, negative=up) if direction is null
        if direction is None:
            direction = "down" if clicks > 0 else "up"
            clicks = abs(clicks)
        else:
            clicks = abs(clicks)  # Ensure clicks is positive when direction is specified

        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/mouse/scroll", expected_type=M.ActionResponse, data={
            "x": x,
            "y": y,
            "clicks": clicks,
            "direction": direction
        })

    def click_by_description(self, user_element_description: str,
                            mechanism: M.MechanismType = M.MechanismType.SCREEN_GRASP2) -> Optional[M.ActionResponse]: # Update return type hint and mechanism type
        """
        Uses AI vision to find and click a UI element based on description.

        Args:
            user_element_description: Natural language description of element
                                     (be specific and include unique identifiers)
            mechanism: The AI mechanism to use for finding the element (defaults to ScreenGrasp2)

        Returns:
            Action response with success status and coordinates or None on error

        Note:
            If you know the exact coordinates, use click instead for faster operation.
        """
        # Use _post_internal with expected_type
        return self._client._post_internal(
            "/tools-api/mouse/click-by-description",
            expected_type=M.ActionResponse,
            data={"taskDescription": user_element_description, "Mechanism": mechanism.value} # Use mechanism.value
        )

    def double_click_by_description(self, user_element_description: str,
                                   mechanism: M.MechanismType = M.MechanismType.SCREEN_GRASP2) -> Optional[M.ActionResponse]: # Update return type hint and mechanism type
        """
        Uses AI vision to find and double-click a UI element based on description.

        Args:
            user_element_description: Natural language description of element
                                     (be specific and include unique identifiers)
            mechanism: The AI mechanism to use for finding the element (defaults to ScreenGrasp2)

        Returns:
            Action response with success status and coordinates or None on error

        Note:
            If you know the exact coordinates, use double_click instead for faster operation.
        """
        # Use _post_internal with expected_type
        return self._client._post_internal(
            "/tools-api/mouse/doubleclick-by-description",
            expected_type=M.ActionResponse,
            data={"taskDescription": user_element_description, "Mechanism": mechanism.value} # Use mechanism.value
        )

    def drag_by_description(self, start_element_description: str,
                           end_element_description: str) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Uses AI vision to drag from source to target elements based on descriptions.

        Args:
            start_element_description: Natural language description of source element
            end_element_description: Natural language description of target element

        Returns:
            Action response with success status and coordinates or None on error

        Note:
            If you know the exact coordinates, use drag instead for faster operation.
        """
        # Use _post_internal with expected_type
        return self._client._post_internal(
            "/tools-api/mouse/drag-by-description",
            expected_type=M.ActionResponse,
            data={"startElementDescription": start_element_description, "endElementDescription": end_element_description}
        )

    def right_click_by_description(self, user_element_description: str,
                                  mechanism: M.MechanismType = M.MechanismType.SCREEN_GRASP2) -> Optional[M.ActionResponse]: # Update return type hint and mechanism type
        """
        Uses AI vision to find and right-click a UI element based on description.

        Args:
            user_element_description: Natural language description of element
                                     (be specific and include unique identifiers)
            mechanism: The AI mechanism to use for finding the element (defaults to ScreenGrasp2)

        Returns:
            Action response with success status and coordinates or None on error

        Note:
            If you know the exact coordinates, use right_click instead for faster operation.
        """
        # Use _post_internal with expected_type
        return self._client._post_internal(
            "/tools-api/mouse/rightclick-by-description",
            expected_type=M.ActionResponse,
            data={"taskDescription": user_element_description, "Mechanism": mechanism.value} # Use mechanism.value
        )

    def move_by_description(self, user_element_description: str,
                           mechanism: M.MechanismType = M.MechanismType.SCREEN_GRASP2) -> Optional[M.ActionResponse]: # Update return type hint and mechanism type
        """
        Uses AI vision to move mouse cursor to element based on description.

        Args:
            user_element_description: Natural language description of element
                                     (be specific and include unique identifiers)
            mechanism: The AI mechanism to use for finding the element (defaults to ScreenGrasp2)

        Returns:
            Action response with success status and coordinates or None on error

        Note:
            If you know the exact coordinates, use move instead for faster operation.
        """
        # Use _post_internal with expected_type
        return self._client._post_internal(
            "/tools-api/mouse/move-by-description",
            expected_type=M.ActionResponse,
            data={"taskDescription": user_element_description, "Mechanism": mechanism.value} # Use mechanism.value
        )

    def __str__(self) -> str:
        """Return a string representation of the MouseApi class."""
        return "MouseApi"


class KeyboardApi:
    """API endpoints for keyboard operations."""

    def __init__(self, client: 'SmoothOperatorClient'): # Add type hint
        """
        Initialize the KeyboardApi.

        Args:
            client: The SmoothOperatorClient instance
        """
        self._client = client

    def type(self, text: str) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Type text at the current cursor position.

        Args:
            text: Text to type

        Returns:
            Action response or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/keyboard/type", expected_type=M.ActionResponse, data={"text": text})

    def press(self, key: str) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Presses key or hotkey combination (e.g. "Ctrl+C" or "Alt+F4").

        Args:
            key: Key name or combination

        Returns:
            Action response with success status or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/keyboard/press", expected_type=M.ActionResponse, data={"key": key})

    def type_at_element(self, element_description: str, text_to_type: str) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Find a UI element based on a text description and type text into it.

        Args:
            element_description: Text description of the UI element
            text_to_type: Text to type

        Returns:
            Action response or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal(
            "/tools-api/keyboard/type-at-element",
            expected_type=M.ActionResponse,
            data={"elementDescription": element_description, "textToType": text_to_type}
        )

    def __str__(self) -> str:
        """Return a string representation of the KeyboardApi class."""
        return "KeyboardApi"


class ChromeApi:
    """API endpoints for Chrome browser operations."""

    def __init__(self, client: 'SmoothOperatorClient'): # Add type hint
        """
        Initialize the ChromeApi.

        Args:
            client: The SmoothOperatorClient instance
        """
        self._client = client

    def open_chrome(self, url: Optional[str] = None, strategy: Optional[str] = None) -> Optional[M.SimpleResponse]: # Update return type hint
        """
        Opens Chrome browser (Playwright-managed instance).

        Args:
            url: Optional URL to navigate to immediately
            strategy: Optional strategy for opening Chrome

        Returns:
            SimpleResponse indicating success or failure or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/system/open-chrome", expected_type=M.SimpleResponse, data={"url": url, "strategy": strategy})

    def explain_current_tab(self) -> Optional[M.ChromeTabDetails]: # Update return type hint
        """
        Gets detailed analysis of current Chrome tab including interactive elements.

        Returns:
            ChromeTabDetails with CSS selectors for key elements or None on error

        Note:
            Requires Chrome to be opened via open_chrome first
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/chrome/current-tab/explain", expected_type=M.ChromeTabDetails, data={})

    def navigate(self, url: str) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Navigate to a URL in the current Chrome tab.

        Args:
            url: URL to navigate to

        Returns:
            Action response or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/chrome/navigate", expected_type=M.ActionResponse, data={"url": url})

    def reload(self) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Reload the current Chrome tab.

        Returns:
            Action response or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/chrome/reload", expected_type=M.ActionResponse, data={})

    def new_tab(self, url: Optional[str] = None) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Open a new Chrome tab.

        Args:
            url: Optional URL to navigate to

        Returns:
            Action response or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/chrome/new-tab", expected_type=M.ActionResponse, data={"url": url})

    def click_element(self, selector: str) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Clicks element in Chrome tab using CSS selector.

        Args:
            selector: CSS selector from explain_current_tab

        Returns:
            Action response with success status or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/chrome/click-element", expected_type=M.ActionResponse, data={"selector": selector})

    def go_back(self) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Navigate back in the current Chrome tab.

        Returns:
            Action response or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/chrome/go-back", expected_type=M.ActionResponse, data={})

    def simulate_input(self, selector: str, text: str) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Simulate input in an element in the current Chrome tab.

        Args:
            selector: CSS selector of the element to input text into
            text: Text to input

        Returns:
            Action response or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/chrome/simulate-input", expected_type=M.ActionResponse, data={"selector": selector, "text": text})

    def get_dom(self) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Get the DOM of the current Chrome tab.

        Returns:
            Action response with DOM content or None on error
        """
        # Use _post_internal with expected_type
        # The response might contain the DOM in the 'Data' field, ActionResponse handles this
        return self._client._post_internal("/tools-api/chrome/get-dom", expected_type=M.ActionResponse, data={})

    def get_text(self) -> Optional[M.ActionResponse]: # Update return type hint
        """
        Get the text content of the current Chrome tab.

        Returns:
            Action response with text content or None on error
        """
        # Use _post_internal with expected_type
        # The response might contain the text in the 'Data' field, ActionResponse handles this
        return self._client._post_internal("/tools-api/chrome/get-text", expected_type=M.ActionResponse, data={})

    def execute_script(self, script: str) -> Optional[M.ChromeScriptResponse]: # Update return type hint
        """
        Executes JavaScript in Chrome tab and returns result.

        Args:
            script: JavaScript code to run

        Returns:
            ChromeScriptResponse with execution result or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/chrome/execute-script", expected_type=M.ChromeScriptResponse, data={"script": script})

    def generate_and_execute_script(self, task_description: str) -> Optional[M.ChromeScriptResponse]: # Update return type hint
        """
        Generate and execute JavaScript based on a description.

        Args:
            task_description: Description of what the JavaScript should do

        Returns:
            ChromeScriptResponse with execution result or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal(
            "/tools-api/chrome/generate-and-execute-script",
            expected_type=M.ChromeScriptResponse,
            data={"taskDescription": task_description}
        )

    def __str__(self) -> str:
        """Return a string representation of the ChromeApi class."""
        return "ChromeApi"


class AutomationApi:
    """API endpoints for Windows automation operations."""

    def __init__(self, client: 'SmoothOperatorClient'): # Add type hint
        """
        Initialize the AutomationApi.

        Args:
            client: The SmoothOperatorClient instance
        """
        self._client = client

    # Note: open_application is also available under SystemApi
    def open_application(self, app_name_or_path: str) -> Optional[M.SimpleResponse]: # Update return type hint
        """
        Launches an application by path or name.

        Args:
            app_name_or_path: Full path to executable or application name,
                             alternatively exe name if in path (e.g. notepad, calc)

        Returns:
            SimpleResponse indicating success or failure or None on error
        """
        # Use _post_internal with expected_type
        # Note: This endpoint exists under /system/, not /automation/
        return self._client._post_internal("/tools-api/system/open-application", expected_type=M.SimpleResponse, data={"appNameOrPath": app_name_or_path})

    def invoke(self, element_id: str) -> Optional[M.SimpleResponse]: # Update return type hint
        """
        Invokes default action on Windows UI element (e.g. click button).

        Args:
            element_id: Element ID from get_overview/get_details

        Returns:
            SimpleResponse indicating success or failure or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/automation/invoke", expected_type=M.SimpleResponse, data={"elementId": element_id})

    def set_value(self, element_id: str, value: str) -> Optional[M.SimpleResponse]: # Update return type hint
        """
        Set the value of a UI element.

        Args:
            element_id: ID of the UI element
            value: Value to set

        Returns:
            SimpleResponse indicating success or failure or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/automation/set-value", expected_type=M.SimpleResponse, data={"elementId": element_id, "value": value})

    def set_focus(self, element_id: str) -> Optional[M.SimpleResponse]: # Update return type hint
        """
        Set focus to a UI element.

        Args:
            element_id: ID of the UI element

        Returns:
            SimpleResponse indicating success or failure or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/automation/set-focus", expected_type=M.SimpleResponse, data={"elementId": element_id})

    # Note: get_window_details is also available under SystemApi
    def get_window_details(self, window_id: str) -> Optional[M.WindowDetailInfosDTO]: # Update return type hint
        """
        Gets detailed UI automation information for a window.

        Args:
            window_id: Window ID from get_overview

        Returns:
            WindowDetailInfosDTO with element hierarchy and properties or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/automation/get-details", expected_type=M.WindowDetailInfosDTO, data={"windowId": window_id})

    def bring_to_front(self, window_id: str) -> Optional[M.SimpleResponse]: # Update return type hint
        """
        Bring a window to the front.

        Args:
            window_id: ID of the window

        Returns:
            SimpleResponse indicating success or failure or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/automation/bring-to-front", expected_type=M.SimpleResponse, data={"windowId": window_id})

    def __str__(self) -> str:
        """Return a string representation of the AutomationApi class."""
        return "AutomationApi"


class CodeApi:
    """API endpoints for code execution operations."""

    def __init__(self, client: 'SmoothOperatorClient'): # Add type hint
        """
        Initialize the CodeApi.

        Args:
            client: The SmoothOperatorClient instance
        """
        self._client = client

    def execute_csharp(self, code: str) -> Optional[M.CSharpCodeResponse]: # Update return type hint
        """
        Executes C# code on server and returns output.

        Args:
            code: C# code to run

        Returns:
            CSharpCodeResponse with execution result or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal("/tools-api/code/csharp", expected_type=M.CSharpCodeResponse, data={"code": code})

    def generate_and_execute_csharp(self, task_description: str) -> Optional[M.CSharpCodeResponse]: # Update return type hint
        """
        Generate and execute C# code based on a description.

        Args:
            task_description: Description of what the C# code should do,
                             include error feedback if a previous try wasn't successful

        Returns:
            CSharpCodeResponse with execution result or None on error
        """
        # Use _post_internal with expected_type
        return self._client._post_internal(
            "/tools-api/code/csharp/generate-and-execute",
            expected_type=M.CSharpCodeResponse,
            data={"taskDescription": task_description}
        )

    def __str__(self) -> str:
        """Return a string representation of the CodeApi class."""
        return "CodeApi"
