# Flask Model Server

This project hosts a Flask server that serves predictions from multiple models.

---

## How to Run the Server

1. **Set up a Virtual Environment**

    ```bash
    python -m venv venv
    ```

2. **Activate the Virtual Environment**

    - On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Server**
    ```bash
    flask run
    ```

---

## How to Add a New Model

1. **Create a New File inside the `models/` Directory**

2. **Define a Function with the `@register_model` Decorator**

    Example:

    ```python
    from .registry import register_modelstructure
    from PIL import Image
    import numpy as np


    @register_model("xo")  # Replace "xo" with your desired action name
    def xo_model(img: Image.Image) -> str:
        result = np.array(detect_tic_tac_toe(img)).flatten().tolist()

        m = {"X": 1, "O": 2, "-": 0}

        logger.info(f"Result: {result}")

        return ",".join([str(m[item]) for item in result])
    ```

    - The function **must**:
        - Take a `PIL.Image.Image` as input.
        - Return a **comma-separated** `string` as output.

3. **Model Files**

    - If your model requires any additional files, **add them to the `model_files/` directory**.
    - Use **clear and descriptive file names** based on your model's purpose.

    Example directory structure:

    ```
    model_files/
      ├── xo.pt
      ├── some_other_model_file.pt
    ```

---

## How to Call the API

-   **Method:** `POST`
-   **Endpoint:** `/predict`
-   **Query Parameter:** `action` (the action name you registered)
-   **Request Body:** raw **image binary buffer** (NOT multipart/form-data)
