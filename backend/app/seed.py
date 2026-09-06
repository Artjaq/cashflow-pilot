import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category

logger = logging.getLogger(__name__)

EXPENSE_CATEGORIES = [
    "Logement",
    "Alimentation",
    "Transport",
    "Véhicule",
    "Assurances",
    "Télécom/Internet",
    "Loisirs",
    "Santé",
    "Formation",
    "Abonnements",
    "Amendes/Poursuites",
    "Autres",
]

INCOME_CATEGORIES = [
    "Salaire",
    "Freelance",
    "Remboursement",
    "Vente",
    "Autres revenus",
]


async def seed_categories(db: AsyncSession) -> None:
    """Insère les catégories de démarrage si elles n'existent pas déjà (idempotent)."""
    result = await db.execute(select(Category.name))
    existing_names = set(result.scalars().all())

    to_create: list[Category] = []
    for name in EXPENSE_CATEGORIES:
        if name not in existing_names:
            to_create.append(Category(name=name, kind="expense"))
    for name in INCOME_CATEGORIES:
        if name not in existing_names:
            to_create.append(Category(name=name, kind="income"))

    if not to_create:
        logger.info("Seed catégories : rien à faire, déjà en place.")
        return

    db.add_all(to_create)
    await db.commit()
    logger.info("Seed catégories : %d catégorie(s) créée(s).", len(to_create))
