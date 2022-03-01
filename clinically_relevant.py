"""
Data from MaxQuant contains gene names and protein names.
However, it is difficult to determine if the MaxQuant protein identification matches a protein in a list of
    clinically relevant proteins. This is because the MaxQuant identification may list one protein ('Serum albumin')
    or a list of proteins, ultimately corresponding to the same protein ('Plasma kallikrein;Plasma kallikrein heavy chain;Plasma kallikrein light chain')

This difficulty in matching protein names means a table must be created matching clinically relevant protein names to MaxQuant identifications
We are also able to pair possible gene names with


Two possible data structures exist for this
1) A dictionary mapping clinically relevant protein names to results from MaxQuant. This also contains a map of any gene names that match
    a family of proteins, such as "Alanine aminotransferase", which is a family of proteins
    {
        ["Clinically Relevant Protein Name 1", "MaxQuant Protein 1;MaxQuant Protein 2;MaxQuant Protein 3"]: ["Gene 1", "Gene 2", "Gene 3"],
        ["Clinically Relevant Protein Name 2", "MaxQuant Protein 4"]:                                       ["Gene 4", "Gene 5"],
        ["Clinically Relevant Protein Name 3", "MaxQuant Protein 5;MaxQuant Protein 6"]:                    ["Gene 6", "Gene 7", "Gene 8", "Gene 9"]
    }

2) A dictionary mapping clinically relevant protein names directly to MaxQuant identifications. This has the clinically relevant protein names as
    keys and ANY MaxQuant identifications that match as values. This has the disadvantage of not knowing the corresponding genes, if this is wanted, but it
    would require less work to implement

    The MaxQuant identifications should match any family of clinically relevant protein names
    For example, the clinically relevant protein Immunoglobulin Gamma is a family of immunoglobulin.
    MaxQuant identifies the following:
        - Ig gamma-3 chain C region
        - Ig gamma-2 chain C region
        - Ig gamma-4 chain C region
    Each of these MaxQuant identifications should be paired to the clinically relevant protein IgG

    {
        "Clinically Relevant Protein Name 1": ["MaxQuant Protein 1;MaxQuant Protein 2", "MaxQuant Protein 3"]
        "Clinically Relevant Protein Name 2": ["MaxQuant Protein 4", "MaxQuant Protein 5;MaxQuant Protein 6"]
        "Clinically Relevant Protein Name 3": ["MaxQuant Protein 7"]
    }


With the current data (c18/direct + sdc/urea), all clinically relevant proteins may not be available between these
    data sets. Assuming this is the case, multiple avenues exist:
    (BETTER) 1) Contact MaxQuant support to see if a list is available of ALL protein identifications MaxQuant is capable of
        This would allow us to cross-check with 100% certainty between MaxQuant and the clinically relevant list
    (WORSE)  2) If the protein is not found in the above dictionary, perform a fuzzy search of the MaxQuant protein in question
        If the MaxQuant protein matches one of the clinically relevant protein with a score greater than 80%,
        add it to a "found proteins" list.
        This will run into issues if the MaxQuant protein is found as a subset of the clinically relevant protein
            but the proteins are not a true match

Using this information, we can determine if the clinically relevant protein matches the MaxQuant identification
    This could be done using a dictionary with clinically relevant proteins as keys and MaxQuant identification as values,
    but it would be easier to have the gene information immediately available as well
"""

