"""Class order MUST match the order used in training (alphabetical folder names).
Override by placing a class_names.json (list of 10 strings) next to app.py."""

CLASS_NAMES = [
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

DISEASES = {
    "Tomato___Bacterial_spot": {
        "name": "Bacterial Spot", "healthy": False,
        "summary": "Small dark, water-soaked spots on leaves and fruit caused by Xanthomonas bacteria; spreads in warm, wet weather.",
        "organic": "Copper-based sprays and neem oil.",
        "chemical": "Bactericides such as streptomycin sulfate (where legally permitted).",
        "prevention": "Avoid overhead watering, rotate crops and use disease-free seed.",
    },
    "Tomato___Early_blight": {
        "name": "Early Blight", "healthy": False,
        "summary": "Brown spots with concentric rings (target-like), usually starting on older, lower leaves.",
        "organic": "Compost tea or garlic extract sprays.",
        "chemical": "Fungicides such as chlorothalonil.",
        "prevention": "Remove infected leaves, mulch, and increase air circulation.",
    },
    "Tomato___Late_blight": {
        "name": "Late Blight", "healthy": False,
        "summary": "Large, greasy grey-green blotches that turn brown; can destroy a crop within days in cool, humid weather.",
        "organic": "Potassium bicarbonate or copper fungicide (preventive).",
        "chemical": "Metalaxyl- or mancozeb-based fungicides.",
        "prevention": "Destroy infected plants promptly and keep foliage dry.",
    },
    "Tomato___Leaf_Mold": {
        "name": "Leaf Mold", "healthy": False,
        "summary": "Pale yellow patches on the upper leaf surface with olive-green mold underneath; common in humid greenhouses.",
        "organic": "Weekly baking soda or milk spray.",
        "chemical": "Chlorothalonil or mancozeb.",
        "prevention": "Improve ventilation and reduce humidity.",
    },
    "Tomato___Septoria_leaf_spot": {
        "name": "Septoria Leaf Spot", "healthy": False,
        "summary": "Many small circular spots with dark borders and grey centres, mostly on lower leaves.",
        "organic": "Neem oil or horsetail tea.",
        "chemical": "Chlorothalonil or copper fungicides.",
        "prevention": "Mulch the base of plants and avoid wetting leaves.",
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "name": "Spider Mites", "healthy": False,
        "summary": "Tiny pests causing fine yellow stippling and sometimes webbing, especially in hot, dry conditions.",
        "organic": "Insecticidal soap or neem oil.",
        "chemical": "Miticides such as abamectin.",
        "prevention": "Spray the undersides of leaves thoroughly and keep plants well watered.",
    },
    "Tomato___Target_Spot": {
        "name": "Target Spot", "healthy": False,
        "summary": "Brown lesions with concentric rings and a yellow halo on leaves, stems and fruit.",
        "organic": "Compost tea and copper sprays.",
        "chemical": "Fungicides containing chlorothalonil.",
        "prevention": "Remove and destroy infected plant debris.",
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "name": "Yellow Leaf Curl Virus", "healthy": False,
        "summary": "Upward-curling, yellowing leaves and stunted growth; spread by whiteflies. There is no cure once infected.",
        "organic": "Reflective mulches and neem oil to deter whiteflies.",
        "chemical": "Control whiteflies with products such as imidacloprid.",
        "prevention": "Plant resistant varieties and cover seedlings with insect netting.",
    },
    "Tomato___Tomato_mosaic_virus": {
        "name": "Tomato Mosaic Virus", "healthy": False,
        "summary": "Mottled light/dark green mosaic pattern and distorted leaves; spreads by touch and contaminated tools.",
        "organic": "No cure: remove and destroy infected plants.",
        "chemical": "No chemical cure; disinfect tools and hands.",
        "prevention": "Use resistant varieties, wash hands, and sterilise tools between plants.",
    },
    "Tomato___healthy": {
        "name": "Healthy Leaf", "healthy": True,
        "summary": "No signs of the diseases this model knows about. Your plant looks good!",
        "organic": "Keep up regular compost feeding and mulching.",
        "chemical": "No treatment needed.",
        "prevention": "Water at the base, space plants for airflow, and inspect leaves weekly.",
    },
}
