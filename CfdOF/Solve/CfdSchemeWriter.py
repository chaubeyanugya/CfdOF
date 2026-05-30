# CfdOF/Solve/CfdSchemeWriter.py

FOAM_HEADER = """\
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      {obj};
}}
// * * * * * * * * * * * * * * * * * * * * * * * //
"""

# Turbulence model → which extra variables need solver entries
TURB_VARIABLES = {
    "kEpsilon":          ["k", "epsilon"],
    "kOmegaSST":         ["k", "omega"],
    "kOmega":            ["k", "omega"],
    "SpalartAllmaras":   ["nuTilda"],
    "realizableKE":      ["k", "epsilon"],
    "RNGkEpsilon":       ["k", "epsilon"],
    "LaminarModel":      [],
    "laminar":           [],
}

# Solvers that use SIMPLE (steady)
SIMPLE_SOLVERS  = {"simpleFoam", "rhoSimpleFoam", "buoyantSimpleFoam"}
# Solvers that use PIMPLE/PISO (transient)
PIMPLE_SOLVERS  = {"pimpleFoam", "pisoFoam", "buoyantPimpleFoam", "interFoam"}


#def writeFvSchemes(cfg, solver_name, transient, turbulence_model):
#    """
#    cfg             : CfdSolverConfig FreeCAD object (or None → use defaults)
#    solver_name     : str e.g. 'simpleFoam'
#    transient       : bool
#    turbulence_model: str e.g. 'kOmegaSST'
#    Returns         : str  (full fvSchemes file content)
#    """
#    # Auto-select ddtScheme if steady-state
#    if not transient:
#        ddt = "steadyState"
#    else:
#        ddt = cfg.DdtScheme if cfg else "Euler"
#
#    grad  = cfg.GradScheme   if cfg else "Gauss linear"
#    div   = cfg.DivScheme    if cfg else "Gauss linearUpwind grad(U)"
#    lap   = cfg.LapScheme    if cfg else "Gauss linear corrected"
#    interp= cfg.InterpScheme if cfg else "linear"
#
#    turb_divs = ""
#    for var in TURB_VARIABLES.get(turbulence_model, []):
#        turb_divs += f"    div(phi,{var})          Gauss upwind;\n"
#
#    content = FOAM_HEADER.format(obj="fvSchemes")
#    content += f"""
#ddtSchemes
#{{
#    default         {ddt};
#}}
#
#gradSchemes
#{{
#    default         {grad};
#    grad(U)         {grad};
#}}
#
#divSchemes
#{{
#    default         none;
#    div(phi,U)      {div};
#{turb_divs}}}
#
#laplacianSchemes
#{{
#    default         {lap};
#}}
#
#interpolationSchemes
#{{
#    default         {interp};
#}}
#
#snGradSchemes
#{{
#    default         corrected;
#}}
#
#fluxRequired
#{{
#    default         no;
#    p               ;
#}}
#"""
#    return content 

def writeFvSchemes(cfg, solver_name, transient, turbulence_model):
    """
    cfg             : CfdSolverConfig FreeCAD object (or None → use defaults)
    solver_name     : str e.g. 'simpleFoam'
    transient       : bool
    turbulence_model: str e.g. 'kOmegaSST'
    Returns         : str  (full fvSchemes file content)
    """
    if not transient:
        ddt = "steadyState"
    else:
        ddt = cfg.DdtScheme if cfg else "Euler"

    grad  = cfg.GradScheme   if cfg else "Gauss linear"
    div   = cfg.DivScheme    if cfg else "bounded Gauss upwind"
    lap   = cfg.LapScheme    if cfg else "Gauss linear corrected"
    interp= cfg.InterpScheme if cfg else "linear"

    turb_divs = ""
    for var in TURB_VARIABLES.get(turbulence_model, []):
        turb_divs += f"    div(phi,{var})          Gauss upwind;\n"

    content = FOAM_HEADER.format(obj="fvSchemes")
    content += f"""
ddtSchemes
{{
    default         {ddt};
}}

gradSchemes
{{
    default         {grad};
    grad(U)         {grad};
}}

divSchemes
{{
    default         none;
    div(phi,U)      {div};
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
{turb_divs}}}

laplacianSchemes
{{
    default         {lap};
}}

interpolationSchemes
{{
    default         {interp};
}}

snGradSchemes
{{
    default         corrected;
}}

fluxRequired
{{
    default         no;
    p               ;
}}
"""
    # Append the wallDist method unconditionally for turbulence
    if turbulence_model in ["kEpsilon", "kOmegaSST", "kOmega", "SpalartAllmaras", "realizableKE", "RNGkEpsilon"]:
        content += "\nwallDist\n{\n    method meshWave;\n}\n"

    return content