# {"Clinically Relevant Protein 1": "MaxQuant Protein 1;MaxQuant Protein 2"}
protein_match: dict[str, list[str]] = {
    "Acid phosphatase": [],
    "IgG": [
        "Ig gamma",
        "Ig gamma-1 chain C region",
        "Ig gamma-3 chain C region",
        "Ig gamma-2 chain C region",
        "Ig gamma-4 chain C region",
    ],
    "Alanine aminotransferase (ALT or SGPT)": [],
    "Albumin": ["Serum albumin"],
    "Aldolase": [],
    "Alkaline phosphatase (ALP)": [],
    "Alpha-1-Acid glycoprotein (orosomucoid)": [
        "Alpha-1-acid glycoprotein 1",
        "Alpha-1-acid glycoprotein 2",
        "Alpha-1-acid glycoprotein 3",
    ],
    "Alpha-1-Antitrypsin": ["Alpha-1-antitrypsin"],
    "Alpha-2-Antiplasmin": ["Alpha-2-Antiplasmin"],
    "Alpha-2-HS-glycoprotein": [
        "Alpha-2-HS-glycoprotein;Alpha-2-HS-glycoprotein chain A;Alpha-2-HS-glycoprotein chain B"
    ],
    "Alpha-2-Macroglobulin": ["Alpha-2-Macroglobulin"],
    "Alpha-Fetoprotein (tumor marker)": [],
    "Amylase": [],
    "Amylase, pancreatic": [],
    "ACE": [],
    "Antithrombin III (ATIII)": ["Antithrombin-III"],
    "Apolipoprotein A1": [
        "Apolipoprotein A-I;Proapolipoprotein A-I;Truncated apolipoprotein A-I"
    ],
    "Apolipoprotein B": ["Apolipoprotein B-100;Apolipoprotein B-48"],
    "Aspartate aminotransferase (AST or SGOT)": [],
    "Beta-2 Microglobulin": ["Beta-2-microglobulin;Beta-2-microglobulin form pI 5.3"],
    "Beta-Thromboglobulin": [
        "Platelet basic protein;Connective tissue-activating peptide III;TC-2;Connective tissue-activating peptide III(1-81);Beta-thromboglobulin;Neutrophil-activating peptide 2(74);Neutrophil-activating peptide 2(73);Neutrophil-activating peptide 2;TC-1;Neutrophil-activating peptide 2(1-66);Neutrophil-activating peptide 2(1-63)"
    ],
    "Biotinidase": [],
    "Cancer antigen 125 (CA 125)": [],
    "Cancer antigen 15-3 (CA 15-3)": [],
    "Cancer antigen, human epididymis protein 4 (HE4)": [],
    "Carcinoembryonic antigen (CEA)": [],
    "Ceruloplasmin": ["Ceruloplasmin"],
    "Cholinesterase": [],
    "Complement C1": [
        "Complement C3;Complement C3 beta chain;C3-beta-c;Complement C3 alpha chain;C3a anaphylatoxin;Acylation stimulating protein;Complement C3b alpha chain;Complement C3c alpha chain fragment 1;Complement C3dg fragment;Complement C3g fragment;Complement C3d fragment;Complement C3f fragment;Complement C3c alpha chain fragment 2"
    ],
    "Complement C1 Inhibitor": [],
    "Complement C1Q": [
        "Complement C1q subcomponent subunit B",
        "Complement C1q subcomponent subunit A",
        "Complement C1q subcomponent subunit C",
    ],
    "Complement C3": [
        "Complement C3;Complement C3 beta chain;C3-beta-c;Complement C3 alpha chain;C3a anaphylatoxin;Acylation stimulating protein;Complement C3b alpha chain;Complement C3c alpha chain fragment 1;Complement C3dg fragment;Complement C3g fragment;Complement C3d fragment;Complement C3f fragment;Complement C3c alpha chain fragment 2"
    ],
    "Complement C4": [
        "Complement C4-B;Complement C4 beta chain;Complement C4-B alpha chain;C4a anaphylatoxin;C4b-B;C4d-B;Complement C4 gamma chain",
        "C4b-binding protein beta chain",
    ],
    "Complement C5": [
        "Complement C5;Complement C5 beta chain;Complement C5 alpha chain;C5a anaphylatoxin;Complement C5 alpha chain"
    ],
    "CRP": [],
    "Creatine kinase-BB (CKBB)": [],
    "Creatine kinase-MM (CKMM)": [],
    "Cystatin C": [],
    "Erythropoietin": [],
    "Factor IX antigen": [],
    "Factor X": [
        "Coagulation factor X;Factor X light chain;Factor X heavy chain;Activated factor Xa heavy chain"
    ],
    "Factor XIII": ["Coagulation factor XIII B chain"],
    "Ferritin": [],
    "Fibrinogen": [
        "Fibrinogen alpha chain;Fibrinopeptide A;Fibrinogen alpha chain",
        "Fibrinogen beta chain;Fibrinopeptide B;Fibrinogen beta chain",
        "Fibrinogen gamma chain",
    ],
    "Fibronectin": ["Fibronectin;Anastellin;Ugl-Y1;Ugl-Y2;Ugl-Y3"],
    "FSH": [],
    "GGT": [],
    "Haptoglobin": [
        "Haptoglobin;Haptoglobin alpha chain;Haptoglobin beta chain",
        "Haptoglobin-related protein",
    ],
    "Human chorionic gonadotropin (hCG), beta, serum, quantitative": [],
    "Hemopexin": ["Hemopexin"],
    "her-2/neu protein": [],
    "Human growth hormone (HGH)": [],
    "Human placental lactogen (HPL)": [],
    "IgA": ["Ig alpha", "Ig alpha-2 chain C region", "Ig alpha-1 chain C region"],
    "IgD": ["Ig delta"],
    "IgE": ["Ig epsilon"],
    "IgM": ["Ig mu", "Ig mu chain C region"],
    "Inhibin-A": [],
    "Insulin": ["Insulin"],
    "Insulinlike growth factor-I (IGF-I)": [],
    "Insulinlike growth factor-II (IGF-II)": [],
    "IGFBP-1": [],
    "IGFBP-3": [],
    "Interleukin-2 receptor (IL-2R)": [],
    "Isocitric dehydrogenase": [],
    "Kappa Light chains": [],
    "Lactate dehydrogenase heart fraction (LDH-1)": [],
    "Lactate dehydrogenase liver fraction (LLDH)": [],
    "Lactoferrin": [],
    "Lambda Light chains": [],
    "Lipase": [],
    "Lp(a)": [],
    "Lipoprotein-associated phospholipase A2 (LP-PLA2)": [],
    "LH": [],
    "Lysozyme": [],
    "Myeloperoxidase (MPO)": [],
    "Myoglobin": [],
    "Osteocalcin": [],
    "Parathyroid hormone, intact": [],
    "Phosphohexose isomerase": [],
    "Plasminogen": [
        "Plasminogen;Plasmin heavy chain A;Activation peptide;Angiostatin;Plasmin heavy chain A, short form;Plasmin light chain B"
    ],
    "Plasminogen activator inhibitor (PAI)": [],
    "Prealbumin": [],
    "NTproBNP": [],
    "Procalcitonin (PCT)": [],
    "Prolactin": [],
    "Properdin factor B": [],
    "Prostatic acid phosphatase (PAP)": [],
    "Prostatic specific antigen (PSA)": [],
    # Izzy starts at Protein C
    "Protein C": [],
    "Protein S": [],
    "Pseudocholinesterase": [],
    "Pyruvate kinase": [],
    "Renin": [],
    "Retinol binding protein (RBP)": [],
    "Sex hormone–binding globulin": [],
    "Soluble mesothelin-related peptide": [],
    "Sorbital dehydrogenase (SDH)": [],
    "Thyroglobulin": [],
    "TSH": [],
    "Thyroxine binding globulin (TBG)": [],
    "Tissue plasminogen activator (T-PA)": [],
    "Transferrin": [],
    "Transferrin receptor (TFR)": [],
    "Troponin T (TnT)": [],
    "TnI (cardiac)": [],
    "Trypsin": [],
    "Urokinase": [],
    "Von Willebrand factor": [],
}
