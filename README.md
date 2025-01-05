`````markdown:README.md
# 📸 Screenshot Organizer Agent

**Automate your screenshot management with ease!**

## 🚀 Features

- **AI-Powered Renaming:** Uses GPT-4o to give each screenshot a descriptive title.
- **Structured Organization:** Sorts screenshots into categorized folders.
- **Update Option:** Add new screenshots without renaming existing ones.
- **Easy Setup:** Simple command-line customization.

## 🛠 Installation

1. **Clone Repository**
    ```bash
    git clone https://github.com/yourusername/screenshot-organizer-agent.git
    cd screenshot-organizer-agent
    ```

2. **Setup Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Configure API Key**
    ```bash
    export OPENAI_API_KEY='your-api-key-here'  # Windows: set OPENAI_API_KEY='your-api-key-here'
    ```

## 🎯 Usage

Run the organizer with your screenshots folder:

```bash
python main.py -d /path/to/screenshots [--update] [--skip-renaming]
```

### Options

- `-d`, `--directory`: **Required.** Path to your screenshots.
- `--update`, `-u`: **Optional.** Update existing folders.
- `--skip-renaming`, `-sk`: **Optional.** Skip renaming files.

### Examples

1. **Organize Screenshots**
    ```bash
    python main.py -d /Users/yourname/Pictures/Screenshots
    ```

2. **Update without Renaming**
    ```bash
    python main.py -d /Users/yourname/Pictures/Screenshots --update --skip-renaming
    ```

## 📂 Project Structure

```
screenshot-organizer-agent/
├── main.py
├── tools.py
├── plan.md
├── README.md
└── requirements.txt
```

- **main.py:** Runs the organization process.
- **tools.py:** Helper functions.
- **plan.md:** Project roadmap.
- **requirements.txt:** Dependencies.

## 🤝 Contribute

Got ideas? Fork the repo and submit a pull request!

## 📝 License

[MIT License](LICENSE)

## 📬 Contact

Questions? [your.email@example.com](mailto:your.email@example.com)
`````
