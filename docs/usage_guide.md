"""
Installation and Usage Guide for the Smooth Operator Agent Tools Python Library
"""

# Installation

## Using pip

The Smooth Operator Agent Tools Python library can be installed using pip:

```bash
pip install smooth-operator-agent-tools
```

This will automatically install the library and all its dependencies, including the server executable.

## From Source

To install from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/fstandhartinger/smooth-operator-python-client.git
   cd smooth-operator-python-client
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

# Basic Usage

## Initializing the Client

```python
from smooth_operator_agent_tools import SmoothOperatorClient

# Initialize the client
client = SmoothOperatorClient(api_key="YOUR_API_KEY")  # Get API key for free at https://screengrasp.com/api.html

# Start the server
client.start_server()

# Stop the server when done
client.stop_server()
```

You can also use the client as a context manager:

```python
from smooth_operator_agent_tools import SmoothOperatorClient

with SmoothOperatorClient() as client:
    client.start_server()
    # Use the client here
    # Server will be automatically stopped when exiting the context
```

## Taking Screenshots

```python
# Take a screenshot - returns image in a form that can easily be passed to LLMs
screenshot = client.screenshot.take()

# Access the screenshot data
image_bytes = screenshot.image_bytes
image_base64 = screenshot.image_base64
```

## Mouse Operations

```python
# Click at coordinates
client.mouse.click(500, 300)

# Right-click at coordinates
client.mouse.right_click(500, 300)

# Double-click at coordinates
client.mouse.double_click(500, 300)

# Drag from one position to another
client.mouse.drag(100, 100, 200, 200)

# Scroll at coordinates
client.mouse.scroll(500, 300, 5)  # Scroll down 5 clicks
client.mouse.scroll(500, 300, -5)  # Scroll up 5 clicks
```

## AI-Powered UI Interaction

```python
# Find and click a UI element by description
client.mouse.click_by_description("the Submit button")

# Find and right-click a UI element by description
client.mouse.right_click_by_description("the Context menu icon")

# Find and double-click a UI element by description
client.mouse.double_click_by_description("the File icon")

# Drag from one element to another by description
client.mouse.drag_by_description("the invoice pdf file", "the 'invoices' folder")
```

## Keyboard Operations

```python
# Type text
client.keyboard.type("Hello, world!")

# Press a key combination
client.keyboard.press("Ctrl+C")
client.keyboard.press("Alt+F4")

# Type text in a UI element
client.keyboard.type_at_element("the Username field", "user123")
```

## Chrome Browser Control

```python
# Open Chrome browser
client.chrome.open_chrome("https://www.example.com")

# Navigate to a URL
client.chrome.navigate("https://www.google.com")

# Get information about the current tab
# Can be used to find likely interactable elements in the page
# Marks all html elements with robust CSS selectors for use
# in functions like click_element() or simulate_input()
# Response can also be passed to LLM to pick the right selector
tab_details = client.chrome.explain_current_tab()

# Click an element using CSS selector
client.chrome.click_element("#search-button")

# Input text into a form field
client.chrome.simulate_input("#username", "user123")

# Execute JavaScript
result = client.chrome.execute_script("return document.title")

# Generate and execute JavaScript based on a description
result = client.chrome.generate_and_execute_script("Extract all links from the page")
```

## System Operations

```python
# Get system overview
# Contains list of windows, available apps on the system,
# detailed infos about the currently focused ui element and window.
# Can be used as a source of ui element ids for use in automation functions 
# like invoke() (=click) or set_value().
# Can be used as a source of window ids for get_window_details(window_id).
# Consider sending the json serialized form of this result to a LLM, together
# with a task description, the form is chosen to be LLM friendly, the LLM
# sould be able to find the relevand ui element ids and windows ids like that.
overview = client.system.get_overview()

# Open an application
client.system.open_application("notepad")

# Get window details - contains the ui automation tree of elements.
# Consider using the response in a LLM prompt.
window_id = overview.windows[0].id
window_details = client.system.get_window_details(window_id)
```

## Windows Automation

```python
# Click a UI element by description
# element ids can be acquired from get_overview() and get_window_details()
client.automation.invoke(element_id)

# Type text in a UI element
# element ids can be acquired from get_overview() and get_window_details()
client.automation.set_value(element_id, "john doe")

# Bring a window to the front
client.automation.bring_to_front(window_id)
```

## Code Execution

```python
# Execute C# code
result = client.code.execute_csharp("return 2 + 2;")

# Generate and execute C# code based on a description - example 1
result = client.code.generate_and_execute_csharp("Calculate the factorial of 5")

# Generate and execute C# code based on a description - example 2
result = client.code.generate_and_execute_csharp("Return content of the biggest file in folder c:\\temp")

# Generate and execute C# code based on a description - example 3
result = client.code.generate_and_execute_csharp("Connect to Outlook via Interop and return text and date of the latest email from pricelist@vendor.com")
```

# Advanced Usage

## Using Different AI Mechanisms

For AI-vision powered operations (provided by Screengrasp.com), you can specify different AI mechanisms:

```python
from smooth_operator_agent_tools import MechanismType

# Use a different AI mechanism
client.mouse.click_by_description("the Submit button", mechanism=MechanismType.OPENAI_COMPUTER_USE)
```

## Converting Responses to JSON - use LLMs to analyze

Most response objects have a `to_json_string()` method that converts the response to a JSON string:

```python
# Get a response
screenshot = client.screenshot.take()

# Convert to JSON string
json_str = screenshot.to_json_string()

# Use the JSON string (e.g., pass it to a language model)
print(json_str)
```

It is a recommended pattern to use these JSON strings with LLMs to analyze the content.

For example you can prompt GPT-4o to extract the CSS selector of "the UI element that can be clicked to submit the form" by providing a textual instruction and the JSON string in a prompt. 

Use GPT-4o's JSON mode (for some LLMs also called structured output) to ensure it answers in a form you can easily parse.

# Platform Support

The Smooth Operator Agent Tools Python library is designed to work on Windows platforms, as the server executable is a Windows application. Support for other platforms may be added in the future.
