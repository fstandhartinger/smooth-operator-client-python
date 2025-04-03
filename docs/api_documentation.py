"""
API documentation for the Smooth Operator Agent Tools Python library.

This module provides detailed documentation for all the classes and methods
in the Smooth Operator Agent Tools Python library.
"""

# Main Client
SmoothOperatorClient_doc = """
Main client for the Smooth Operator Agent Tools API.

This class is the main entry point for the Smooth Operator Agent Tools library.
It manages the server process and provides access to all the API categories.
Requires a Screengrasp.com API key for AI-powered features.

Setup Examples:
    ```python
    from smooth_operator_agent_tools import SmoothOperatorClient

    # Initialize the client (Get API key for free at https://screengrasp.com/api.html)
    client = SmoothOperatorClient(api_key="YOUR_API_KEY")

    # Start the server
    client.start_server()

    # --- Use the API --- 
    # screenshot = client.screenshot.take()
    # overview = client.system.get_overview()

    # Stop the server when done
    client.stop_server()
    ```

Context Manager Usage:
    ```python
    from smooth_operator_agent_tools import SmoothOperatorClient

    with SmoothOperatorClient(api_key="YOUR_API_KEY") as client:
        client.start_server()
        # Use the client here
        # Server will be automatically stopped when exiting the context
    ```
"""

# API Categories
ScreenshotApi_doc = """
API endpoints for screenshot and analysis operations.

Provides methods for taking screenshots and using AI (via Screengrasp.com)
to find UI elements based on visual descriptions.

Example:
    ```python
    # Take a screenshot (returns base64 and bytes)
    screenshot = client.screenshot.take()
    image_base64 = screenshot.image_base64

    # Find a UI element by description using AI
    element_coords = client.screenshot.find_ui_element("Submit button")
    ```
"""

SystemApi_doc = """
API endpoints for system operations.

Provides methods for getting system/window information (useful for context and finding IDs),
and managing applications.

Example:
    ```python
    # Get detailed system overview (open windows, focus info, etc.)
    # Useful for getting window/element IDs for other functions.
    # Consider passing the JSON output to an LLM for analysis.
    overview = client.system.get_overview()
    window_id = overview.windows[0].id # Example: Get first window ID

    # Get detailed UI element tree for a specific window
    # Useful for getting element IDs. Consider passing JSON to an LLM.
    window_details = client.system.get_window_details(window_id)

    # Open Chrome browser
    client.system.open_chrome("https://www.example.com")

    # Open an application
    client.system.open_application("notepad")
    ```
"""

MouseApi_doc = """
API endpoints for mouse operations.

Provides methods for controlling the mouse cursor, performing clicks/drags,
and using AI (via Screengrasp.com) to interact with elements by description.

Example:
    ```python
    # Move the mouse cursor
    client.mouse.move(500, 300)

    # Click at coordinates
    client.mouse.click(500, 300)

    # Find and click a UI element by description using AI
    client.mouse.click_by_description("Submit button")

    # Find and drag an element to another by description using AI
    client.mouse.drag_by_description("file icon", "trash can icon")
    ```
"""

KeyboardApi_doc = """
API endpoints for keyboard operations.

Provides methods for typing text, sending key combinations, and typing into
UI elements found by description (using AI via Screengrasp.com).

Example:
    ```python
    # Type text
    client.keyboard.type("Hello, world!")

    # Press a key combination
    client.keyboard.press("Ctrl+C")

    # Find a UI element by description and type into it using AI
    client.keyboard.type_at_element("Username field", "user123")
    ```
"""

ChromeApi_doc = """
API endpoints for Chrome browser operations.

Provides methods for controlling a Playwright-managed Chrome instance,
including navigation, interaction via CSS selectors, and script execution.

Example:
    ```python
    # Open Chrome browser
    client.chrome.open_chrome("https://www.example.com")

    # Navigate to a URL
    client.chrome.navigate("https://www.google.com")

    # Get details of the current tab (DOM structure, potential interaction points)
    # Useful for finding CSS selectors. Consider passing JSON to an LLM.
    tab_details = client.chrome.explain_current_tab()
    # css_selector = find_selector_via_llm(tab_details.to_json_string(), "search input")

    # Click an element using CSS selector
    client.chrome.click_element("#search-button") # Example selector

    # Simulate typing into an element using CSS selector
    client.chrome.simulate_input("textarea[name='q']", "Smooth Operator") # Example selector

    # Execute JavaScript
    title = client.chrome.execute_script("return document.title")

    # Generate and execute JavaScript based on a task description
    result = client.chrome.generate_and_execute_script("Extract all H2 tags text content")
    ```
"""

AutomationApi_doc = """
API endpoints for Windows automation operations.

Provides methods for interacting with Windows UI elements using their
automation IDs (obtained typically from `system.get_overview` or `system.get_window_details`).

Example:
    ```python
    # Assuming element_id and window_id are obtained from system.get_overview() or system.get_window_details()
    element_id = "..."
    window_id = "..."

    # Invoke the default action on an element (e.g., click a button)
    client.automation.invoke(element_id)

    # Set the value of an element (e.g., type in a text box)
    client.automation.set_value(element_id, "Some text")

    # Set focus to an element
    client.automation.set_focus(element_id)

    # Bring a window to the front
    client.automation.bring_to_front(window_id)
    ```
"""

CodeApi_doc = """
API endpoints for code execution operations.

Provides methods for executing C# code on the server, either directly
or generated by AI based on a task description.

Example:
    ```python
    # Execute C# code
    result = client.code.execute_csharp("return System.DateTime.Now.ToString();")

    # Generate and execute C# code based on a description
    result = client.code.generate_and_execute_csharp("Return the current user name")
    ```
"""

# Models
Models_doc = """
Data models for the Smooth Operator Agent Tools.

Provides Pydantic models for requests and responses. Most response models
have a `to_json_string()` method, useful for serialization, especially
when passing structured data to Large Language Models (LLMs).

Example:
    ```python
    from smooth_operator_agent_tools import models as M

    # Example: Create an ActionResponse instance
    response = M.ActionResponse(success=True, message="Done")

    # Convert to JSON string (e.g., for LLM input)
    json_str = response.to_json_string()
    # llm_result = call_llm("Analyze this result:" + json_str)
    ```
"""

# Server Utils
ServerUtils_doc = """
Server management utilities for the Smooth Operator Agent Tools.

Provides functions for finding and checking the server executable installation.
These are mainly used internally by the `SmoothOperatorClient`.

Example:
    ```python
    from smooth_operator_agent_tools.server_utils import get_server_installation_path, is_server_installed

    # Get the server installation path
    path = get_server_installation_path()

    # Check if the server is installed
    installed = is_server_installed()
    ```
"""
