# Smooth Operator Agent Tools - Python Library

This is the official Python library implementation for Smooth Operator Agent Tools, a state-of-the-art toolkit for programmers developing Computer Use Agents on Windows systems.

## Overview

The Smooth Operator Agent Tools are a powerful toolkit that handles the complex tasks of interacting with the Windows Automation Tree and Playwright browser control, while providing advanced AI functions such as identifying UI elements through screenshots and textual descriptions.

This Python library provides a convenient wrapper around the Smooth Operator Tools Server API, allowing you to easily integrate these capabilities into your Python applications.

## Installation

```bash
pip install smooth-operator-agent-tools
```

## Prerequisites

### Google Chrome

The Smooth Operator Agent Tools library requires Google Chrome (or a compatible Chromium-based browser) to be installed on the system for browser automation features to work.

## Server Installation

The Smooth Operator client library includes a server component that needs to be installed in your application data directory. The server files are packaged with the library and will be automatically extracted on first use.

### First-Time Execution

When you first use the library, it will automatically:
1. Create the directory `%APPDATA%\SmoothOperator\AgentToolsServer` (or the equivalent on your OS)
2. Extract the server files from the package
3. Start the server process

Note that for Chrome automation features to work, you need to ensure Node.js and Playwright are installed as described in the Prerequisites section.

### For Application Installers

If you're building an application installer that includes this library, you should include steps to install Node.js and Playwright during your application's installation process for better user experience. See the Prerequisites section for the required installation steps.

## Usage

```python
from smooth_operator_agent_tools import SmoothOperatorClient

# Initialize the client with your API key, get it for free at https://screengrasp.com/api.html
client = SmoothOperatorClient(api_key="YOUR_API_KEY")

# Start the Server - this takes a moment
client.start_server()

# Take a screenshot
screenshot = client.screenshot.take()

# Get system overview
overview = client.system.get_overview()

# Perform a mouse click
client.mouse.click(500, 300)

# Find and click a UI element by description
client.mouse.click_by_description("Submit button")

# Type text
client.keyboard.type("Hello, world!")

# Control Chrome browser
client.chrome.open_chrome("https://www.example.com")
client.chrome.get_dom()

# You can also use the to_json_string() method on many objects
# to get a JSON string that can easily be used in a prompt to a LLM
# to utilize AI even more for automated decision making
```

## Features

- **Screenshot and Analysis**: Capture screenshots and analyze UI elements
- **Mouse Control**: Precise mouse operations using coordinates or AI-powered element detection
- **Keyboard Input**: Type text and send key combinations
- **Chrome Browser Control**: Navigate, interact with elements, and execute JavaScript
- **Windows Automation**: Interact with Windows applications and UI elements
- **System Operations**: Open applications and manage system state

## Documentation

For detailed API documentation, visit:

*   **[Usage Guide](docs/usage_guide.md):** Detailed examples and explanations for common use cases.
*   **[Example Project](https://github.com/fstandhartinger/smooth-operator-example-python):** Download, follow step by step instructions and have your first automation running in mintes.
*   **[Documentation](https://smooth-operator.online/agent-tools-api-docs/toolserverdocs):** Describes the endpoints of the local tools server the python client library communicates with.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
