from typing import List

import discord


def is_target_reaction(payload: discord.RawReactionActionEvent,
                       target_message_id: int,
                       target_emoji_name: List[str],
                       target_emoji_id:  List[int] = None,
                       ) -> bool:
    if target_emoji_id:
        match = payload.message_id == target_message_id and payload.emoji.id in target_emoji_id
        print(f"[ReactionRole] Checking emoji='{payload.emoji.id}' → Match: {match}")
    else:
        match = payload.message_id == target_message_id and payload.emoji.name in target_emoji_name
        print(f"[ReactionRole] Checking emoji='{payload.emoji.name}' → Match: {match}")


    return match