SEED_CATEGORIES = {
    "KIT INICIANTE": [
        "Alongamento em Acrílico",
        "Alongamento em Fibra",
        "Alongamento em Molde F1",
        "Alongamento em Soft Gel",
        "Esmaltação em Gel",
        "Manicure Tradicional",
    ],
    "ALONGAMENTO DE UNHAS": [
        "Algodão Prensado",
        "Brocas",
        "Cola",
        "Fibra",
        "Finalizadores",
        "Gel",
        "Hidratante de cutículas",
        "Lixas",
        "Molde F1/ Papel",
        "Monômer",
        "Pincel",
        "Pó acrílico",
        "Preparadores",
        "Presilhas",
        "Soft Gel",
        "Tips/ Molde",
    ],
    "ELETRÔNICOS": [
        "Cabideiro",
        "Estufa",
        "Lixadeira/ Motor/ Sugador",
        "Luminária",
    ],
    "ESMALTES": [
        "Base Coat",
        "Esmalte em Gel",
        "Esmalte Tradicional",
        "Top Coat",
    ],
    "CUTICULAGEM": [
        "Acessórios",
        "Alicates",
        "Espátula/ Bisturi",
        "Hidratante de cuticulas",
        "Hidratante para mãos",
        "Lixas",
        "Removedores",
    ],
    "MANICURE TRADICIONAL": [
        "Acetona/ Removedor Esmalte",
        "Algodão",
        "Alicate de unha",
        "Amaciante para cutículas",
        "Cortador de Unhas",
        "Lixas",
        "Palito",
    ],
    "ACESSÓRIOS PARA MANICURE": [
        "Alicates/ Tesoura Cutícula",
        "Cortador de Unhas",
    ],
    "DEPILAÇÃO": [
        "Aquecedor de Cera",
        "Cera Depilatória",
        "Espátula para Depilação",
        "Papel para Depilação",
        "Pós Depilação",
    ],
    "SPA DOS PÉS": [
        "Bacia",
        "Descartáveis",
        "Emolientes e Hidratantes",
        "Lixas",
        "Sapatilhas",
        "Spa Nuvem",
    ],
    "SOBRANCELHA": [
        "Henna",
        "Linha",
        "Pinça",
    ],
    "VANESSA SABATER": [],
}


def seed_categories(db, Category):
    existing = db.query(Category).count()
    if existing > 0:
        return

    for parent_name, subcats in SEED_CATEGORIES.items():
        parent = Category(name=parent_name, parent_id=None)
        db.add(parent)
        db.flush()
        for sub_name in subcats:
            child = Category(name=sub_name, parent_id=parent.id)
            db.add(child)
    db.commit()
    print(f"SEED: {len(SEED_CATEGORIES)} categorias e subcategorias inseridas")
