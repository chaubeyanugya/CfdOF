TURBULENCE_MODELS = {
    "RANS": {
        "kOmegaSST": {
            "simulationType": "RAS",
            "modelKeyword": "kOmegaSST",
            "fields": ["k", "omega"],
            "coeffs": {
                "alphaK1":    0.85,
                "alphaK2":    1.0,
                "alphaOmega1": 0.5,
                "alphaOmega2": 0.856,
                "gamma1":     0.5556,
                "gamma2":     0.44,
                "beta1":      0.075,
                "beta2":      0.0828,
                "betaStar":   0.09,
                "a1":         0.31,
                "b1":         1.0,
                "c1":         10.0,
            }
        },
        "kEpsilon": {
            "simulationType": "RAS",
            "modelKeyword": "kEpsilon",
            "fields": ["k", "epsilon"],
            "coeffs": {
                "Cmu":      0.09,
                "C1":       1.44,
                "C2":       1.92,
                "C3":      -0.33,
                "sigmak":   1.0,
                "sigmaEps": 1.3,
            }
        },
        "SpalartAllmaras": {
            "simulationType": "RAS",
            "modelKeyword": "SpalartAllmaras",
            "fields": ["nuTilda"],
            "coeffs": {
                "Cb1": 0.1355,
                "Cb2": 0.622,
                "Cw2": 0.3,
                "Cw3": 2.0,
                "Cv1": 7.1,
                "Cs":  0.3,
            }
        },
        "realizableKE": {
            "simulationType": "RAS",
            "modelKeyword": "realizableKE",
            "fields": ["k", "epsilon"],
            "coeffs": {
                "Cmu":      0.09,
                "A0":       4.0,
                "C2":       1.9,
                "sigmak":   1.0,
                "sigmaEps": 1.2,
            }
        },
    },
    "LES": {
        "kEqn": {
            "simulationType": "LES",
            "modelKeyword": "kEqn",
            "fields": ["k"],
            "coeffs": {
                "Ck": 0.094,
                "Ce": 1.048,
            }
        },
        "Smagorinsky": {
            "simulationType": "LES",
            "modelKeyword": "Smagorinsky",
            "fields": ["k"],
            "coeffs": {
                "Ck": 0.094,
                "Ce": 1.048,
            }
        },
        "WALE": {
            "simulationType": "LES",
            "modelKeyword": "WALE",
            "fields": ["k"],
            "coeffs": {
                "Ck": 0.094,
                "Ce": 1.048,
                "Cw": 0.325,
            }
        },
        "dynamicKEqn": {
            "simulationType": "LES",
            "modelKeyword": "dynamicKEqn",
            "fields": ["k"],
            "coeffs": {
                "Ck": 0.094,
                "Ce": 1.048,
            }
        },
    },
    "DES": {
        "kOmegaSSTDES": {
            "simulationType": "DES",
            "modelKeyword": "kOmegaSSTDES",
            "fields": ["k", "omega"],
            "coeffs": {
                "CDES": 0.65,
            }
        },
        "SpalartAllmarasDES": {
            "simulationType": "DES",
            "modelKeyword": "SpalartAllmarasDES",
            "fields": ["nuTilda"],
            "coeffs": {
                "CDES": 0.65,
            }
        },
    },
    "Laminar": {
        "laminar": {
            "simulationType": "laminar",
            "modelKeyword": "laminar",
            "fields": [],
            "coeffs": {}
        }
    },
}


def getModelCoefficients(modelName):
    for category in TURBULENCE_MODELS.values():
        if modelName in category:
            return category[modelName]["coeffs"].copy()  # .copy() prevents mutating master defaults
    return {}


def getOfKeyword(modelName):
    """Return the OpenFOAM modelKeyword for a given model name."""
    for category in TURBULENCE_MODELS.values():
        if modelName in category:
            return category[modelName].get("modelKeyword", modelName)
    return modelName


def getSimulationType(modelName):
    """Return the simulationType string (RAS, LES, DES, laminar) for a model."""
    for category in TURBULENCE_MODELS.values():
        if modelName in category:
            return category[modelName].get("simulationType", "RAS")
    return "RAS"


def getModelFields(modelName):
    """Return the list of OpenFOAM field files required by a model (e.g. ['k', 'omega'])."""
    for category in TURBULENCE_MODELS.values():
        if modelName in category:
            return category[modelName].get("fields", [])
    return []


def getModelsForCategory(category):
    """Return a list of model names for a given UI category string (RANS, LES, DES, Laminar)."""
    return list(TURBULENCE_MODELS.get(category, {}).keys())