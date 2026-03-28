TURBULENCE_MODELS = {
    "RANS": {
        "kOmegaSST": {
            "simulationType": "RAS",
            "modelKeyword": "kOmegaSST",
            "fields": ["k", "omega"],
            "coeffs": {}
        },
        "kEpsilon": {
            "simulationType": "RAS",
            "modelKeyword": "kEpsilon",
            "fields": ["k", "epsilon"],
            "coeffs": {
                "Cmu": 0.09,
                "C1": 1.44,
                "C2": 1.92
            }
        }
    },
    "Laminar": {
        "laminar": {
            "simulationType": "laminar",
            "fields": [],
            "coeffs": {}
        }
    }
}