# LLM Financial Image Scans

This project demonstrates how to combine chat-style prompting with image analysis to extract insights from financial statements. The repository contains a single notebook and sample balance-sheet images that can be executed in VS Code, Jupyter, or Google Colab without any web application layer.

## Contents
- `Financial_Image_Scans.ipynb` – End-to-end notebook covering the problem statement, prompt design, simulated AI extraction, and structured reporting.
- `assets/` – Sample balance-sheet and KPI dashboard images referenced by the notebook.

## Requirements
- Python 3.10+
- Libraries: `pandas`, `numpy`, `matplotlib`, `Pillow`

Install the dependencies via:
```bash
pip install pandas numpy matplotlib pillow
```

## Usage
1. Clone the repo and open `Financial_Image_Scans.ipynb` in your preferred notebook environment.
2. Run the cells sequentially to load the images, review the prompts, and generate the simulated analysis output.
3. Replace the sample images in `assets/` with your own financial scans to analyze different reports.

## Notes
- The notebook is intentionally self-contained and does not depend on `.vscode` or other folders from the original workspace.
- When supplying new images, ensure paths remain inside `assets/` and update captions/notes in the display section if needed.