#def writeFvSolution(cfg, solver_name, transient, turbulence_model):
#    """
#    Returns : str  (full fvSolution file content)
#    """
#    p_solver  = cfg.PressureSolver   if cfg else "GAMG"
#    u_solver  = cfg.VelocitySolver   if cfg else "smoothSolver"
#    t_solver  = cfg.TurbSolver       if cfg else "smoothSolver"
#    p_tol     = cfg.PTolerance       if cfg else 1e-6
#    u_tol     = cfg.UTolerance       if cfg else 1e-5
#    relax_p   = cfg.RelaxP           if cfg else 0.3
#    relax_u   = cfg.RelaxU           if cfg else 0.7
#    algorithm = cfg.Algorithm        if cfg else ("SIMPLE" if not transient else "PIMPLE")
#    n_outer   = cfg.NOuterCorrectors if cfg else 50
#    n_corr    = cfg.NCorrectors      if cfg else 2
#
#    # Build turbulence variable solver blocks
#    turb_vars = TURB_VARIABLES.get(turbulence_model, [])
#    turb_blocks = ""
#    for var in turb_vars:
#        turb_blocks += f"""
#    {var}
#    {{
#        solver          {t_solver};
#        smoother        GaussSeidel;
#        tolerance       {u_tol};
#        relTol          0.1;
#    }}
#"""
#
#    turb_relax = "".join(f"        {v}    0.5;\n" for v in turb_vars)
#
#    # Build algorithm block
#    if algorithm == "SIMPLE" or not transient:
#        algo_block = f"""
#SIMPLE
#{{
#    nNonOrthogonalCorrectors    2;
#    consistent                  yes;
#    residualControl
#    {{
#        p               {p_tol};
#        U               {u_tol};
#    }}
#}}
#
#relaxationFactors
#{{
#    fields
#    {{
#        p               {relax_p};
#    }}
#    equations
#    {{
#        U               {relax_u};
#{turb_relax}    }}
#}}
#"""
#    else:  # PIMPLE / PISO
#        algo_block = f"""
#PIMPLE
#{{
#    nOuterCorrectors    {n_outer};
#    nCorrectors         {n_corr};
#    nNonOrthogonalCorrectors 1;
#    pRefCell            0;
#    pRefValue           0;
#}}
#
#relaxationFactors
#{{
#    equations
#    {{
#        U               {relax_u};
#{turb_relax}    }}
#}}
#"""
#
#    content = FOAM_HEADER.format(obj="fvSolution")
#    content += f"""
#solvers
#{{
#    p
#    {{
#        solver          {p_solver};
#        smoother        GaussSeidel;
#        agglomerator    faceAreaPair;
#        mergeLevels     1;
#        nCellsInCoarsestLevel 10;
#        tolerance       {p_tol};
#        relTol          0.01;
#    }}
#
#    pFinal
#    {{
#        $p;
#        relTol          0;
#    }}
#
#    U
#    {{
#        solver          {u_solver};
#        smoother        symGaussSeidel;
#        tolerance       {u_tol};
#        relTol          0.1;
#    }}
#{turb_blocks}}}
#{algo_block}
#"""
#    return content

def writeFvSolution(cfg, solver_name, transient, turbulence_model):
    """
    Returns : str  (full fvSolution file content)
    """
    p_solver  = cfg.PressureSolver   if cfg else "GAMG"
    u_solver  = cfg.VelocitySolver   if cfg else "smoothSolver"
    t_solver  = cfg.TurbSolver       if cfg else "smoothSolver"
    p_tol     = cfg.PTolerance       if cfg else 1e-6
    u_tol     = cfg.UTolerance       if cfg else 1e-5
    relax_p   = cfg.RelaxP           if cfg else 0.3
    relax_u   = cfg.RelaxU           if cfg else 0.7
    algorithm = cfg.Algorithm        if cfg else ("SIMPLE" if not transient else "PIMPLE")
    n_outer   = cfg.NOuterCorrectors if cfg else 50
    n_corr    = cfg.NCorrectors      if cfg else 2

    turb_vars = TURB_VARIABLES.get(turbulence_model, [])
    turb_blocks = ""
    for var in turb_vars:
        turb_blocks += f"""
    "({var}|{var}Final)"
    {{
        solver          {t_solver};
        smoother        GaussSeidel;
        tolerance       {u_tol};
        relTol          0.1;
    }}
"""

    turb_relax = "".join(f"        {v}    0.5;\n" for v in turb_vars)

    if algorithm == "SIMPLE" or not transient:
        algo_block = f"""
SIMPLE
{{
    nNonOrthogonalCorrectors    2;
    consistent                  yes;
    residualControl
    {{
        p               {p_tol};
        U               {u_tol};
    }}
}}

relaxationFactors
{{
    fields
    {{
        p               {relax_p};
    }}
    equations
    {{
        U               {relax_u};
{turb_relax}    }}
}}
"""
    else:  # PIMPLE / PISO
        algo_block = f"""
PIMPLE
{{
    nOuterCorrectors    {n_outer};
    nCorrectors         {n_corr};
    nNonOrthogonalCorrectors 1;
    pRefCell            0;
    pRefValue           0;
}}

relaxationFactors
{{
    equations
    {{
        U               {relax_u};
{turb_relax}    }}
}}
"""

    content = FOAM_HEADER.format(obj="fvSolution")
    content += f"""
solvers
{{
    p
    {{
        solver          {p_solver};
        smoother        GaussSeidel;
        agglomerator    faceAreaPair;
        mergeLevels     1;
        nCellsInCoarsestLevel 10;
        tolerance       {p_tol};
        relTol          0.01;
    }}

    pFinal
    {{
        $p;
        relTol          0;
    }}

    "(U|UFinal)"
    {{
        solver          {u_solver};
        smoother        symGaussSeidel;
        tolerance       {u_tol};
        relTol          0.1;
    }}

    Phi
    {{
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0;
    }}
{turb_blocks}}}
{algo_block}
"""
    return content