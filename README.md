# Flavorly | Prom Cafe

**Curated Flavours for Every Palate**

Flavorly is an intelligent menu assistant designed for Prom Cafe. Powered by Google Gemini AI, it helps customers find exactly what they're craving using natural language queries, while accounting for dietary restrictions and group orders.

## Features

-   **AI-Powered Search**: Ask complex questions like "I need a vegan breakfast and a coffee" or "What's good for 3 people?".
-   **Dietary Filtering**: Automatically identifies and respects dietary tags (Vegan, Gluten-Free, etc.).
-   **Structured Recommendations**: Returns clear, itemized lists with pricing and totals.
-   **Premium UI**: A beautiful, responsive interface built with Tailwind CSS and modern design principles.

## Tech Stack

-   **Backend**: FastAPI, Python, SQLite, SQLAlchemy.
-   **AI**: Google Gemini 2.0 Flash.
-   **Frontend**: Vanilla JavaScript, HTML5, Tailwind CSS.
-   **Deployment**: Render.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sahabajalam/prom_cafe.git
    cd prom_cafe
    ```

2.  **Create a virtual environment:**
    ```bash
    uv venv
    # or
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your Gemini API key:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```

5.  **Run the application:**
    ```bash
    uvicorn backend.main:app --reload
    ```
    The app will be available at `http://localhost:8000`.

## Deployment

This project is configured for deployment on **Render**.

1.  Push your code to GitHub.
2.  Create a new **Web Service** on Render.
3.  Connect your GitHub repository.
4.  Render will automatically detect the `render.yaml` configuration.
5.  Add the `GEMINI_API_KEY` in the Environment Variables section.
6.  Deploy!

## License

[MIT](LICENSE)
