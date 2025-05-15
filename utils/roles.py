import os
import discord

PROMOTION_PATHS = [
    [
        os.getenv("PRE_TRAINER_ROLE", "PreTrainer"),
        os.getenv("TRAINER_ROLE", "Trainer"),
        os.getenv("RYUZEN_STAFF_ROLE", "RyuZen Team")
    ],
    [
        os.getenv("PRE_COMPETITOR_ROLE", "PreCompetitor"),
        os.getenv("COMPETITOR_ROLE", "Competitor"),
        os.getenv("RYUZEN_STAFF_ROLE", "RyuZen Team")
    ]
]

DEMOTION_PATHS = [list(reversed(path)) for path in PROMOTION_PATHS]


async def promote_member(guild: discord.Guild, member: discord.Member) -> list[discord.Role]:
    """
    Promuove il membro su ogni ramo applicabile, una sola volta per ramo.
    """
    roles_by_name = {r.name: r for r in guild.roles}
    member_roles = {r.name for r in member.roles}
    added_roles = []

    for path in PROMOTION_PATHS:
        for i in range(len(path) - 1):
            current, next_ = path[i], path[i + 1]
            if current in member_roles:
                current_role = roles_by_name.get(current)
                next_role = roles_by_name.get(next_)

                if current_role and next_role:
                    await member.add_roles(next_role, reason="Promoted via command or reaction")
                    await member.remove_roles(current_role, reason="Auto-remove previous role")
                    added_roles.append(next_role)
                break  # ⛔️ Evita promozioni multiple nello stesso ramo

    return added_roles


async def demote_member(guild: discord.Guild, member: discord.Member) -> list[discord.Role]:
    """
    Retrocede il membro su ogni ramo applicabile, una sola volta per ramo.
    """
    roles_by_name = {r.name: r for r in guild.roles}
    member_roles = {r.name for r in member.roles}
    added_roles = []

    for path in DEMOTION_PATHS:
        for i in range(len(path) - 1):
            current, next_ = path[i], path[i + 1]
            if current in member_roles:
                current_role = roles_by_name.get(current)
                next_role = roles_by_name.get(next_)

                if current_role and next_role:
                    await member.add_roles(next_role, reason="Demoted via command or reaction")
                    await member.remove_roles(current_role, reason="Removed higher role")
                    added_roles.append(next_role)
                break  # ⛔️ Evita doppie demozioni nello stesso ramo

    return added_roles
